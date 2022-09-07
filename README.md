An automated system for orchestration and project management for multi-cloud infrstructure as code leveraging widely used open source tools.    
  
Run a demo of this system by completing the following simple steps:  
  
# STEP ONE: Assemble the Prerequisites:  
  
Prerequisites include:  
  
1.  [An Azure account](https://portal.azure.com/) with sufficient privileges such as subscription owner, Active Directory Contributor, Azure DevOps Organization Owner, etc.  
2.  Azure resources configured as described in the training that comes with this system, including an Azure DevOps organization, an Azure Application Registration, a Personal Access Token, etc.  
3.  [An AWS account]() with sufficient privilates, which here for demonstration purposes we will assume is the account root.
4.  A compute instance such as a devbox, VM, or container into which to clone this repository.    
  
Note that you will be able to restrict ammount permissions on your own separately.  The root and owner roles for this demo are just to simplify the demonstration process for new users.  
   
# STEP TWO: Clone this repository and run setup 
  
Open a command prompt in the compute instance into which you will clone this repository, and do the following:  
  
    cd <directory-into-which-repo-will-be-cloned>
    git clone -b dev https://github.com/AgileCloudInstitute/agile-cloud-manager.git
    cd agile-cloud-manager\controller
    python3 acm.py setup on
  
If the preceding `python3 acm.py setup on` command told you that you are missing any dependencies, then install those dependencies.  Otherwise, you should be ready to proceed with these instructions.  
  
# STEP THREE: Add secrets  
  
Populate the secrets for Azure in ``, and for AWS in ``.  
  
# STEP FOUR: Run the ACM Creation Workflow commands  
  
Make sure that the Azure version is installed as `infrastructureConfig.yaml`.  
  
Type the following commands to get the demo up and running:  
  
    python3 acm.py admin on
    python3 acm.py foundation on
    python3 acm.py system on
    python3 acm.py project on
    python3 acm.py pipeline on
  
Manually confirm that everything works as intended in [the Azure Portal](https://portal.azure.com/)

# STEP FIVE: Destroy the ACM Demo  
  
Manually destroy the Release definition in [the Azure Portal](https://portal.azure.com/) .  We are leaving release definition destruction as a manual step for security purposes, to protect your release logs.  
  
Type the following commands to destroy the rest of the demo infrastructure that you just created.  
  
    python3 acm.py project off
    python3 acm.py system off
    python3 acm.py foundation off
    python3 acm.py admin off
  
# STEP SIX: Destroy Secrets
  
Remember to destroy the secrets that you populated into `` for Azure and into `` for AWS.  
