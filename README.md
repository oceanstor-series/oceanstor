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
```

Make sure OceanStor 100D artifact file(version 8.0.1) in directory /opt/workspace. if other version, please check ansible task and change the parameters oceanstor_artifact_version and oceanstor_artifact_dir in roles\hw_oceanstor_management\defaults\main.yml


Now you need to config you host information in file:
<b>inventory/inventory.ini</b>
``` ini
; Add the host information like this: <address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>

;FSM1
[fsm-master]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>

;FSM2
[fsm-slave]


;FSA: When you need to clean the fsa node, you must add this group.
[fsa]


[fsm:children]
fsm-master
fsm-slave
```

Modify ansible variable, configuration file <b>variable.yml</b>
Change follow parameters according env.
- hw_ha_deploy_mode
- hw_net_mode
- hw_master_float_address
- hw_master_local_address
- hw_master_root_login_pwd
- hw_remote_address
- hw_remote_root_login_pwd

``` yaml
# hw_ha_deploy_mode:                              # double : HA deployment mode. HA can be deployed on a single node or two nodes. FusionStorage only supports the two-node deployment mode.
# hw_net_mode:                                    # single/double : Management plane d
# hw_master_float_address:                        # External management floating IP address. The value is the same as the internal floating IP address in the single-management plane deployment mode.
# hw_web_password:                                # The new web login password. This parameter is mandatory for password change. For details about password rules, refer to the security policy.
# hw_master_local_address:                        # External management IP address of FSM 1. The value is the same as the internal management IP address in the single-management plane deployment mode.ss
# hw_master_root_login_pwd:                       # Password of user root used for logging in to FSM 1 using SSH.
# hw_remote_address:                              # External management IP address of FSM 2. The value is the same as the internal management IP address in the single-management plane deployment mode.
# hw_remote_root_login_pwd:                       # Password of user root used for logging in to FSM 2 using SSH.
```

## Install OceanStor 100D manage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini install.yml -t fsm --skip-tags always -e @<you file name>
```
## Change the Initial DeviceManager Login Password 
Change info about the manager float ip and the login password. 

 <b>variable.yml</b>

- hw_web_password: Storage System need change default password when first login.


``` yaml
# hw_web_password:                                # The new web login password
```
Now, you can change the password like following

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'change-password' -e @<you file name>
```

## Add Storage Node

Change info about Storage node to be added. <b>variable.yml</b>

- hw_server_default_root_password
- hw_server_list

``` yaml
# # Add storage node
# hw_server_default_root_password:     # server default root password. If you donot add root_password, then we will use this.
# hw_server_list:                      # server list
#  - address:                          # server ip adress
#    root_password:                    # root password.  If you not add root_password, we will use: hw_server_default_root_password
#    role:                             # role list. role: management/storage.  If you not add role, we will set default role: storage
#      - storage 
```
Then you can add storage like following:

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'add-storage' -e @<you file name>
```
### Config network Parameters

<b>variable.yml</b>

``` yaml
# # Config network
# hw_storage_network:
#  storage_frontend_network:          # IP address of the front-end network
#    scenario:                        # Scenario. initialization: initialization of the cluster; extend: node expansion
#    transfer_protocol:               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
#    address_list:                    # List of IP addresses.
#      - port_name:                   # Port name. This parameter is mandatory when the IP address of a specified port is configured.
#        address_segment:             # IP segment.
#          begin_address:             # Start IP address.
#          end_address:               # End IP address.
#        subnet_prefix:               # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
#        default_gateway:             # Default gateway. This parameter is required when the IP address of a specified port is configured.
#  storage_backend_network:           # IP address of the back-end network
#    transfer_protocol:               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
#    scenario:                        # Scenario. initialization: initialization of the cluster; extend: node expansion
#    address_list:                    # List of IP addresses.
#      - port_name:                   # Port name. This parameter is mandatory when the IP address of a specified port is configured.
#        address_segment:             # IP segment.
#          begin_address:             # Start IP address.
#          end_address:               # End IP address.
#        subnet_prefix:               # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
#        default_gateway:             # Default gateway. This parameter is required when the IP address of a specified port is configured.
```
Then you can use follow command to config network and check it.

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'network'  -e @<you file name>
```
### Install Storage Node Parameters

When you have successful configured network, the next step is Install Storage Node
, you can use the follow comman to create.

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'install-storage'  -e @<you file name>
```
### Create Control Cluster Parameters

The next step is Create Control Cluster.
<b>variable.yml</b>
``` yaml
# # Create manage cluster
# hw_manage_cluster:
#  name:                                # Cluster name. The value contains up to 64 characters consisting of letters, digits, or underscores (_).
#  serverList:                          # Node list.
#    - address:                         # Server IP address of a node.
#      zkType:                          # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
#      zkDiskSlot:                      # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
#      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
#      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
```

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'mdc'  -e @<you file name>
```
### Import License Parameters
- Now you should log in you management page, which is: https://<hw_master_float_address>:8088/
- Then copy the SN and log in to esdp.huawei.com to apply for a license.
- Upload your license file.

### Create pool
The next step is Create Control Cluster.
<b>variable.yml</b>
``` yaml
# hw_oceanstor_pool:
#   name:                         # pool name
#   service_type:                 # 1: block 2: file 3: object 4: HDFS
#   encryt_type:                  # 0: common storage pool, 1:encrypted storage pool
#   main_media_type:              # "sas_disk": SAS disk, "sata_disk": SATA disk, "ssd_card": SSD card and NVMe SSD, "ssd_disk": SSD
#   cache_media_type:             # Cache type of the storage pool. "ssd_card": SSD card&NVMe SSD, "ssd_disk": SSD, "none": no cache
#   ompression_algorithm:         # Compression algorithm. "performance": performance algorithm; "capacity": capacity algorithm
#   redundancy_policy:            # "replication": replication, "ec": EC
#   replica_num:                  # Values: 2 and 3
#   security_level:               # 0: cabinet level; 1: server level
#   num_data_units:               # Value range: [4, 22]
#   num_parity_units:             # Value range: 2-4
#   num_fault_tolerance:          # Number of simultaneous failures.
#   server_list:                  # list of server addess
#     - address:                  # Server IP address of a storage node
```

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'create-pool'  -e @<you file name>
```
### Create VBS
The next step is Create Control Cluster.
<b>variable.yml</b>
``` yaml
# # Create VBS server list
# hw_vbs_list:
#  - address:                     # Server ip adress
```

``` shell
ansible-playbook -i inventory/inventory.ini install.yml -t 'create-VBS'  -e @<you file name>
```

## Clean all node

When you failed to install, or want to clean all node, can use follow command to clear manage node and storage node

``` shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini clean_node.yml
```
