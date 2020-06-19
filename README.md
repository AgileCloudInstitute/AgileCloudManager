An automated system for orchestrating multi-cloud infrstructure as code using Terraform, Azure DevOps, and Azure Pipelines.  

Prerequisites include:  
  
1.  [An Azure account](https://portal.azure.com/) with sufficient privileges such as subscription owner, Active Directory Contributor, Azure DevOps Organization Owner, etc.  
2.  Azure resources configured as described in the training that comes with this system, including an Azure DevOps organization, an Azure Application Registration, a Personal Access Token, etc.  
3.  A VM or container into which to clone this repository.  Here, we will start with our own [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example) in order to keep things simple.  That means you need to follow the instructions to instantiate `terraform-aws-simple-example` or something comparable in order to proceed.  

Once you have assembled the pre-requisites, do the following in order to use this repository:  
  
1.  Putty or `ssh` into the compute unit you created with [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example)  
2.  Navigate into directory into which to clone repos by typing  `cd cloned-repos`  
3.  Clone this repository by typing `https://github.com/AgileCloudInstitute/agile-cloud-manager.git`  
4.  Run [scripts/setup.sh](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/scripts/setup.sh)
5.  Enter the variables you assembled in the pre-requisite steps into the appropriate variable files that were just moved to `/home/aci-user/vars/agile-cloud-manager/`
6.  Run [pipeline-scripts/installPipelineSystemAndAgents]{https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/pipeline-scipts/installPipelineSystemAndAgents.py}  
7.  ... 
  
