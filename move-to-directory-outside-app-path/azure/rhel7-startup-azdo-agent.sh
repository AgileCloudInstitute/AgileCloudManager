#!/bin/bash

#The following command set -e will cause the script to exit the moment any error is thrown by any command in the script.  
#set -e

#####################################################################################################
#### Section One: Set environment variables, including secrets. Later, these will come from a key vault.
####              SECURITY ALERT: RE-WRITE THE FOLLOWING TO RETRIEVE THE SECRETS FROM A KEYVAULT OR 
####              FROM SOME SECURE LOCATION.  Also make sure secrets are not printed to logs.  
#####################################################################################################

echo "About to echo who am i: "
whoami

echo "About to echo $USR_NM : "
export USR_NM=$USR_NM
echo $USR_NM

echo "About to set environment_variables .  "
## NOTE:  OBSCURING PASSWORDS FROM LOGS BY ADDING:  

#Set AZ_PASS environment variable:
export AZ_PASS=$AZ_PSS
echo "export AZ_PASS='$AZ_PSS'" >> /etc/environment
echo "export AZ_PASS='$AZ_PSS'" >> /etc/bashrc
echo "export AZ_PASS='$AZ_PSS'" >> /etc/profile
#Set AZ_CLIENT environment variable:
export AZ_CLIENT=$AZ_CLNT
echo "export AZ_CLIENT=$AZ_CLNT" >> /etc/environment
echo "export AZ_CLIENT=$AZ_CLNT" >> /etc/bashrc
echo "export AZ_CLIENT=$AZ_CLNT" >> /etc/profile
#Set AZ_TENANT environment variable:
export AZ_TENANT=$AZ_TNT
echo "export AZ_TENANT=$AZ_TNT" >> /etc/environment
echo "export AZ_TENANT=$AZ_TNT" >> /etc/bashrc
echo "export AZ_TENANT=$AZ_TNT" >> /etc/profile
#Set AZ_PAT environment variable: 
export AZ_PAT=$AZ_PT
echo "export AZ_PAT=$AZ_PT" >> /etc/environment
echo "export AZ_PAT=$AZ_PT" >> /etc/bashrc
echo "export AZ_PAT=$AZ_PT" >> /etc/profile
#Set AZ_SERVER environment variable:  
export AZ_SERVER=$AZ_SRVR
echo "export AZ_SERVER=$AZ_SRVR" >> /etc/environment
echo "export AZ_SERVER=$AZ_SRVR" >> /etc/bashrc
echo "export AZ_SERVER=$AZ_SRVR" >> /etc/profile
#Set AZURE_DEVOPS_EXT_PAT environment variable.  Used by az devops cli extension.  Keeping this separate from $AZ_PAT to increase customizability.  
export AZURE_DEVOPS_EXT_PAT=$AZ_PT
echo "export AZURE_DEVOPS_EXT_PAT=$AZ_PT" >> /etc/environment
echo "export AZURE_DEVOPS_EXT_PAT=$AZ_PT" >> /etc/bashrc
echo "export AZURE_DEVOPS_EXT_PAT=$AZ_PT" >> /etc/profile
  
###########################################################################################################
#### Section Two:  Create user then install dependencies.
###########################################################################################################
echo "About to check if $USR_NM exists.  1 if exists and 0 if does not exist: "
grep -c "^$USR_NM:" /etc/passwd
  
#Configure user to not require password to execute sudo commands by first deleting sudoer membership and then recreating without password requirement.
rm -f /etc/sudoers.d/waagent
  
cat << EOF > /etc/sudoers.d/waagent
$USR_NM ALL=(ALL) NOPASSWD: ALL
EOF

#echo "About to cat /etc/sudoers.d/waagent "
#cat /etc/sudoers.d/waagent

yum clean all 

#First update the certificate so that dnf update commands below can work properly.  If you do not update certificates with this line, the script can break.  
echo "About to dnf update -y --disablerepo='*' --enablerepo='*microsoft*'  "
dnf update -y --disablerepo='*' --enablerepo='*microsoft*'

echo "--------------------------------------------------"
echo "About to dnf update"
dnf update -y
echo "Done with dnf update. "
echo "--------------------------------------------------"
dnf install -y git 
#Check version
git --version

## Next, Install dependencies using the just updated certificate:  
dnf install -y openssl curl dos2unix

## Install Terraform
cd /home/$USR_NM
mkdir terraform-download
cd terraform-download
wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip
unzip terraform_0.12.24_linux_amd64.zip
#Move the terraform binary into a folder that is listed as part of the PATH variable.  
mv terraform /usr/local/bin/
cd /home/$USR_NM

#-->echo "About to install python3"
#-->dnf install -y python3
#-->dnf install -y python3-setuptools
#-->dnf install python3-pip -y

#Have to install epel using rpm because dnf could not see epel-release
echo "About to install ansible, epel, and telnet"
dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
dnf install -y telnet
dnf -y install ansible
  
##Install the Azure CLI using the following 3 steps:  
rpm --import https://packages.microsoft.com/keys/microsoft.asc

sh -c 'echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'

dnf install -y azure-cli

#Install Powershell in the following steps:
mkdir /home/$USR_NM/powershell-download
cd /home/$USR_NM/powershell-download
dnf install -y wget
wget https://github.com/PowerShell/PowerShell/releases/download/v7.1.3/powershell-7.1.3-1.rhel.7.x86_64.rpm
dnf install -y powershell-7.1.3-1.rhel.7.x86_64.rpm
#-->wget https://github.com/PowerShell/PowerShell/releases/download/v7.0.1/powershell-7.0.1-1.rhel.7.x86_64.rpm
#-->dnf install -y powershell-7.0.1-1.rhel.7.x86_64.rpm
#You should now be able to open powershell by typing "pwsh" in the command line

#-->echo "About to add extra libraries:"
wget -P /etc/yum.repos.d/ https://packages.efficios.com/repo.files/EfficiOS-RHEL7-x86-64.repo
rpmkeys --import https://packages.efficios.com/rhel/repo.key
curl https://packages.microsoft.com/config/rhel/8/prod.repo > ./microsoft-prod.repo
cp ./microsoft-prod.repo /etc/yum.repos.d/

## Download the agent to the VM:  
cd /home/$USR_NM
ls -al
mkdir agent-download
cd agent-download
wget https://vstsagentpackage.azureedge.net/agent/2.187.2/vsts-agent-linux-x64-2.187.2.tar.gz
tar xvf vsts-agent-linux-x64-2.187.2.tar.gz
#-->wget https://vstsagentpackage.azureedge.net/agent/2.171.1/vsts-agent-linux-x64-2.171.1.tar.gz
#-->tar xvf vsts-agent-linux-x64-2.171.1.tar.gz

chown -R $USR_NM:$USR_NM /home/$USR_NM/terraform-download
chown -R $USR_NM:$USR_NM /home/$USR_NM/agent-download
chown -R $USR_NM:$USR_NM /home/$USR_NM

echo "About to dnf clean all "
yum clean all

##Install the agent as a systemd service using the following 8 commands, which depend on the environment variables you just set in the line above this line.  
echo "About to switch to $USR_NM, then run many install commands.  "
su - $USR_NM << EOF
echo "User from whoami is: "
whoami
echo "About to login to az.  "
az login --service-principal -u '$AZ_CLIENT' -p '$AZ_PASS' --tenant '$AZ_TENANT'
echo "About to cd into agent-download directory.  "
cd /home/$USR_NM/agent-download/
echo "The server is: $AZ_SERVER "
echo "About to run the config sh script.  "
./config.sh --unattended --url $AZ_SERVER --auth pat --token $AZ_PAT --pool default --agent rhelBox --replace --acceptTeeEula
echo "About to run the install dependencies sh script.  "
sudo ./bin/installdependencies.sh
#Wait for the svc.sh file to be created before running it in subsequent steps.
echo "About to begin sleeping until the svc sh script has been found.  "
while [ ! -f /home/$USR_NM/agent-download/svc.sh ]; do sleep 1; done
echo "Finished sleeping because the svc sh file has now been found.  "
echo "About to svc sh install "
sudo ./svc.sh install
echo "About to svc sh start "
sudo ./svc.sh start
echo "About to svc sh status "
sudo ./svc.sh status
echo "About to e o f "
EOF

pip3 install requests
pip3 install pyyaml
pip3 install IPy

#Cause the ansible configuration to be owned by the agent user so that pipelines can change things like hosts file, etc.  
chown -R $USR_NM:$USR_NM /etc/ansible

echo "All done with cloud-init.  "

echo "--------------------------------------------------"
echo "About to dnf update"
dnf update -y
echo "Done with dnf update. "
echo "--------------------------------------------------"
echo "About to echo $USR_NM : "
echo $USR_NM
