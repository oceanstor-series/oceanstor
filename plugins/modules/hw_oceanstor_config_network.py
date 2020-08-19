#!/usr/bin/python

# (c) 2020, huawei, Inc


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.oceanstor_series.oceanstor.plugins.module_utils.oceanstor.oceanstor_add_storage \
    import OceanStorStorage


class HuaweiOceanStorConfigNetwork(object):
    def __init__(self):
        ansible_options = dict(api_url=dict(type="str", required=True),
                               api_port=dict(type="int", required=True),
                               username=dict(type="str", required=True),
                               password=dict(type="str", required=True, no_log=True),
                               token=dict(type="str", required=True),
                               validate_certs=dict(type="bool", default=False, required=False),
                               network_type=dict(type="str", required=True,
                                                 choices=["management_external_float",
                                                          "management_internal_float",
                                                          "management_external",
                                                          "management_internal",
                                                          "storage_frontend",
                                                          "storage_backend",
                                                          "replication", "quorum", "iscsi"]),
                               network_param=dict(type="dict", required=True),
                               step=dict(type="str", default="config_network",
                                         choices=["validity_network", "config_network"]))

        required_together = [["api_url", "api_port", "username", "password", "network_type", "network_param"]]

        self.module = AnsibleModule(argument_spec=ansible_options, required_together=required_together)

        self.base_url = self._format_base_url()

        username = self.module.params["username"]
        password = self.module.params["password"]
        token = self.module.params["token"]

        self.oceanstor = OceanStorStorage(self.base_url, username, password, token)

    def _format_base_url(self):
        url = self.module.params["api_url"]
        port = self.module.params["api_port"]
        return "https://{0}:{1}".format(url, port)

    def config_network(self):
        """Config OceanStor network."""
        # step 1: check storage connection
        network_type = self.module.params['network_type']
        network_param = self.module.params['network_param']
        param = dict()
        param['name'] = ''
        transfer_protocol = network_param['transfer_protocol']
        param['transfer_protocol'] = network_param['transfer_protocol']
        ip_list = []
        default_gateway = '0.0.0.0'
        default_port_name = ''
        for ip in network_param['address_list']:
            address_segment = dict()
            address_segment['begin_ip'] = ip['address_segment']['begin_address']
            address_segment['end_ip'] = ip['address_segment']['end_address']
            ip_param = dict(port_name=ip.get('port_name', default_port_name), ip_segment=address_segment,
                            subnet_prefix=str(ip['subnet_prefix']),
                            default_gateway=ip.get('default_gateway', default_gateway))
            ip_list.append(ip_param)
        param['ip_list'] = ip_list

        response = self.oceanstor.config_network_type(network_type, transfer_protocol, param)

        if str(response['result']['code']) != '0':
            self.module.fail_json(msg=("Config OceanStor network Error {0}--{1}"
                                       ).format(response['result']['code'], response['result']['description']),
                                  changed=False)
        elif 'success' in response['result']['description']:
            self.module.exit_json(msg="Config OceanStor network complete", changed=True)
        else:
            self.module.fail_json(msg=("Config OceanStor network Error {0}--{1}"
                                       ).format(response['result']['code'], response['result']['description']),
                                  changed=False)

    def validity_network(self):
        """Validity network"""
        response = self.oceanstor.get_server_info()
        servers = response["data"]
        server_param = []
        for server in servers:
            server_param.append({"management_internal_ip": server['management_internal_ip']})

        network_type = self.module.params['network_type']

        response = self.oceanstor.validity_network(network_type, server_param)

        if str(response['result']['code']) != '0':
            self.module.fail_json(changed=False, msg=("Validity OceanStor {0} network Error {1}--{2}"
                                                      ).format(network_type, response['result']['code'],
                                                               response['result']['description']))
        else:
            self.module.exit_json(msg="Validity OceanStor {0} network complete".format(network_type), changed=True)

    def update(self):
        step = self.module.params["step"]

        if step == "config_network":
            self.config_network()

        elif step == "validity_network":
            self.validity_network()


def main():
    settings = HuaweiOceanStorConfigNetwork()
    settings.update()


if __name__ == '__main__':
    main()
