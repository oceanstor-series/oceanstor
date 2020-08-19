# OceanStor installation

This document guild how to install OceanStor 100D

## Install ansible

Install the latest ansible(>=2.9.10) using pip

```shell
pip install ansible
```

## Download code and set path

Create directory on ansible node, such as <i>/opt/workspace/oceanstor_series</i>

```shell
# mkdir /opt/workspace/oceanstor_series
# cd /opt/workspace/oceanstor_series
# git clone https://github.com/oceanstor-series/oceanstor.git
# mkdir /root/.ansible/collections/ansible_collections
# ln -s /<your path>/oceanstor_series  /root/.ansible/collections/ansible_collections

```
If you set right, you can see like follow:
```shell
$ ls /root/.ansible/collections/ansible_collections/oceanstor_series/oceanstor
clean_node.yml   galaxy.yml   inventory  __pycache__  roles      vars
fsm-install.yml  install.yml  plugins    README.md    variable.yml
```

Make sure OceanStor 100D artifact file(version 8.0.1) in directory /opt/workspace. 
If other version, please check ansible task and change the parameters oceanstor_artifact_version 
and oceanstor_artifact_dir in roles/hw_oceanstor_management/defaults/main.yml

Before start the work, we need know which Operating system the servers are. 
If they are EulerOS, you don't need this step. 
If not, you need install the dependency package for they. You can see how to do this in the product documentation.

The servers also need configuring the IP address. It can find details in the product documentation as the same.


## Config OceanStor host information
Now you need to config you host information in file:
<b>inventory/inventory.ini</b>
```ini
; Add the host information like this: <address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>

;FSM1.
[fsm-master]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>

;FSM2. If HA deployment mode is sigle, it is the same as FSM1.
[fsm-slave]


;FSA. When you want to clean the fsa node, you need add it to this group.
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

```yaml
# hw_ha_deploy_mode:                              # double : HA deployment mode. HA can be deployed on a single node or two nodes. FusionStorage only supports the two-node deployment mode.
# hw_net_mode:                                    # single/double : Single management plane and dual management planes (internal and external planes) are supported. In the single-management plane deployment mode, the external and internal IP addresses are the same.
# hw_master_float_address:                        # External management floating IP address. The value is the same as the internal floating IP address in the single-management plane deployment mode.
# hw_web_password:                                # The new web login password. This parameter is mandatory for password change. For details about password rules, refer to the security policy.
# hw_master_local_address:                        # External management IP address of FSM 1. The value is the same as the internal management IP address in the single-management plane deployment mode.ss
# hw_master_root_login_pwd:                       # Password of user root used for logging in to FSM 1 using SSH.
# hw_remote_address:                              # External management IP address of FSM 2. The value is the same as the internal management IP address in the single-management plane deployment mode.
# hw_remote_root_login_pwd:                       # Password of user root used for logging in to FSM 2 using SSH.
```

## Install OceanStor 100D manage node

```shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini install.yml -t fsm -e @<your yaml file name>
```
## Change the Initial DeviceManager Login Password 
Change info about the manager float ip and the login password. 

 <b>variable.yml</b>

- hw_web_password: Storage System need change default password when first login.


```yaml
# hw_web_password:                                # The new web login password
```
Now, you can change the password like following

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t change-password -e @<your yaml file name>
```

## Add Node

Change info about Storage node to be added.If you havenot created control cluster, it need add three nodes at least. <b>variable.yml</b>

- hw_server_default_root_password
- hw_server_list

```yaml
# # Add node
# hw_server_default_root_password:     # server default root password. If you donot add root_password, then we will use this.
# hw_server_list:                      # server list. If you hadn't create cluster, there need three server at least.
#  - address:                          # server ip adress
#    root_password:                    # root password.  If you not add root_password, we will use: hw_server_default_root_password
#    role:                             # role list. role: management/storage.  If you not add role, we will set default role: storage
#      - storage 
```
Then you can add storage like following:

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t add-node -e @<your yaml file name>
```
### Config network

This step is configuring  network for communication between VBS and OSD nodes.
<b>variable.yml</b>

```yaml
## Config network
#hw_storage_network:
#  scenario:                        # Scenario. initialization: initialization of the cluster; extend: node expansion
#  transfer_protocol:               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
#  address_list:                    # List of IP addresses.
#    - address_segment:             # IP segment.
#        begin_address:             # Start IP address.
#        end_address:               # End IP address.
#      subnet_prefix:               # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
```
Then you can use follow command to config network and check it.
If it has same error, maybe you should check the parameter settings. Then you can run it again.

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t network  -e @<your yaml file name>
```

### Install Node

When you have successful configured network, the next step is Install Node
, you can use the follow command to install.

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t install-node  -e @<your yaml file name>
```
### Rollback if have error on Add Node or Install Node
When you add node or install node fail and you want try again, you can run the command, 
it will clean the nodes, then you can add the nodes from the step: Add Node.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t restore-factory  -e @<your yaml file name>
```
### Modify the smio config file before create control cluster when your deploy FusionStorage in VM
Login in every nodes to do the following steps. 
Step1: Enter the FusionStorage smio module directory
```shell
# cd /opt/fusionstorage/persistence_layer/osd/ko/EulerOS/$(uname -r)/smio
```
Step2: Modify the file (smio_gen_disk_info_for_vm.sh), modify 14 row and 18 row.
For example:
1）Run the cat /proc/smio_host command to get the drive name of these data disks. 
the name of these data disks are vdb vdc vdd vde vdf.
```shell
# cat /proc/smio_host
```
2）Change the hard disk name in the script file (smio_gen_disk_info_for_vm.sh) to: /dev/*vd[b-f], and change the type to SAS_SSD.
```shell
# vi smio_gen_disk_info_for_vm.sh

smio_gen_disk_info_for_vm.sh:
#!/bin/bash

get_local_ip()
{
    ip address show up | grep -A2 'UP' | grep inet | grep -v 127.0.0.1 | cut -d/ -f1 | cut -d" " -f6-| awk -vFS="." '{print $1 $2 $3 $4}' | head -n 1 | sed "s/\://g"
}

esn=`get_local_ip`;
len=`echo $esn | wc -L`
if [ "${len}" -gt 24 ];then
    esn=`echo ${esn:0-24}`
fi
i=0;
    for devname in /dev/*vd[e-n];    #  Based on the result of cat /proc/smio_host, change '[e-n]'，'[b-n]' denoting contains vdb~vdn
do
    name=`echo $devname |awk -F '/' '{print $3}'`;
    ((i++));
    type=SAS_HDD;                    # Modify 'SAS_HDD' to 'SAS_SSD'
    if [ $name == xvdn ];then
        type=PCIE_SSD;
    fi;
    echo "MAGIC:HUAWEI_DSW_eca34729a05b ESN:$esn$name PHY:0:$i TYPE:$type" > /tmp/devslot;
    dd if=/tmp/devslot of=$devname oflag=direct seek=1920;
done;
``` 
Step3:Excute the command: ./smio_stop && ./smio_gen_disk_info_for_vm.sh && ./smio_start
 
Step4:Excute the command: cat /proc/smio_host, to make sure the Type is SAS_SSD. 
### Create Control Cluster

The next step is Create Control Cluster. You need at least three nodes to create control cluster.
<b>variable.yml</b>
```yaml
# # Create manage cluster
# hw_manage_cluster:
#  name:                                # Cluster name. The value contains up to 64 characters consisting of letters, digits, or underscores (_).
#  serverList:                          # Node list. The number of server must in (3, 5, 7, 9).
#    - address:                         # Server IP address of a node.
#      zkType:                          # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
#      zkDiskSlot:                      # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
#      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
#      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
```
Use the following command.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t mdc  -e @<your yaml file name>
```
### One step do: Insatll manage 、Change password、Add node、Confige Network、Install node、Create Control Cluster
**If you config all the information, you also can run all the work in one step like follow:**
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -e @<your yaml file name>
```

### Import License Parameters
- Now you should log in you management page, which is: [https://<hw_master_float_address>:8088]
- Then copy the SN and log in to [esdp.huawei.com] to apply for a license.
- Upload your license file.

You can also add the license file in <b>variable.yml</b>
```yaml
# hw_license_file_path:          # License file path.When you want activate the Oceation System, you can add the path of license file, and then executes.
```
Then use the command like follow. It will upload the file and activate the license.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t license  -e @<your yaml file name>
```

### Create pool
The next step is Create pool.
<b>variable.yml</b>
```yaml
# hw_oceanstor_pool:
#   name:                         # Storage pool name.The value contains a maximum of 64 characters consisting of letters, digits, and underscores (_).
#   service_type:                 # 1: block 2: file 3: object 4: HDFS
#   encryt_type:                  # Encryption type. 0: common storage pool, 1:encrypted storage pool
#   main_media_type:              # Main storage type of the storage pool."sas_disk": SAS disk, "sata_disk": SATA disk, "ssd_card": SSD card and NVMe SSD, "ssd_disk": SSD
#   cache_media_type:             # Cache type of the storage pool. "ssd_card": SSD card&NVMe SSD, "ssd_disk": SSD, "none": no cache
#   compression_algorithm:        # Compression algorithm. "performance": performance algorithm; "capacity": capacity algorithm
#   redundancy_policy:            # Redundancy policy."replication": replication, "ec": EC
#   replica_num:                  # Replica quantity.Values: 2 and 3.Default value: 2.This parameter is available when ”redundancy_policy“ is "replication".
#   security_level:               # Security level. 0: cabinet level; 1: server level.Only the server level is supported when "redundancyPolicy" is "ec".
#   num_data_units:               # EC data block quantity.Value range: [4, 22].Default value: 4. When "redundancyPolicy" is "ec" and "enableAdvanceVolume" is "false", this parameter must be delivered.
#   num_parity_units:             # EC parity block quantity.Value range: 2-4.Default value: 2.This parameter is available when "redundancyPolicy" is "ec".
#   num_fault_tolerance:          # The default value is the same as the number of parity blocks.
#   server_list:                  # List of server addess
#     - address:                  # Server IP address of a storage node
```
Use the following command. It will create a storage pool.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t create-pool  -e @<your yaml file name>
```
### Create VBS
The next step is Create VBS. When you want create VBS, you need make sure it have in the cluster. 
If you want to create VBS which not in cluster you can use: Add Compute Node .
<b>variable.yml</b>
```yaml
## Create VBS server list
#hw_vbs_list:
#  - address:                     # Server ip adress
```
Use the following command.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t create-VBS  -e @<your yaml file name>
```
### Add storage Node
When you want add storage node, you can config the params almost like add node. Add you 
need make sure the network config right. During the working, we also will check the network.
<b>variable.yml</b>
```yaml
## Add node
#hw_server_default_root_password:     # server default root password. If you donot add root_password, then we will use this.
#hw_server_list:                      # server list. If you hadn't create cluster, there need three server at least.
#  - address:                         # server ip adress
#    root_password:                   # root password.  If you not add root_password, we will use: hw_server_default_root_password
#    role:                            # role list. role: management/storage/compute. If you hadn't create cluster, you cannot choose compute. If you not add role, we will set default role: storage
#      - storage
```
Use the following command. It will add the node to cluster. 
**Rollback if have error on Add Node or Install Node** to clean the nodes, then you can try the following command again.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t add-storage  -e @<your yaml file name>
```

### Add Compute Node
When you want add compute node, you can config the params almost like add storage, but change the role to compute. Add you 
need make sure the network config right. During the working, we also will check the network.
<b>variable.yml</b>
```yaml
## Add node
#hw_server_default_root_password:     # server default root password. If you donot add root_password, then we will use this.
#hw_server_list:                      # server list. If you hadn't create cluster, there need three server at least.
#  - address:                         # server ip adress
#    root_password:                   # root password.  If you not add root_password, we will use: hw_server_default_root_password
#    role:                            # role list. role: management/storage/compute. If you hadn't create cluster, you cannot choose compute. If you not add role, we will set default role: storage
#      - compute
```
Use the following command. It will add the nodes, then create the VBS for these nodes. If you fail in add nodes,
you can use the command in 
**Rollback if have error on Add Node or Install Node** to clean the nodes, then you can try the following command again.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t add-compute  -e @<your yaml file name>
```
### Remove node
When you want to remove nodes, you can do as the follow.
First step: Config the variable *hw_remove_server_list* in <b>variable.yml</b>
```yaml
## Remove node
#hw_remove_server_list:              # server list.
#  - address:                         # server ip adress
#    root_password:                   # root password.
```
Second step: Use the following command.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t remove-node  -e @<your yaml file name>
```
## Clean all node

When you failed to install, or want to clean all node, can use follow command to clear manage node and storage node.
Tips: If you want clear the storage node, you need add the storage node to FSA which in the file *inventory/inventory.ini* .

```shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini clean_node.yml
```
