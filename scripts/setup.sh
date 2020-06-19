#!/bin/bash  

[[ -d /home/aci-user/vars ]] || mkdir /home/aci-user/vars
[[ -d /home/aci-user/vars/agile-cloud-manager ]] || mkdir /home/aci-user/vars/agile-cloud-manager
#mkdir /home/aci-user/vars/agile-cloud-manager
cp -a /home/aci-user/cloned-repos/agile-cloud-manager/move-to-directory-outside-app-path/. /home/aci-user/vars/agile-cloud-manager/

#Set ACM_ROOT_DIR environment variable:
export ACM_ROOT_DIR=/home/aci-user/cloned-repos/agile-cloud-manager/
echo 'export ACM_ROOT_DIR=/home/aci-user/cloned-repos/agile-cloud-manager/' >> /etc/environment
echo 'export ACM_ROOT_DIR=/home/aci-user/cloned-repos/agile-cloud-manager/' >> /etc/bashrc
echo 'export ACM_ROOT_DIR=/home/aci-user/cloned-repos/agile-cloud-manager/' >> /etc/profile
