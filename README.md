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

Make sure OceanStor 100D artifact file(version 8.0.3) in directory /opt/workspace. if other version, please check ansible task and change the code

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
      - /opt/workspace/OceanStor_100D_{{oceanstor_artifact_version}}*.tar.gz
```

Modify ansible variable, configuration file roles\hw_oceanstor_management\vars\main.yml

``` yaml
ha_role: primary
init_role: primary
local_sn:
remote_sn:
local_cabinet:
remote_cabinet:
ha_mode: double
net_mode: single
service_float_ip: 10.183.144.46
service_gateway: 10.183.144.1
service_mask: 255.255.254.0
service_local_ip: 10.183.144.186
service_local_port: eth0
service_remote_ip: 10.183.144.161
service_remote_port: eth0
manager_float_ip: 10.183.144.46
float_ip_for_ha: 10.183.144.46
manager_gateway: 10.183.144.1
manager_mask: 255.255.254.0
manager_local_ip: 10.183.144.186
manager_local_port: eth0
manager_remote_ip: 10.183.144.161
manager_remote_port: eth0
local_host_name: ctuphisprb00472
remote_host_name: ctuphisprb00475
pk_b: ySaVXoWz3GV3FJoBMCXr8Q==
login_user_name:
login_user_pwd:
login_pwd: sha256.1562.zZ_HB56gSwhj4JlWG-yuHGSbas16KAuEf8REjwQnJXVtKs2vXgO6zOkGzo0OFX622gsKEjuIQ7M=
remote_login_user_name:
remote_login_user_pwd:
remote_login_pwd: sha256.1192.bXsGpM2WZSZ3_l80C9J5HJ41-A3196m2EylPDdYUmsFJbFOnQ7-jbTHi7J9Kh4qlqjfs_5roTy0=
```

pk_b, login_pwd and remote_login_pwd is encryed, and will changed next version.

Install OceanStor 100D manage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini install.yml –t fsm
```

## Clean all node

When you failed to install, or want to clean all node, can use follow command to clear manage node and storage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini clean_node.yml
```
