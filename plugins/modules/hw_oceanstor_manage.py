#!/usr/bin/env python
# !coding:utf-8

# (c) 2020, huawei, Inc

import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.oceanstor_series.oceanstor.plugins.module_utils.oceanstor.oceanstor_add_storage \
    import OceanStorStorage


class HuaweiOceanStorManage(object):
    """ Huawei OceanStor Manage Module
    """

    def __init__(self):
        """ __init__
        """
        # Ansible的入口参数
        ansible_options = dict(
            api_url=dict(type="str", required=True),
            api_port=dict(type="int", required=True),
            username=dict(type="str", required=True),
            password=dict(type="str", required=True, no_log=True),
            token=dict(type="str", required=False, no_log=True),
            validate_certs=dict(type="bool", default=False, required=False),
            function=dict(type="str", required=True),
            param=dict(type="dict", required=False)
        )

        required_together = [["api_url", "api_port", "username", "password"]]

        self.module = AnsibleModule(
            argument_spec=ansible_options, required_together=required_together
        )

        self.client = self.create_oceanstor_api_client()

    def create_oceanstor_api_client(self):
        """ 创建调用OceanStor API的REST client
        """
        base_url = self._format_base_url()

        username = self.module.params["username"]
        password = self.module.params["password"]
        token = self.module.params["token"]

        client = OceanStorStorage(base_url, username, password, token, timeout=300)

        return client

    def _format_base_url(self):
        """ 格式化请求的基础路径 https://ip:port
        """
        url = self.module.params["api_url"]
        port = self.module.params["api_port"]
        return "https://{0}:{1}".format(url, port)

    def fun(self):
        """ 根据ansible的function参数调用对应的函数
        """
        function = self.module.params["function"]

        try:
            func = getattr(self, function)
            func()
        except AttributeError:
            self.module.fail_json(
                msg="{0} not supported".format(function),
                changed=False)

    def modify_user_password(self):
        """ 修改用户密码
        """
        username = self.module.params['username']
        old_password = self.module.params['password']
        password = self.module.params['param']['new_password']
        response = self.client.modify_user_password(
            username, password, old_password)

        res = response['result']

        if res["code"] != 0:
            self.module.fail_json(
                msg="Change password faild {0}".format(res['description']),
                changed=False)

        self.module.exit_json(changed=True, msg="Change password successful")

    def get_token(self):
        """ 获取token
        """
        token = self.client.get_token()

        if not token:
            self.module.fail_json(msg="Get token failed", changed=False)

        self.module.exit_json(changed=True, token=token)

    def restore_factory(self):
        """ 恢复出厂设置
        """
        response = self.client.restore_factory()

        result = response["result"]

        if result['code'] == '0':
            self.module.exit_json(changed=False,
                                  msg="restore factory successful")
        else:
            self.module.fail_json(changed=True, msg=result['description'])

    def uploading_license(self):
        """加载License文件
        """
        param = self.module.params["param"]
        license_file_name = param['license_file_name']
        if not license_file_name:
            self.module.fail_json(msg="Please input license file name like: -e filename=<licensefilename>",
                                  changed=False, status='fail')

        response = self.client.uploading_license(self, license_file_name)

        if str(response['result']['code']) == '0':
            self.module.exit_json(msg="Uploading License file: {0} success.".format(license_file_name),
                                  changed=True, status='success')
        elif str(response['result']['code']) == '2':
            self.module.fail_json(msg="Uploading License file: {0} fail.{1}".format(license_file_name,
                                                                                    response['result']['description']),
                                  changed=False, status='fail')
        else:
            self.module.fail_json(msg="Uploading License file: {0} fail.".format(license_file_name),
                                  changed=False, status='fail')

    def create_manage_cluster(self):
        """ 创建控制集群
        """
        param = self.module.params["param"]

        if "serverList" not in param:
            self.module.fail_json(msg="No Servers for Manage Cluster",
                                  changed=False)

        servers = []
        for server_param in param["serverList"]:
            server = {}
            server["nodeMgrIp"] = server_param["address"]
            server["zkType"] = server_param["zkType"]
            if server["zkType"] in ["sas_disk", "sata_disk", "ssd_disk", "ssd_card"]:
                server["zkDiskSlot"] = int(server_param["zkDiskSlot"])
            if server["zkType"] in ["ssd_card"]:
                server["zkDiskEsn"] = server_param["zkDiskEsn"]
            server["zkPartition"] = server_param["zkPartition"]

            servers.append(server)

        if len(servers) not in [3, 5, 7, 9]:
            self.module.fail_json(msg="The number of servers for manage cluster is incorrect", changed=False)

        name = "StorageControlCluster"
        if "name" in param:
            name = param["name"]

        self.module.warn("{0} {1}".format(name, servers))
        response = self.client.create_manage_cluster(name, servers)

        if str(response['result']) == '0':
            self.module.exit_json(msg="Create manage cluster success",
                                  changed=True)
        elif str(response['result']) == '1':
            self.module.exit_json(
                msg="Create manage cluster failed "
                "{0}".format(response['detail']['description']),
                changed=False)
        elif str(response['result']) == '2':
            self.module.fail_json(
                msg="Create manage cluster failed {0} {1}".format(response['description'], response['result']),
                changed=False, data="{0} {1}".format(name, servers))

        self.module.fail_json(msg="Create manage cluster failed {0}".format(response['result']),
                              changed=False)

    def new_create_storage_pool(self):
        """ 四合一创建存储池
        """
        param = self.module.params["param"]

        serviceType = param['serviceType']

        server_list = []
        for server in param["serverList"]:
            server_list.append(server['address'])

        response = self.client.new_create_storage_pool(serviceType, server_list)

        if str(response['result']['code']) == '0':
            self.module.exit_json(msg="Create Storage pool success",
                                  taskId=response['taskId'],
                                  changed=True)
        else:
            self.module.fail_json(msg="Create Storage pool fail {0}".format(response['result']['description']),
                                  server=server_list, changed=False)

    @staticmethod
    def _get_server_disk(server, server_disks, default_media_role, media_type_list):
        """获取单个节点硬盘信息
        """
        disk_list = []
        for server_disk in server_disks:
            if server_disk["devRole"] == "no_use":
                disk_list.append(dict(mediaRole=default_media_role, mediaType=server_disk["devType"],
                                      phyDevEsn=server_disk["devEsn"], phySlotId=server_disk["devSlot"]))
                if server_disk["devType"] not in media_type_list:
                    media_type_list[server_disk["devType"]] = [server]
                elif server not in media_type_list[server_disk["devType"]]:
                    media_type_list[server_disk["devType"]].append(server)

        return disk_list, media_type_list

    def _get_list_disk(self, server_list):
        """获取未使用存储,组成创池数据
        """
        disks = self.get_all_disk()
        default_media_role = "main_storage"
        media_type_list = dict()
        server_param = list()
        for server in server_list:
            if server['address'] in disks and server.get('mediaList'):
                disk_param = dict(nodeMgrIp=server['address'])
                disk_list = list()
                for disk in server.get('mediaList'):
                    disk_list.append(dict(mediaRole=disk['mediaRole'], mediaType=disk['mediaType'],
                                          phyDevEsn=disk['phyDevEsn'], phySlotId=disk['phySlotId']))
                if len(disk_list) < 4:
                    self.module.fail_json(msg=("The number of disk is not enough.You need four unused disks at "
                                               "least on {0}.").format(server["address"]), changed=False)
                disk_param["mediaList"] = disk_list
                server_param.append(disk_param)
            elif server['address'] in disks:
                disk_param = dict(nodeMgrIp=server['address'])
                disk_list, media_type_list = self._get_server_disk(server['address'], disks[server['address']],
                                                                   default_media_role, media_type_list)
                if len(disk_list) < 4:
                    self.module.fail_json(msg=("The number of disk is not enough.You need four unused disks at "
                                               "least on {0}.").format(server["address"]), changed=False)
                disk_param["mediaList"] = disk_list
                server_param.append(disk_param)
            else:
                self.module.fail_json(msg="Query {0} disk failed.".format(server["address"]), changed=False)
        if len(media_type_list.keys()) > 1:
            self.module.fail_json(msg="Create pool Failed.All the type of server disk must be the same. "
                                      "{0}".format(media_type_list),
                                  changed=False)

        return server_param

    def create_storage_pool(self):
        """ 创建存储池
        """
        param = self.module.params["param"]
        pool_para = {}
        if "poolName" not in param:
            self.module.fail_json(msg="Pool name not assigned.",
                                  changed=False)
        pool_para["poolName"] = param['poolName']

        pool_para['serviceType'] = param['serviceType']
        pool_para['encryptType'] = param['encryptType']

        if "storageMediaType" not in param:
            self.module.fail_json(msg="Storage Media type not assigned.",
                                  changed=False)

        pool_para['storageMediaType'] = param["storageMediaType"]
        pool_para['cacheMediaType'] = param["cacheMediaType"]
        pool_para["securityLevel"] = param["securityLevel"]
        redundancyPolicy = param["redundancyPolicy"]

        if param["compressionAlgorithm"] in ["performance", "capacity"]:
            pool_para['compressionAlgorithm'] = param["compressionAlgorithm"]

        if redundancyPolicy == "replication":
            pool_para["redundancyPolicy"] = param["redundancyPolicy"]
            pool_para["replicaNum"] = param["replicaNum"]
        elif redundancyPolicy == "ec":
            pool_para["redundancyPolicy"] = param["redundancyPolicy"]
            pool_para['numDataUnits'] = param["numDataUnits"]
            pool_para['numParityUnits'] = param["numParityUnits"]
            pool_para['numFaultTolerance'] = param["numFaultTolerance"]
        else:
            self.module.fail_json(msg="Invalid para redundancy policy",
                                  changed=False)

        if "serverList" not in param:
            self.module.fail_json(msg="Servers for pool not assigned")

        server_list = param["serverList"]

        if len(server_list) < 3:
            self.module.fail_json(msg="At least three Servers.There are only {0}.".format(len(server_list)))
        server_param = self._get_list_disk(server_list)
        response = self.client.create_storage_pool(pool_para, server_param)

        if str(response['result']) == "0":
            self.module.exit_json(msg="Create Storage pool success",
                                  taskId=response['taskId'],
                                  changed=True)
        elif str(response['result']) == "2":
            self.module.fail_json(msg="Create Storage pool fail {0}".format(response["description"]),
                                  server=server_param, changed=False)
        self.module.fail_json(msg=response, param=pool_para, server=server_param, changed=False)

    def get_all_disk(self):
        """ 查询所有存储介质信息
        """
        response = self.client.query_all_disk()

        if response['result'] != 0:
            self.module.fail_json(msg="Query all disk failed.", changed=False)

        disks = response['disks']

        return disks

    def query_task_info(self):
        """ 查询任务的状态
        """
        response = self.client.get_task_info(locale="zh_CN")

        if response['result'] != 0:
            self.module.fail_json(changed=False,
                                  msg="Query system tasks failed",
                                  description=response['description'])

        taskId = self.module.params["param"]["taskId"]

        for task in response['taskInfo']:
            if str(taskId) != str(task['taskId']):
                continue
            if task.get("taskStatus"):
                self.module.exit_json(changed=False, task=task)
            else:
                self.module.exit_json(changed=False, task={"taskStatus": "waiting"}, response=response)

        self.module.exit_json(changed=False, task={"taskStatus": "waiting"},
                              response=response)

    def create_vbs_client(self):
        """ 创建VBS Client
        """
        param = self.module.params["param"]
        management_ip_list = []
        if "vbs_list" in param:
            vbs_list = param["vbs_list"]
            for vbs in vbs_list:
                management_ip_list.append(vbs['address'])
        response = self.client.get_cluster_info()
        servers = response["data"]
        server_list = []

        for server in servers:
            if server["management_ip"] in management_ip_list:
                management_ip_list.remove(server["management_ip"])
                if 'vbs' in server['usage']:
                    self.module.warn('{0} has created VBS: '.format(server["management_ip"]))
                else:
                    server_list.append({"nodeMgrIp": server['management_ip'], "nodeType": 0})
        if management_ip_list:
            self.module.warn('{0} have not add storage node.Please add storage node '
                             'first !'.format(' '.join(management_ip_list)))
        if len(server_list) == 0:
            self.module.exit_json(msg="All node haved add VBS client",
                                  server_list=server_list,
                                  status='success',
                                  changed=True)

        response = self.client.create_vbs_client(server_list)

        if response['result'] == 0:
            self.module.exit_json(msg="Create VBS client success",
                                  server_list=server_list,
                                  status='success',
                                  changed=True)
        elif response['result'] == 1:
            fail_list = []
            for server in response['detail']:
                fail_list.append("{0}:{1}".format(server['ip'], server['description']))
            self.module.fail_json(msg="Create VBS client fail "
                                      "{0}".format(' '.join(fail_list)),
                                  server_list=server_list,
                                  status='failure',
                                  changed=False)
        elif response['result'] == 2:
            self.module.fail_json(msg="Create VBS client fail "
                                      "{0}".format(response['description']),
                                  status='failure',
                                  changed=False)

        self.module.fail_json(msg=response,
                              status='failure',
                              server_list=server_list,
                              changed=False)

    def upload_license(self):
        """ Upload a license file.
        """
        param = self.module.params["param"]
        license_file_path = param['license_file_path']
        if license_file_path and os.access(license_file_path, os.F_OK) and os.access(license_file_path, os.R_OK):
            self.client.upload_license(license_file_path)
            self.module.exit_json(msg="Import license file Success.", changed=True, status='success')
        else:
            self.module.fail_json(msg="Import license file Fail.Please add 'hw_license_file_path' "
                                      "and make sure it can be read.",
                                  changed=True, status='fail')

    def activate_license(self):
        """Activating a License File
        """
        response = self.client.activate_license()
        if str(response["result"]["code"]) == "0" and str(response["data"]["LicenseActiveResult"]) == "0":
            self.module.exit_json(msg="Activate license file Success.", changed=True, status='success')
        else:
            self.module.fail_json(msg="Activate license file fail.{0}".format(response['result']['description']),
                                  status='fail', changed=False)

    def query_active_license(self):
        """Query active licenses in batches
        """
        response = self.client.query_active_license()
        if str(response["result"]["code"]) == "0":
            if str(response["data"]["FileExist"]) == "0":
                self.module.exit_json(msg="License file exists.", changed=True, status='success')
            else:
                self.module.fail_json(msg="License file not exists.You should add the License file first.Your License "
                                          "Serial No is: {0}".format(response["data"]["LicenseSerialNo"]),
                                      changed=False, status='fail')
        else:
            self.module.fail_json(msg="Query active licenses in batches has an error."
                                      "{0}".format(response['result']['description']),
                                  status='fail', changed=False)


def main():
    manage = HuaweiOceanStorManage()
    manage.fun()


if __name__ == '__main__':
    main()
