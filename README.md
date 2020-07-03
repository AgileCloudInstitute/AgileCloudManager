An automated system for orchestrating multi-cloud infrstructure as code using Terraform, Azure DevOps, and Azure Pipelines.  
  
# Assemble the Prerequisites:  
  
Prerequisites include:  
  
1.  [An Azure account](https://portal.azure.com/) with sufficient privileges such as subscription owner, Active Directory Contributor, Azure DevOps Organization Owner, etc.  
2.  Azure resources configured as described in the training that comes with this system, including an Azure DevOps organization, an Azure Application Registration, a Personal Access Token, etc.  
3.  A VM or container into which to clone this repository.  Here, we will start with our own [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example) in order to keep things simple.  That means you need to follow the instructions to instantiate `terraform-aws-simple-example` or something comparable in order to proceed.  
  
# Create the Infrastructure Orchestration System  
  
Once you have assembled the pre-requisites, do the following in order to use this repository:  
    
1.  Putty or `ssh` into the compute unit you created with [terraform-aws-simple-example](https://github.com/AgileCloudInstitute/terraform-aws-simple-example)  
2.  Navigate into directory into which to clone repos by typing  `cd cloned-repos`  
3.  Clone this repository by typing `git clone https://github.com/AgileCloudInstitute/agile-cloud-manager.git`  
4.  **SetupStepOne:**  Run [scripts/setupStepOne.sh](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/scripts/setupStepOne.sh) by typing the following commands:   
    
    cd agile-cloud-manager/scripts/  
    chmod +x setupStepOne.sh  
    sudo ./setupStepOne.sh  
    source /etc/bashrc  
    
5.  **SetupStepTwo:**  Enter the variables you assembled in the pre-requisite steps into [/home/aci-user/vars/agile-cloud-manager/enter-user-input-here-only.txt](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/move-to-directory-outside-app-path/enter-user-input-here-only.txt) file.  Note this can be done by replacing the file with pre-set values by some automation you create separately if you need to do this repeatedly.   
6.  **SetupStepThree:**  Automatically transfer the input variable values by running [setupStepThree.py](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/scripts/setupStepThree.py) while the terminal is still pointed to the same directory. And then run the script for setting local environment variables as follows:  
    
    python3 setupStepThree.py   
    chmod +x /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh  
    sudo /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh  
    source /etc/bashrc  
 
7.  Create the infrastructure foundation for Azure Pipelines including an Agent VM by running [pipeline-scripts/installPipelineSystemAndAgents](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/pipeline-scipts/installPipelineSystemAndAgents.py)   
    
    cd ../pipeline-scripts  
    python3 installPipelineSystemAndAgents.py  

8.  Validate that the infrastructure foundation was created by reading the console output, logging into [the Azure Portal](https://portal.azure.com/) to view the created elements, and puttying in to the Agent VM using the IP address you can find in the Azure Portal.   

# Create an Azure DevOps Project and import the sample repo and pipeline     
    
1.  Run the Pipeline task that calls the project-repo-build module using the `apply` command.  (Variables have been automatically imported for you for this demo.)   
    
    #Navigate to the same `pipeline-scripts` directory   
    az extension add --name azure-devops    
    python3 installProjectRepoBuild.py   
    
2.  Validate that the project, repository, and build have been created in the Azure DevOps portal.  And validate that the code was cloned into the new repository.      
3.  Copy the output variables into a text editor so that they can be used in subsequent scripted steps.  This will be automated later.    
4.  Trigger the build pipeline by making an inconsequential change to the README file for the `terraform-aws-simple-example` repo from within the Azure DevOps portal.  You are changing the copy that was just imported into your own Azure DevOps Organization, but you are only adding a couple spaces of white space to the README so that the functionality is not changed.  Then confirm that the build created the deployable artifact from the newly imported repository.    
        
# Destroy the Azure DevOps Project and its elements    
    
1.  Run the pipeline task that calls the project-repo-build module withe the `destroy` command.   
    
    #From the same `pipeline-scripts` directory    
    python3 destroyProjectRepoBuild.py   
    
2.  Validate that the project, repository, and build have been destroyed in the Azure Devops portal.        
    
# Destroy the Infrastructure Orchestration System    
    
1.  Log in the the VM from which you ran the agile-cloud-manager program to create the Agile Cloud Manager instance.  If you are continuing directly from the creation steps described above, you can do this from within the same Putty or SSH session as above.      
2.  Point the terminal to the directory containing destroyPipelineSystemAndAgents.py and then run destroyPipelineSystemAndAgents.py by typing the following:    
    
    cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scripts   
    python3 destroyPipelineSystemAndAgents.py    
    
3.  Validate that the infrastructure has been destroyed by examining the console output that printed while the destroyPipelineSystemAndAgents.py was running, by examining the Azure Portal see the infrastructure disappear, and by validating in the Azure DevOps Organization that the agent has moved offline.    
    
