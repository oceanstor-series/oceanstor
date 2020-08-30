# OceanStor 100D (FusionStorage) Installation

This document guild how to install OceanStor 100D (FusionStorage)

## 1. Install ansible

Install the latest ansible(>=2.9.10) using pip

```shell
pip install ansible
```

## 2. Download code and set path

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

Make sure OceanStor 100D(FusionStorage) artifact file(version 8.0.1) in directory /opt/workspace. 
If other version, please check ansible task and change the parameters oceanstor_artifact_version 
and oceanstor_artifact_dir in roles/hw_oceanstor_management/defaults/main.yml

Before start the work, we need know which Operating system the servers are. 
If they are EulerOS, you don't need this step. 
If not, you need install the dependency package for they. You can see how to do this in the product documentation.

The servers also need configuring the IP address. It can find details in the product documentation as the same.

## 3. Install OceanStor 100D (FusionStorage)
There have six steps to install OceanStor 100D (FusionStorage). If it is the first time to do this, you'd better 
do it step-by-step, the detail step are in [**Install Details**](#Appendixe1:) at the end of the README file. If not, you can do like follow.

Befor start install oceanstor 100D (Fusionstorage), it need config some inforamations.
The information need to add to the file <b>inventory/inventory.ini</b> and <b>variable.yml</b>.
<br>
Config the hosts information in the file: <b>inventory/inventory.ini</b>.
<br>
For example:
```ini
; Add the host information like this: <address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
;address: the IP address of host. method: ansible connection method, usually use:ssh. 
;FSM1.
[fsm-master]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.2   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
;FSM2. If HA deployment mode is sigle, it is the same as FSM1.
[fsm-slave]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.3   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa

;FSA. When you want to clean the fsa node, you need add it to this group.
[fsa]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.2   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
192.0.0.3   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
192.0.0.4   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa

[fsm:children]
fsm-master
fsm-slave
```
Then modify the file <b>variable.yml</b> about the FSM nodes information.
<br>
For example:
```yaml
hw_ha_deploy_mode: double                       # double/singel  double: HA deployment mode. HA can be deployed on a single node or two nodes. FusionStorage only supports the two-node deployment mode.
hw_net_mode: singel                             # single/double  single: Single management plane and dual management planes (internal and external planes) are supported. In the single-management plane deployment mode, the external and internal IP addresses are the same.
hw_master_float_address: 192.168.0.1            # External management floating IP address. The value is the same as the internal floating IP address in the single-management plane deployment mode.
hw_web_password: '******'                       # The new web login password. This parameter is mandatory for password change. For details about password rules, refer to the security policy.
hw_master_local_address: 192.168.0.2            # External management IP address of FSM 1. The value is the same as the internal management IP address in the single-management plane deployment mode.ss
hw_master_root_login_pwd: '******'              # Password of user root used for logging in to FSM 1 using SSH.
hw_remote_address: 192.168.0.3                  # External management IP address of FSM 2. The value is the same as the internal management IP address in the single-management plane deployment mode.
hw_remote_root_login_pwd: '******'              # Password of user root used for logging in to FSM 2 using SSH.
```

Then add three storage nodes at least , and the role of 
node cannot contain ***compute***. If the node role is both management and storage, you need add they both.
<br>
For example:
```yaml
# hw_server_default_root_password:    # server default root password. If you donot add root_password, then we will use this.
hw_server_list:                       # server list. If you hadn't create cluster, there need three servers at least.
  - address: 192.168.0.2              # server ip adress
    user_name: hwstorage              # the login name. If the value if null, the script will uses root by default.
    password: '******'                # password for user_name.
    root_password: '******'           # root password.  If you not add root_password, we will use: hw_server_default_root_password
    role:                             # role list. role: management/storage/compute.  If you not add role, we will set default role: storage
      - management 
      - storage
  - address: 192.168.0.3                         
    root_password: '******'
    role:                             
      - management 
      - storage
  - address: 192.168.0.4             
    root_password: '******'           
    role:                            
      - storage
```
Then config the storage frontend network and storage backend network.
For example:
```yaml
hw_storage_network:
  storage_frontend_network:              # IP address of the front-end network
    scenario: initialization             # Scenario. initialization: initialization of the cluster; extend: node expansion
    transfer_protocol: TCP               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
    address_list:                        # List of IP addresses.
      - address_segment:                 # IP segment.
          begin_address: 192.168.0.1     # Start IP address.
          end_address: 192.168.0.255     # End IP address.
        subnet_prefix: 24                # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
  storage_backend_network:               # IP address of the back-end network
    scenario: initialization             # Scenario. initialization: initialization of the cluster; extend: node expansion
    transfer_protocol: TCP               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
    address_list:                        # List of IP addresses.
      - address_segment:                 # IP segment.
          begin_address: 192.168.0.1     # Start IP address.
          end_address: 192.168.0.255     # End IP address.
        subnet_prefix: 24                # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
```
Add the control cluster information about which you want to create.
You need at least three nodes to create control cluster. 
<br>
For example:
```yaml
# Create manage cluster
hw_manage_cluster:
  name: hw_cluster                     # Cluster name. The value contains up to 64 characters consisting of letters, digits, or underscores (_).
  serverList:                          # Node list. The number of server must in (3, 5, 7, 9).
    - address: 192.168.0.2             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
    - address: 192.168.0.3             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
    - address: 192.168.0.4             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
```
Then run the following command. If there have some errors, you can start from the failure step.

```shell
ansible-playbook -i inventory/inventory.ini install.yml -e @<your yaml file name>
```


##4. Import License
- Now you can login in you management page, which is: [https://<hw_master_float_address>:8088]()
- Then copy the ESN and log in to [https://esdp.huawei.com](https://esdp.huawei.com) to apply for a license.
- Upload your license file.

You can also add the path of license file in <b>variable.yml</b> 
<br>
For example:
```yaml
hw_license_file_path: /opt/workspace/oceanstor_series/oceanstor/LICFusionStorageRA_xxx.dat   # License file path.When you want activate the Oceation System, you can add the path of license file, and then executes.
```
Then use the command like follow. It will upload the file and activate the license.
```shell
ansible-playbook -i inventory/inventory.ini install.yml -t import-license  -e @<your yaml file name>
```

##5. Create Pool
The next step is Create pool. Add the information in file <b>variable.yml</b>. <br>
1） You need add three servers at least and each server need four unused disks at least.<br>
2） If you don't add ***mediaList***, the script will use all the unused disks in 
the server to create pool.
For example:
```yaml
hw_oceanstor_pool:
  name: hw_pool                        # Storage pool name.The value contains a maximum of 64 characters consisting of letters, digits, and underscores (_).
  service_type: 1                      # 1: block 2: file 3: object 4: HDFS
  encryt_type: 0                       # Encryption type. 0: common storage pool, 1:encrypted storage pool
  main_media_type: ssd_disk            # Main storage type of the storage pool."sas_disk": SAS disk, "sata_disk": SATA disk, "ssd_card": SSD card and NVMe SSD, "ssd_disk": SSD
  cache_media_type: none               # Cache type of the storage pool. "ssd_card": SSD card&NVMe SSD, "ssd_disk": SSD, "none": no cache
  compression_algorithm:               # Compression algorithm. "performance": performance algorithm; "capacity": capacity algorithm
  redundancy_policy: ec                # Redundancy policy."replication": replication, "ec": EC
  replica_num: 3                       # Replica quantity.Values: 2 and 3.Default value: 2.This parameter is available when ”redundancy_policy“ is "replication".
  security_level: server               # Security level. server: server level; rack: cabinet level; disk: disk level.Only the server level is supported when "redundancyPolicy" is "ec".
  num_data_units: 4                    # EC data block quantity.Value range: [4, 22].Default value: 4. When "redundancyPolicy" is "ec" and "enableAdvanceVolume" is "false", this parameter must be delivered.
  num_parity_units: 2                  # EC parity block quantity.Value range: 2-4.Default value: 2.This parameter is available when "redundancyPolicy" is "ec".
  num_fault_tolerance: 1               # The default value is the same as the number of parity blocks.
  server_list:                         # List of server addess. The number of servers at least three,  and each server need four unused disks at least.
    - address: 192.168.0.2             # Server IP address of a storage node.
      mediaList:                       # List of main storage disks and cache disks for creating the storage pool. You can not add this, then the script will use all the unuse disks to create pool.
        - mediaRole: main_storage      # Media role."main_storage": main storage; "osd_cache": cache.
          mediaType: ssd_disk          # Cache type."sas_disk": SAS disk;"sata_disk": SATA disk;"ssd_card": SSD card and NVMe SSD;"ssd_disk": SSD
          phyDevEsn: 10183144186xvdf   # Physical ESN.
          phySlotId: 2                 # Physical slot ID.
        - mediaRole: main_storage
          mediaType: ssd_disk
          phyDevEsn: 10183144186xvdg
          phySlotId: 3
        - mediaRole: main_storage
          mediaType: ssd_disk
          phyDevEsn: 10183144186xvdh
          phySlotId: 4
        - mediaRole: main_storage
          mediaType: ssd_disk
          phyDevEsn: 10183144186xvdi
          phySlotId: 5
    - address: 192.168.0.3
    - address: 192.168.0.4
```
Use the following command. It will create a storage pool.
```shell
ansible-playbook -i inventory/inventory.ini install.yml -t create-pool  -e @<your yaml file name>
```
##6. Create VBS
When you want to create VBS, you need add the compute nodes IP address and password in the file 
<b>variable.yml</b>.
<br>
If the root_password is null, the script will use the value of ***hw_server_default_root_password***.
If the user_name is null, the script will use user: root.
```yaml
# Create VBS server list
hw_vbs_list:
  - address: 192.168.0.5         # compute node ip adress
    user_name: hwcompute         # the login name. If the value if null, the script will uses root by default.
    password: '******'           # password for user_name.
    root_password: '******'      # root password. If you donot input this, the script will use the value of "hw_server_default_root_password".
```
Use the following command. It will do two things. Firstly: add the node to 
cluster (if the node not in cluster); Secondly: create the vbs server.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t create-VBS  -e @<your yaml file name>
```
If there have some error during work, you can also use 
```shell
ansible-playbook -i inventory/inventory.ini install.yml -t restore-factory  -e @<your yaml file name>
```
Then you can try to create again.

##7. Add storage Node For Expansion
When you need capacity expansion, you can add the nodes in the ***hw_server_list*** 
in file <b>variable.yml</b>. Add you 
need make sure the network config is correct. During the working, we will check the network.

```yaml
## Add node
#hw_server_default_root_password:     # server default root password. If you donot add root_password, then we will use this.
#hw_server_list:                      # server list. If you hadn't create cluster, there need three server at least.
#  - address:                         # server ip adress
#    root_password:                   # root password.  If you not add root_password, we will use: hw_server_default_root_password
#    role:                            # role list. role: management/storage/compute. If you hadn't create cluster, you cannot choose compute. If you not add role, we will set default role: storage
#      - storage
```
Use the following command. It will add the node to cluster. <br>
If there are some error during add storage node, you can use:
**Rollback if have error on Add Node or Install Node** to clean the nodes, then you can try the following command again.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t add-storage  -e @<your yaml file name>
```

##8. Remove node
When you want to remove node, you need make sure there are no services on the node. 
Config the variable ***hw_remove_server_list*** in <b>variable.yml</b>
```yaml
## Remove node
#hw_remove_server_list:              # server list.
#  - address:                         # server ip adress
#    user_name:
#    password:
#    root_password:                   # root password.
```
Then run the follow command.
```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t remove-node  -e @<your yaml file name>
```
##9. Clean all node

When you failed to install, or want to clean all the nodes, you can use follow command 
to clear management nodes and storage nodes.<br>
Tips: If you want clear the storage node, you need add the storage node to FSA which in 
the file *inventory/inventory.ini* .

```shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini clean_node.yml
```
Appendixe1:
------------
## Install OceanStor 100D (FusionStorage) Detail Steps:
### 3.1 Install management nodes
Before you start install the management nodes, you need to config the hosts information in the file:
<b>inventory/inventory.ini</b>
```ini
; Add the host information like this: <address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
;address: the IP address of host. method: ansible connection method, usually use:ssh. 
;FSM1.
[fsm-master]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.2   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
;FSM2. If HA deployment mode is sigle, it is the same as FSM1.
[fsm-slave]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.3   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa

;FSA. When you want to clean the fsa node, you need add it to this group.
[fsa]
;<address>  ansible_connection=<method>  ansible_user=<user_name>  ansible_ssh_private_key_file=<key_file>
192.0.0.2   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
192.0.0.3   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa
192.0.0.4   ansible_connection=ssh  ansible_user=root  ansible_ssh_private_key_file=/root/.ssh/id_rsa

[fsm:children]
fsm-master
fsm-slave
```
Then modify ansible variable, configuration file <b>variable.yml</b>
Change follow parameters according env.

```yaml
hw_ha_deploy_mode: double                       # double/singel double: HA deployment mode. HA can be deployed on a single node or two nodes. FusionStorage only supports the two-node deployment mode.
hw_net_mode: singel                             # single/double : Single management plane and dual management planes (internal and external planes) are supported. In the single-management plane deployment mode, the external and internal IP addresses are the same.
hw_master_float_address: 192.168.0.1            # External management floating IP address. The value is the same as the internal floating IP address in the single-management plane deployment mode.
hw_web_password: '******'                       # The new web login password. This parameter is mandatory for password change. For details about password rules, refer to the security policy.
hw_master_local_address: 192.168.0.2            # External management IP address of FSM 1. The value is the same as the internal management IP address in the single-management plane deployment mode.ss
hw_master_root_login_pwd: '******'              # Password of user root used for logging in to FSM 1 using SSH.
hw_remote_address: 192.168.0.3                  # External management IP address of FSM 2. The value is the same as the internal management IP address in the single-management plane deployment mode.
hw_remote_root_login_pwd: '******'              # Password of user root used for logging in to FSM 2 using SSH.
```
Now you can run the command follow:
```shell
# cd /opt/workspace/oceanstor_series/oceanstor
# ansible-playbook -i inventory/inventory.ini install.yml -t install-management -e @<your yaml file name>
```
### 3.2 Change the Initial DeviceManager Login Password 
When you first login the web of Fusionstarage, you need change the login password. 
You can do this like follow. Change the value of ***hw_web_password*** in file: <b>variable.yml</b> .

```yaml
# hw_web_password: ******                           # The new web login password
```
Now, you can change the password like following

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t change-password -e @<your yaml file name>
```

### 3.3 Add Storage Node

Add the information about the node in the file. 
You need add three storage nodes at least, and the role of 
node cannot contain ***compute***. Add the nodes 
 information in file <b>variable.yml</b>

```yaml
# hw_server_default_root_password:    # server default root password. If you donot add root_password, then we will use this.
hw_server_list:                       # server list. If you hadn't create cluster, there need three servers at least.
  - address: 192.168.0.2              # server ip adress
    user_name: hwstorage              # the login name. If the value if null, the script will uses root by default.
    password: '******'                # password for user_name.
    root_password: '******'           # root password.  If you not add root_password, we will use: hw_server_default_root_password
    role:                             # role list. role: management/storage/compute.  If you not add role, we will set default role: storage
      - management 
      - storage
  - address: 192.168.0.3                         
    root_password: '******'
    role:                             
      - management 
      - storage
  - address: 192.168.0.4             
    root_password: '******'           
    role:                            
      - storage
```
Then you can add storage like following:

```shell
# ansible-playbook -i inventory/inventory.ini install.yml -t add-node -e @<your yaml file name>
```
### 3.4 Config Storage Network

This step is configuring storage frontend network
 and storage backend network. Add the network information in file
<b>variable.yml</b>

```yaml
hw_storage_network:
  storage_frontend_network:              # IP address of the front-end network
    scenario: initialization             # Scenario. initialization: initialization of the cluster; extend: node expansion
    transfer_protocol: TCP               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
    address_list:                        # List of IP addresses.
      - address_segment:                 # IP segment.
          begin_address: 192.168.0.1     # Start IP address.
          end_address: 192.168.0.255     # End IP address.
        subnet_prefix: 24                # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
  storage_backend_network:               # IP address of the back-end network
    scenario: initialization             # Scenario. initialization: initialization of the cluster; extend: node expansion
    transfer_protocol: TCP               # Transmission protocols: TCP/InfiniBand/RDMA over Converged Ethernet
    address_list:                        # List of IP addresses.
      - address_segment:                 # IP segment.
          begin_address: 192.168.0.1     # Start IP address.
          end_address: 192.168.0.255     # End IP address.
        subnet_prefix: 24                # Subnet mask/prefix. This parameter is required when the IP address of a specified port is configured.
```
Then you can use follow command to config network and check it.
If it has some error, maybe you should check the parameter settings. Then you can run it again.

```shell
ansible-playbook -i inventory/inventory.ini install.yml -t config-network  -e @<your yaml file name>
```
### 3.5 Install Storage Node

When you have successfully configured network, the next step is Install Storage Node
, you can use the follow command to install.

```shell
ansible-playbook -i inventory/inventory.ini install.yml -t install-node  -e @<your yaml file name>
```
If there are some errors during install storage nodes, you can use the follow command 
 to clean the nodes, then start the work from **3.4 Add Storage Node** step-by-step.
```shell
ansible-playbook -i inventory/inventory.ini install.yml -t restore-factory  -e @<your yaml file name>
```
**Before Create Control Cluster, you need check whether the nodes is VM. If it is, 
you need [Modify the smio config file](#Appendixe2)**.
### 3.6 Create Control Cluster
When you have installed the storage nodes, then you can create control cluster.
You need at least three nodes to create control cluster. Add it's information in the file.
<b>variable.yml</b>
```yaml
# Create manage cluster
hw_manage_cluster:
  name: hw_cluster                     # Cluster name. The value contains up to 64 characters consisting of letters, digits, or underscores (_).
  serverList:                          # Node list. The number of server must in (3, 5, 7, 9).
    - address: 192.168.0.2             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
    - address: 192.168.0.3             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
    - address: 192.168.0.4             # Server IP address of a node.
      zkType: ssd_disk                 # ZooKeeper disk type. Independent disks (SSDs and HDDs) and system disks are supported."sas_disk": SAS HDD;"sata_disk": SATA HDD;"ssd_disk": SAS SSD;"ssd_card": SSD card and NVMe SSD;"sys_disk": system disk
      zkDiskSlot: 1                    # Slot ID of the ZooKeeper disk. This parameter is mandatory when "sas", "sata", "ssd_disk", or "ssd_card" is specified for "zkType".
      zkDiskEsn:                       # ESN of the ZooKeeper disk. This parameter is mandatory when "zkType" is set to "ssd_card".
      zkPartition:                     # Mount path of a partition. This parameter is mandatory when "partition" is specified for "zkType".
```
Use the following command.
```shell
ansible-playbook -i inventory/inventory.ini install.yml -t create-control-cluster  -e @<your yaml file name>
```
Appendixe2:
-----------
## Modify the smio config file before create control cluster when your deploy FusionStorage in VM
Login in every nodes to do the following steps. <br>
Step1: Enter the FusionStorage smio module directory
```shell
cd /opt/fusionstorage/persistence_layer/osd/ko/EulerOS/$(uname -r)/smio
```
Step2: Modify the file (smio_gen_disk_info_for_vm.sh), modify 14 row and 18 row.<br>
For example:<br>
1）Run the cat /proc/smio_host command to get the drive name of these data disks. 
the name of these data disks are vdb vdc vdd vde vdf.
```shell
cat /proc/smio_host
```
2）Change the hard disk name in the script file (smio_gen_disk_info_for_vm.sh) to: /dev/*vd[b-f], 
and change the type to PCIE_SSD.
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
    type=SAS_HDD;                    # Modify 'SAS_HDD' to 'PCIE_SSD'
    if [ $name == xvdn ];then
        type=PCIE_SSD;
    fi;
    echo "MAGIC:HUAWEI_DSW_eca34729a05b ESN:$esn$name PHY:0:$i TYPE:$type" > /tmp/devslot;
    dd if=/tmp/devslot of=$devname oflag=direct seek=1920;
done;
``` 
Step3:Excute the command: ./smio_stop && ./smio_gen_disk_info_for_vm.sh && ./smio_start
 
Step4:Excute the command: cat /proc/smio_host, to make sure the Type is PCIE_SSD. 