# OceanStor installation

This document guild how to install OceanStor 100D

## Install ansible

Install the latest ansible(>=2.9.10) using pip

```shell
pip install ansible
```

## Download code and set path

Create directory on ansible node, such as <i>/opt/workspace/oceanstor_series</i>

``` shell
# mkdir /opt/workspace/oceanstor_series
# cd /opt/workspace/oceanstor_series
# git clone https://github.com/oceanstor-series/oceanstor.git
# ln -s /opt/workspace/oceanstor_series /root/.ansible/collections/ansible_collections
# ln -s /opt/workspace/oceanstor_series/oceanstor/oceanstor-client/oceanstor /usr/lib/python2.7/site-packages
```

Make sure OceanStor 100D artifact file(version 8.0.1) in directory /opt/workspace. if other version, please check ansible task and change the parameters oceanstor_artifact_version and oceanstor_artifact_dir in roles\hw_oceanstor_management\defaults\main.yml

``` ansible
- name: Upload OceanStor artifact file to the first FSM node
  copy:
    src: "{{ item }}"
    dest: "{{ oceanstor_deploymanager_dir }}"
    owner: root
    group: root
    mode: u+rw,g-wx,o-rwx
  become: yes
  tags: fsm
  with_fileglob:
      - "{{ oceanstor_artifact_dir }}*{{oceanstor_artifact_version}}*.tar.gz"
```

Modify ansible variable, configuration file roles\hw_oceanstor_management\vars\main.yml
Change follow parameters according env.
- service_float_ip
- service_local_ip
- master_login_pwd
- service_remote_ip
- slave_login_pwd

``` yaml
ha_role: primary       # primary/standby : Role of the HA process. Set this parameter to primary for FSM 1.
init_role: primary     # primary/standby : Initial role. Set this parameter to primary for FSM 1.
ha_mode: double        # double : HA deployment mode. HA can be deployed on a single node or two nodes. FusionStorage only supports the two-node deployment mode.
net_mode: single       # single/double : Management plane deployment mode. Single management plane and dual management planes (internal and external planes) are supported. In the single-management plane deployment mode, the external and internal IP addresses are the same.
service_float_ip: &service_float_ip_config # External management floating IP address. The value is the same as the internal floating IP address in the single-management plane deployment mode.
  10.183.144.46
service_local_ip: &service_local_ip_config # External management IP address of FSM 1. The value is the same as the internal management IP address in the single-management plane deployment mode.ss
  10.183.144.186
master_login_pwd: iq7YV8DGBTc^   # Password of user root used for logging in to FSM 1 using SSH.
service_remote_ip: &service_remote_ip_config # External management IP address of FSM 2. The value is the same as the internal management IP address in the single-management plane deployment mode.
  10.183.144.161
slave_login_pwd: Ra014KO%YVzd   # Password of user root used for logging in to FSM 2 using SSH.
local_sn:
remote_sn:
local_cabinet:
remote_cabinet:
service_gateway:
service_mask:
service_local_port:
service_remote_port:
manager_float_ip: *service_float_ip_config
float_ip_for_ha: *service_float_ip_config
manager_gateway:
manager_mask:
manager_local_ip: *service_local_ip_config
manager_local_port:
manager_remote_ip: *service_remote_ip_config
manager_remote_port:
local_host_name:
remote_host_name:
pk_b:
login_user_name:
login_user_pwd:
login_pwd:
remote_login_user_name:
remote_login_user_pwd:
remote_login_pwd:
```

## Install OceanStor 100D manage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini install.yml -t fsm
```

## Add Storage Node

Modify the parameters <b>roles\hw_oceanstor_storage\defaults\main.yml</b>

- manager_fload_ip: change this value according env.
- api_password: Storage System need change default password when first login.

Change info about Storage node to be added. <b>roles\hw_oceanstor_storage\vars\main.yml</b>

``` yaml
servers_info: [
  {"model": null, "slot_number": "", "name":"", "serial_number": "", "management_internal_ip": "10.183.144.186", "cabinet": "1", "user_name": "root", "password": "iq7YV8DGBTc^","root_password": "iq7YV8DGBTc^", role:["management","storage"], "authentication_mode": "password"},
  {"model": null, "slot_number": "", "name":"", "serial_number": "", "management_internal_ip": "10.183.144.161", "cabinet": "1", "user_name": "root", "password": "Ra014KO%YVzd","root_password": "Ra014KO%YVzd", role:["management","storage"], "authentication_mode": "password"},
  {"model": null, "slot_number": "", "name":"", "serial_number": "", "management_internal_ip": "10.183.145.14", "cabinet": "1", "user_name": "root", "password": "tqg8OQX!C^xL","root_password": "tqg8OQX!C^xL", role:["storage"], "authentication_mode": "password"}
]
```

### Config network Parameters

<b>roles\hw_oceanstor_storage\vars\main.yml</b>

``` yaml
storage_front_network: {
  "bond_mode": "",
  "ip_version": 4,
  "transfer_protocol": "TCP",
  "ip_list": [{"port_name": "", "ip_segment":{"begin_ip":"10.183.144.1", "end_ip":"10.183.145.255"}, "subnet_prefix":"23", "default_gateway":"0.0.0.0"}]
}

storage_backend_network: {
  "bond_mode": "",
  "ip_version": 4,
  "transfer_protocol": "TCP",
  "ip_list": [{"port_name": "", "ip_segment":{"begin_ip":"10.183.144.1", "end_ip":"10.183.145.255"}, "subnet_prefix":"23", "default_gateway":"0.0.0.0"}]
}
```

## Clean all node

When you failed to install, or want to clean all node, can use follow command to clear manage node and storage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini clean_node.yml
```
