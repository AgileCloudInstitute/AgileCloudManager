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

##################################################
## Install Terraform
cd /home/aci-user
[[ -d terraform-download ]] || mkdir terraform-download
cd terraform-download
wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip
unzip terraform_0.12.24_linux_amd64.zip
chown aci-user:aci-user /home/aci-user/terraform-download
#Move the terraform binary into a folder that is listed as part of the PATH variable.  
mv terraform /usr/local/bin/

# #Install azdo provider
# cd /home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/
# [[ -d terraform.d/ ]] || mkdir terraform.d/
# [[ -d terraform.d/plugins/ ]] || mkdir terraform.d/plugins/
# [[ -d terraform.d/plugins/linux_amd64 ]] || mkdir terraform.d/plugins/linux_amd64
# chown aci-user:aci-user -R terraform.d/

# cd terraform.d/plugins/linux_amd64
# wget https://github.com/microsoft/terraform-provider-azuredevops/releases/download/v0.1.2/terraform-provider-azuredevops_linux_amd64.tar.gz
# tar xzf terraform-provider-azuredevops_linux_amd64.tar.gz
# rm terraform-provider-azuredevops_linux_amd64.tar.gz
# cd /home/aci-user/cloned-repos/agile-cloud-manager/calls-to-modules/azure-pipelines-project-repo-build-resources/

###################################################  
## Install the azure-cli  
  
#Get the microsoft key 
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

#Set the local yum pointer to the official microsoft repo for azure-cli
sudo sh -c 'echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'

#Workaround a bug in the az-cli installation that fails to see that Python 3.6+ is already installed.
#Identify the most recent version of the RPM from this address: https://packages.microsoft.com/yumrepos/azure-cli/
#Then specify the RPM explicitly in the following line:
sudo rpm -ivh --nodeps azure-cli-2.8.0-1.el7.x86_64.rpm

#Install the azure-devops extension of the az-cli
az extension add --name azure-devops

