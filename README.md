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
    
3.  **Import Config Variables:**  Enter the variables you assembled in the pre-requisite steps into a new file you will create in `/home/aci-user/staging/enter-user-input-here-only.txt` which follows the exact list of variables and syntax given in [this template file from the repository](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/move-to-directory-outside-app-path/enter-user-input-here-only.txt) .  
  
    vi /home/aci-user/staging/enter-user-input-here-only.txt
    #Then enter the values for each listed variable.  
    #Then save the file.  
    #Note this can be done by some automation you create separately if you need to do this repeatedly.   
  
5.  **Run the Setup Script:**  
    
    cd /home/aci-user/cloned-repos/agile-cloud-manager/scripts/
    sudo python3 setupStepThree.py   
    source /etc/bashrc  
    
#  Create the foundation of the infrastructure for the Azure Pipelines implementation   
    
1.  Create the infrastructure foundation for Azure Pipelines including an Agent VM by running [pipeline-scripts/installPipelineSystemAndAgents](https://github.com/AgileCloudInstitute/agile-cloud-manager/blob/master/pipeline-scipts/installPipelineSystemAndAgents.py)   
    
    cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scripts  
    python3 installPipelineSystemAndAgents.py  
  
2.  Validate that the infrastructure foundation was created by reading the console output, logging into [the Azure Portal](https://portal.azure.com/) to view the created elements, and puttying in to the Agent VM using the IP address you can find in the Azure Portal.   

# Create an Azure DevOps Project and import the sample repo and pipeline     
    
1.  Run the Pipeline task that calls the project-repo-build module using the `apply` command.  (Variables have been automatically imported for you for this demo.)   
    
    #Navigate to the same `pipeline-scripts` directory if you are not already there  
    cd /home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scripts    
    python3 installProjectRepoBuild.py   
    
2.  Validate that the project, repository, and build have been created in the Azure DevOps portal.  And validate that the code was cloned into the new repository.      
    
3.  Trigger the build pipeline by making an inconsequential change to the README file for the `terraform-aws-simple-example` repo from within the Azure DevOps portal.  You are changing the copy that was just imported into your own Azure DevOps Organization, but you are only adding a couple spaces of white space to the README so that the functionality is not changed.  Then confirm that the build created the deployable artifact from the newly imported repository.    
        
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
    
