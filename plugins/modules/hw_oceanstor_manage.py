#!/usr/bin/env python
# !coding:utf-8

# (c) 2020, huawei, Inc

from ansible.module_utils.basic import AnsibleModule
from oceanstor.oceanstor_add_storage import OceanStorStorage


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

        client = OceanStorStorage(base_url, username, password, token)

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

    def create_manage_cluster(self):
        """ 创建控制集群
        """
        param = self.module.params["param"]

        if "serverList" not in param:
            self.module.fail_json(msg="No Servers for Manage Cluster",
                                  changed=False)

        servers = param["serverList"]

        if len(servers) not in [3, 5, 7, 9]:
            self.module.fail_json(
                msg="The number of servers for manage cluster is incorrect",
                changed=False)

        name = "StorageControlCluster"
        if "name" in param:
            name = param["name"]

        response = self.client.create_manage_cluster(name, servers)

        if response['result'] == '1':
            self.module.exit_json(
                msg="Create manage cluster failed "
                "{0}".format(response['detail']['description']),
                changed=False)
        elif response['result'] == '2':
            self.module.fail_json(
                msg="Create manage cluster failed "
                "{0}".format(response['description']), changed=False)

        self.module.exit_json(msg="Create manage cluster success",
                              changed=True)

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

        response = self.client.create_storage_pool(pool_para, server_list)

        result = response['result']

        if result == 0:
            self.module.exit_json(msg="Create Storage pool success",
                                  taskId=response['taskId'],
                                  changed=True)

        self.module.fail_json(msg=response, para=pool_para,
                              server=server_list, changed=False)

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

            self.module.exit_json(changed=False, task=task)

        self.module.exit_json(changed=False, task={"taskStatus": "waiting"},
                              response=response)

    def create_vbs_client(self):
        """ 创建VBS Client
        """
        param = self.module.params["param"]
        response = self.client.get_cluster_info()
        servers = response["data"]
        server_list = []
        nodeType = 0

        if "nodeType" in param:
            nodeType = param["nodeType"]

        for server in servers:
            if 'vbs' not in server['usage']:
                server_list.append({"nodeMgrIp": server['management_ip'],
                                    "nodeType": nodeType})

        # network_type = self.module.params['network_type']
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


def main():
    manage = HuaweiOceanStorManage()
    manage.fun()


if __name__ == '__main__':
    main()
