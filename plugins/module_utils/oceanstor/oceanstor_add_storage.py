#!/usr/bin/python
# -*- coding: UTF-8 -*-、

# Copyright (c) 2020 Huawei Inc.
#
""" oceanstor_add_storage.py """

import logging

from ansible_collections.oceanstor_series.oceanstor.plugins.module_utils.oceanstor.oceanstor_base import OceanStorBase
from ansible_collections.oceanstor_series.oceanstor.plugins.module_utils.oceanstor.exception import OceanStorParamError

LOG = logging.getLogger(__name__)


class OceanStorStorage(OceanStorBase):
    """ Add OceanStor storage """

    def __init__(self, auth_url, username, password, token=None, verify=False,
                 retries=3, timeout=120, application_type=None):
        """__init__."""
        super(OceanStorStorage, self).__init__(auth_url,
                                               username,
                                               password,
                                               token,
                                               verify=verify,
                                               retries=retries,
                                               timeout=timeout)

    def login(self, username, password):
        """ 登录鉴权
        """
        url = "/api/v2/aa/sessions"
        session = self._establish_session(url, username, password)
        return session

    def get_token(self):
        """ 获取token信息
        """
        if "X-Auth-Token" in self.session.headers and \
                self.session.headers["X-Auth-Token"] is not None:
            return self.session.headers["X-Auth-Token"]

        return None

    def logout(self):
        """ 退出登录
        """
        url = "/api/v2/aa/sessions"
        params = {
            "is_timeout": "false"
        }

        return self.request(url, "DELETE", params=params)

    def check_connection(self, server):
        """ 查询节点的连接状态
        input: server, 请求参数体,为dict
            - management_internal_ip:  str - required
            - cabinet: str -
            - slot_number: int -
            - subrack: int -
            - role: - list -required ["management", "storage"]
            - serial_number: int -
            - name: str -
            - model: str -
            - authentication_mode: str - required "password"
            - user_name: str - required "root"
            - password: str - required "****"
            - root_password: str - required "****"
        OceanStor return:
        {
            data: null,
            result: {
                code: '0',
                description: null,
                suggestion: null
            }
        }
        """
        target_url = "/api/v2/deploy_manager/connection"

        if "management_internal_ip" not in server or \
                server['management_internal_ip'] == "":
            LOG.error("management ip not configured!")
            raise OceanStorParamError("management ip not exists")

        response = self.request(target_url, method="POST",
                                request_object=server)

        return response

    def get_server_info(self):
        """ 查询节点信息
        """
        url = "/api/v2/deploy_manager/servers"

        return self.request(url, "GET")

    def restore_factory(self):
        """ 恢复出厂设置
        """
        url = "/api/v2/deploy_manager/nodes.restore_factory_settings()"

        response = self.request(url, "POST")

        return response

    def add_storage_servers_with_fsm(self, servers):
        """ 增加管理存储节点
        """
        url = "/api/v2/deploy_manager/servers"

        return self.request(url, "PUT", request_object=servers)

    def add_storage_servers(self, servers):
        """ 增加节点信息
        """
        url = "/api/v2/deploy_manager/servers_async"

        return self.request(url, "POST", request_object=servers)

    def deploy_service(self, node_list, service_type="agent"):
        """ 批量部署存储服务
        """
        url = "/api/v2/deploy_manager/deploy_service"
        body = {
            "service_type": service_type,
            "node_ip_set": node_list
        }
        return self.request(url, "POST", request_object=body)

    def deploy_service_task(self, service_type="agent"):
        """ 查询节点的部署状态
        """
        url = "/api/v2/deploy_manager/deploy_service_task"

        params = {
            "service_type": service_type
        }

        return self.request(url, "GET", params=params)

    def get_network_platform(self, network_type):
        """ 查询指定网络平面信息
        network_type 可选值:
            management_external_float：管理外部网络浮动IP；
            management_internal_float：管理内部网络浮动IP；
            management_external：管理外部网络IP；
            management_internal：管理内部网络IP；
            storage_frontend：存储前端网络IP；
            storage_backend：存储后端网络IP；
            replication：复制网络；
            quorum：仲裁网络；
            iscsi：iSCSI网络。
        """
        url = "/api/v2/network_service/network_platform"
        params = {
            "network_type": network_type
        }

        return self.request(url, "GET", params=params)

    def config_network_type(self, network_type, protocol, network):
        """ 配置指定网络平面信息
        network_type 可选值:
            management_external_float：管理外部网络浮动IP；
            management_internal_float：管理内部网络浮动IP；
            management_external：管理外部网络IP；
            management_internal：管理内部网络IP；
            storage_frontend：存储前端网络IP；
            storage_backend：存储后端网络IP；
            replication：复制网络；
            quorum：仲裁网络；
            iscsi：iSCSI网络。
        """
        url = "/api/v2/network_service/network_platform"
        body = {
            "network_type": network_type,
            "transfer_protocol": protocol
        }

        body.update(network)

        return self.request(url, "PUT", request_object=body)

    def validity_network(self, network_type, servers):
        """ 校验指定网络平面信息
        network_type 可选值:
            management_external_float：管理外部网络浮动IP；
            management_internal_float：管理内部网络浮动IP；
            management_external：管理外部网络IP；
            management_internal：管理内部网络IP；
            storage_frontend：存储前端网络IP；
            storage_backend：存储后端网络IP；
            replication：复制网络；
            quorum：仲裁网络；
            iscsi：iSCSI网络。
        servers: 管理ip列表
            [
                {"management_internal_ip": "1.1.1.1"},
                {"management_internal_ip": "1.1.1.2"}
            ]
        """
        url = "/api/v2/network_service/validity"

        body = {
            "network_type": network_type,
            "servers": servers
        }

        return self.request(url, "POST", request_object=body)

    def scan_server_media(self, servers):
        """ 指定节点扫描硬盘
        servers：节点管理IP列表
        """
        url = "/dsware/service/vsan/scanServerMedia"

        body = {
            "nodeIpList": servers
        }

        response = self.request(url, "POST", request_object=body)

        return response

    def create_manage_cluster(self, name, servers):
        """ 创建控制集群
        name: 集群名称(汉字，字母，数字和下划线，最长64字符)
        servers: 节点列表, 长度为3,5,7,9
            - nodeMgrIp: required 节点管理IP
            - zkDiskEsn: ZK盘的ESN。zkType是ssd_card时必须下发。
            - zkType: required ZK类型： 独立硬盘（支持SSD、HDD）、系统盘。
                                        sas: SAS HDD;
                                        sata: SATA HDD;
                                        ssd_disk: SAS SSD;
                                        ssd_card: SSD Card/NVMe SSD;
                                        sys_disk: 系统盘。
            - zkDiskSlot: ZK磁盘槽位号
                          zkType类型为 sas/sata/ssd_disk/ssd_card时必选。
            - zkPartition: 分区挂载路径
                          zkType = partition时必选。
            [
                {
                    "nodeMgrIp": "",
                    "zkDiskEsn": "",
                    "zkType": "",
                    "zkDiskSlot": ""，
                    "zkPartition": ""
                }, {...}, {...}
            ]
        """
        url = "/dsware/service/cluster/createManageCluster"

        body = {
            "clusterName": name,
            "serverList": servers
        }

        response = self.request(url, "POST", request_object=body)
        return response

    def modify_user_password(self, username, password, old_password, role_id=None):
        """ 修改用户密码
        """
        url = "/deviceManager/rest/xxx/user/{0}".format(username)

        body = {
            "ID": username,
            "PASSWORD": password,
            "OLDPASSWORD": old_password
        }

        if role_id:
            body.update({"ROLEID": role_id})

        return self.request(url, "PUT", request_object=body)

    def create_storage_pool(self, pool_para, server_list):
        """ 创建存储池
        """
        url = "/dsware/service/cluster/storagepool/createStoragePool"

        body = {
            "poolPara": pool_para,
            "serverList": server_list
        }

        return self.request(url, "POST", request_object=body)

    def new_create_storage_pool(self, servicetype, server_list):
        """ 四合一推荐存储池创建方案 （8015无此接口）
        """
        url = "/v2/data_service/storagepool/recommendStoragePool"

        body = {
            "serviceType": servicetype,
            "recommendSource": "DeviceManager",
            "serverIpList": server_list
        }

        return self.request(url, "POST", request_object=body)

    def query_all_disk(self):
        """ 查询存储介质信息
        """
        url = "/dsware/service/resource/queryAllDisk"

        return self.request(url, "GET")

    def get_storage_pool(self, pool_id=None):
        """ 查询存储池信息
            pool_id: 不下发时表示查询系统集群下所有的存储池。
                     如果查询的存储池不存在，则返回值为空。
        """
        url = "/dsware/service/resource/queryStoragePool"

        params = None
        if pool_id:
            params = {
                "poolId": pool_id
            }

        return self.request(url, "GET", params=params)

    def get_task_info(self, locale="en_US"):
        """ 查询当前系统的所有任务
        """
        url = "/dsware/service/task/queryTaskInfo"

        params = {
            locale: locale
        }

        return self.request(url, "GET", params=params)

    def query_storage_node_info(self, pool_id=None):
        """ 查询存储节点信息
            pool_id: 可选，如果不携带该属性表示查询系统集群下所有
                     的存储池，如果携带该属性表示查询具体的存储池的信息。
        """
        url = "/dsware/service/cluster/storagepool/queryStorageNodeInfo"

        params = None
        if pool_id:
            params = {
                "poolId": pool_id
            }

        return self.request(url, "GET", params=params)

    def query_tasklog_info(self, task_id):
        """ 查询任务日志信息
        """
        url = "/dsware/service/task/queryTaskLogInfo"

        params = {
            "taskId": task_id
        }

        return self.request(url, "GET", params=params)

    def get_cluster_info(self):
        """ 批量查询集群节点信息
        """
        url = "/api/v2/cluster/servers"

        return self.request(url, "GET")

    def create_vbs_client(self, server_list):
        """ 创建VBS Client
        """
        url = "/dsware/service/cluster/dswareclient/createDSwareClient"

        body = {
            "servers": server_list
        }

        return self.request(url, "POST", request_object=body)

    def uploading_license(self, license_file_name):
        """ 加载License文件
        """
        url = "/dsware/service/license/loadLicenseFile"

        body = {
            "license": license_file_name,
            "tinyFormDatas": '',
        }

        return self.request(url, "POST", request_object=body)


def main():
    pass


if __name__ == "__main__":
    main()
