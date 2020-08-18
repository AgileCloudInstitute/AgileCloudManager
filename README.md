An automated system for orchestrating multi-cloud infrstructure as code using Terraform, Azure DevOps, and Azure Pipelines.  
  
# Assemble the Prerequisites:  
  
Prerequisites include:  
  
1.  [An Azure account](https://portal.azure.com/) with sufficient privileges such as subscription owner, Active Directory Contributor, Azure DevOps Organization Owner, etc.  
2.  Azure resources configured as described in the training that comes with this system, including an Azure DevOps organization, an Azure Application Registration, a Personal Access Token, etc.  
3.  A VM or container into which to clone this repository.  Here, we will start with our own [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example) in order to keep things simple.  That means you need to follow the instructions to instantiate `terraform-aws-simple-example` or something comparable in order to proceed.  
  
# Create the Infrastructure Orchestration System  
  
Once you have assembled the pre-requisites, do the following in order to use this repository:  
    
1.  **Log In To Dev Server:**  Putty or `ssh` into the compute unit you created with [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example)    
    
2.  **Clone this Repository:**  Navigate into the target directory and clone the repo by typing:    
    
      cd cloned-repos    
      git clone https://github.com/AgileCloudInstitute/agile-cloud-manager.git    
    
3.  **Import Config Variables:**  Enter the variables you assembled in the pre-requisite steps into a new file you will create in `/home/aci-user/staging/enter-user-input-here-only.yaml` which follows the exact list of variables and syntax given in [this template file from the repository](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/move-to-directory-outside-app-path/enter-user-input-here-only.yaml) .  
  
      vi /home/aci-user/staging/enter-user-input-here-only.yaml       
      #Then enter the values for each listed variable.    
      #Then save the file.    
      #Note this can be done by some automation you create separately if you need to do this repeatedly.     
  
5.  **Run the Setup Script:**  
    
      cd /home/aci-user/cloned-repos/agile-cloud-manager/setup/      
      sudo python3 setup.py      
      source /etc/bashrc     
    
#  Create the foundation of the infrastructure for the Azure Pipelines implementation   
    
1.  Create the infrastructure foundation for Azure Pipelines including an Agent VM by running [pipeline-tasks/installPipelineSystemAndAgents.py](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/pipeline-tasks/installPipelineSystemAndAgents.py)   
    
      cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks     
      python3 installPipelineSystemAndAgents.py     
  
2.  Validate that the infrastructure foundation was created by reading the console output, logging into [the Azure Portal](https://portal.azure.com/) to view the created elements, and puttying in to the Agent VM using the IP address you can find in the Azure Portal.   

# Create an Azure DevOps Project and import the sample repo and pipeline     
    
1.  Run the Pipeline task that calls the project-repo-build module using the `apply` command.  (Variables have been automatically imported for you for this demo.)   
    
      #Navigate to the same `pipeline-tasks` directory if you are not already there    
      cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks      
      python3 installProjectRepoBuild.py     
    
2.  Validate that the project, repository, and build have been created in the Azure DevOps portal.  And validate that the code was cloned into the new repository.      
    
      #Manually trigger a build by navigating into one of the files in the `terraform-aws-simple-example` Azure Repo that was just imported and adding one character of white space and then clicking the "commit" button.  
      #Confirm that the build was triggered by navigating to the Pipelines control panel and seeing that a build was just run.  
        
# Create two Release Definitions
        
      #Navigate to the same `pipeline-tasks` directory if you are not already there        
      #Type the following two commands to create two Release Definitions, noting that the yaml files are in the `release-definitions/yaml-definition-files/` directory.        
      python3 constructReleaseDef.py createTerraformSimpleAWS.yaml       
      python3 constructReleaseDef.py destroyTerraformSimpleAWS.yaml       
      #Confirm in the console that each of the commands produced a 200 HTTP response code.  Then navigate to the Azure Devops Portal to view the Release Definitions.  
      #Manually Trigger the "Create Terraform AWS Simple Example Release" in the Azure Devops Portal and confirm that the infrastructure was created in AWS.  Note that you must click the manual "Deploy" button in the release the way the definition is currently configured.        
      #Then Manually trigger the "Destroy Terraform AWS Simple Example Release" in the Azure Devops Portal and confirm that the same infrastructure was destroyed in AWS. Again note that you must manually click on the "Deploy" button on the release the way the definition is currently configured.         
  
# Delete both Release Definitions  
  
      #In the Azure Devops Portal, manually delete both of the two Release Definitions that you created in the preceding step.  This is necessary before deleting the Project, Repository, and Build objects in the next step.        
        
# Destroy the Azure DevOps Project and its elements    
    
1.  Run the pipeline task that calls the project-repo-build module withe the `destroy` command.   
    
      #From the same `pipeline-tasks` directory      
      python3 destroyProjectRepoBuild.py     
    
2.  Validate that the project, repository, and build have been destroyed in the Azure Devops portal.        
    
# Destroy the Infrastructure Orchestration System    
    
1.  Log in the the VM from which you ran the agile-cloud-manager program to create the Agile Cloud Manager instance.  If you are continuing directly from the creation steps described above, you can do this from within the same Putty or SSH session as above.      
2.  Point the terminal to the directory containing destroyPipelineSystemAndAgents.py and then run destroyPipelineSystemAndAgents.py by typing the following:    
    
      cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks     
      python3 destroyPipelineSystemAndAgents.py      
    
3.  Validate that the infrastructure has been destroyed by examining the console output that printed while the destroyPipelineSystemAndAgents.py was running, by examining the Azure Portal see the infrastructure disappear, and by validating in the Azure DevOps Organization that the agent has moved offline.    
    
