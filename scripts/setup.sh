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

#Install Python 3 (VM may already have Python 2 installed, which is not high enough for our needs.)
## Install Python 3.7 (Note: Next time try different location outside of PATH to see if it is added automatically to PATH.)
#Install Python 3.7
yum install -y gcc openssl-devel bzip2-devel libffi-devel
cd /usr/local/bin/
wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
tar xzf Python-3.7.7.tgz
cd Python-3.7.7
./configure --enable-optimizations
make altinstall
rm /usr/local/bin/Python-3.7.7.tgz
python3.7 -V


#Install azdo provider

