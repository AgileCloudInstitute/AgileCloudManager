An automated system for orchestrating multi-cloud infrstructure as code using Terraform, Azure DevOps, and Azure Pipelines.  
  
#Assemble the Prerequisites:  
  
Prerequisites include:  
  
1.  [An Azure account](https://portal.azure.com/) with sufficient privileges such as subscription owner, Active Directory Contributor, Azure DevOps Organization Owner, etc.  
2.  Azure resources configured as described in the training that comes with this system, including an Azure DevOps organization, an Azure Application Registration, a Personal Access Token, etc.  
3.  A VM or container into which to clone this repository.  Here, we will start with our own [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example) in order to keep things simple.  That means you need to follow the instructions to instantiate `terraform-aws-simple-example` or something comparable in order to proceed.  
  
#Create the Infrastructure Orchestration System  
  
Once you have assembled the pre-requisites, do the following in order to use this repository:  
    
1.  Putty or `ssh` into the compute unit you created with [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example)  
2.  Navigate into directory into which to clone repos by typing  `cd cloned-repos`  
3.  Clone this repository by typing `git clone https://github.com/AgileCloudInstitute/agile-cloud-manager.git`  
4.  Run [scripts/setup.sh](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/scripts/setup.sh)  
    
    cd scripts  
    chmod +x setup.sh  
    sudo ./setup.sh  
    
5.  Enter the variables you assembled in the pre-requisite steps into [/home/aci-user/vars/agile-cloud-manager/enter-user-input-here-only.txt](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/move-to-directory-outside-app-path/enter-user-input-here-only.txt) file.  Note this can be done by replacing the file with pre-set values by some automation you create separately if you need to do this repeatedly.   
6.  Automatically transfer the input variable values by running [importTheInputVariables.py](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/scripts/importTheInputVariables.py)   
    
    cd scripts
    python3.7 importTheInputVariables.py  

7.  Create the infrastructure foundation for Azure Pipelines including an Agent VM by running [pipeline-scripts/installPipelineSystemAndAgents](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/pipeline-scipts/installPipelineSystemAndAgents.py)   
    
    cd pipeline-scripts  
    python3.7 installPipelineSystemAndAgents.py  

8.  Validate that the infrastructure foundation was created by reading the console output, logging into [the Azure Portal](https://portal.azure.com/) to view the created elements, and puttying in to the Agent VM using the IP address you can find in the Azure Portal.   

9.  Create an Azure DevOps Project and import the sample repo and pipeline by... 
  
#Destroy the Azure DevOps Project and its elements  
  
1.  ...  
2.  ...  

#Destroy the Infrastructure Orchestration System  
  
