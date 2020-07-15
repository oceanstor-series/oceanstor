#!/usr/bin/python

# (c) 2020, huawei, Inc


from ansible.module_utils.basic import AnsibleModule
from oceanstor.oceanstor_add_storage import OceanStorStorage

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
        param = self.module.params['network_param']
        self.oceanstor.config_network_type(network_type, param["transfer_protocol"], param)

        self.module.warn("{0}-{1}".format(network_type, param.__str__()))

        self.module.exit_json(msg="Config OceanStor network complete",
                              changed=True)

    def validity_network(self):
        """Validity network"""
        response, code = self.oceanstor.get_server_info()
        servers = response["data"]
        server_param = []
        for server in servers:
            server_param.append({"management_internal_ip": server['management_internal_ip']})
        
        network_type = self.module.params['network_type']

        self.oceanstor.validity_network(network_type, server_param)

        self.module.exit_json(msg="Valid network complete", changed=True)

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
