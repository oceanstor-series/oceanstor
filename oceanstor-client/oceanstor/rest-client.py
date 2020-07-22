
# -*- coding: utf-8 -*-

from oceanstor_base import OceanStorBase


class StorageArray(object):
    def __init__(self, address):
        self.rest_api = OceanStorBase(address)
        self._esn = "xxx"

    def login(self, username, password):
        path = "aa/sessions"
        body = {"username": username, "password": password, "scope": 0}
        http_code, resp = self.rest_api.request("POST", path, body)
        if http_code == 200 and resp.get("result").get("code") == 0:
            token = resp.get("data").get("x_auth_token")
            self._esn = resp.get("data").get("system_esn")
            self.rest_api.set_token(token)
        if resp.get("result").get("code") != 0:
            raise Exception("Failed to login array")
        return resp

    def logout(self):
        path = 'aa/sessions?is_timeout=false'
        http_code, resp = self.rest_api.request("DELETE", path)
        return resp

    def set_password(self, username, old_password, new_password):
        path = '/deviceManager/rest/xxx/user/%s'.format(username)
        body = {"ID": username, "PASSWORD": new_password, "OLDPASSWORD": old_password}
        http_code, resp = self.rest_api.request("PUT", path, body)
        self.get_result_data(resp)
        return resp

    def validate_nodes(self, node_list):
        path = "deploy_manager/nodes.check_validity()"
        body = node_list
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def add_nodes(self, node_list):
        path = "deploy_manager/servers"
        body = node_list
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def deploy_service(self, node_list, service_type):
        path = "deploy_manager/deploy_service"
        body = {'node_ip_set': node_list, 'service_type': service_type}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def get_deploy_task(self, service_type):
        path = "deploy_manager/deploy_service_task?service_type={0}".format(service_type)
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def get_network_platform(self, net_type):
        path = "network_service/network_platform?network_type={0}".format(net_type)
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def set_network_platform(self, network_type, ip_list, scenario, protocol="TCP", **kwargs):
        path = "network_service/network_platform"
        body = {'network_type': network_type,
                'ip_list': ip_list,
                'transfer_protocol': protocol,
                'scenario': scenario}
        body.update(kwargs)
        http_code, resp = self.rest_api.request("PUT", path, body)
        self.get_result_data(resp)
        return resp

    def validate_network(self, network_type, node_list):
        path = "network_service/validity"
        body = {'network_type': network_type,
                'servers': node_list}
        http_code, resp = self.rest_api.request("PUT", path, body)
        self.get_result_data(resp)
        return resp

    def retry_deploy_service(self, node_list, service_type):
        path = "deploy_manager/deploy_service/retry"
        body = {'node_ip_set': node_list, 'service_type': service_type}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def get_cluster_nodes(self):
        path = "cluster/servers"
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def add_cluster_nodes(self, node_list):
        path = "cluster/cluster_node"
        body = {"in_cluster": node_list}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def scan_disk(self, node_list):
        path = "/dsware/service/vsan/scanServerMedia"
        body = {"nodeIpList": node_list}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def create_manage_cluster(self, cluster_name, node_list):
        path = "/dsware/service/cluster/createManageCluster"
        body = {"clusterName": cluster_name, "serverList": node_list}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def get_manage_cluster(self):
        path = "/dsware/service/cluster/queryManageCluster"
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def create_storage_pool(self, pool_info):
        path = "/dsware/service/cluster/storagepool/createStoragePool"
        body = pool_info
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def get_storage_pool(self, pool_id=None):
        if pool_id:
            path = "/dsware/service/resource/queryStoragePool?poolId={0}".format(pool_id)
        else:
            path = "/dsware/service/resource/queryStoragePool"
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def get_task_info(self):
        path = "/dsware/service/task/queryTaskInfo"
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def get_disks(self):
        path = "/dsware/service/resource/queryAllDisk"
        http_code, resp = self.rest_api.request("GET", path)
        self.get_result_data(resp)
        return resp

    def create_vbs_client(self, node_list):
        path = "/dsware/service/cluster/dswareclient/createDSwareClient"
        body = {"servers": node_list}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def get_net_nodes(self, manage_ip):
        path = "network_service/servers"
        body = {"servers": [{"management_internal_ip": manage_ip}]}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def set_iscsi_switch(self, manage_ip, switch):
        path = "/dsware/service/configIscsiSwitch"
        body = {"ips": [manage_ip], "switch": switch}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    def add_iscsi_portal(self, manage_ip, storage_ip, port="3266"):
        path = "/dsware/service/cluster/dswareclient/addIscsiPortal"
        body = {"iscsiIp": storage_ip, "iscsiPort": port, "nodeMgrIps": [manage_ip]}
        http_code, resp = self.rest_api.request("POST", path, body)
        self.get_result_data(resp)
        return resp

    @staticmethod
    def get_result_data(resp):
        err_code = -1
        if "result" in resp:
            result = resp.get('result')
            if "code" in result:
                err_code = result.get('code')
        if str(err_code) != '0':
            raise Exception("request failed")
