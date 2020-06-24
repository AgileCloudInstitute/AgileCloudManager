#The Azure DevOps resources, including a project, a repository, and a build.

resource "azuredevops_project" "project" {
  project_name       = "Sample Project"
  visibility         = "private"
  version_control    = "Git"
  work_item_template = "Agile"
}

resource "azuredevops_git_repository" "repository" {
  project_id = azuredevops_project.project.id
  name       = "my-simple-repo"
  initialization {
    init_type = "Clean"
  }
  provisioner "local-exec" {
    #Use the following to set up git bash:  https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops&tabs=current-page  
    #PAT example very easy:  https://stackoverflow.com/questions/53106546/cannot-clone-git-from-azure-devops-using-pat
    #command = "dir && git remote set-url origin ${azuredevops_git_repository.repository.remote_url} && git push -u origin --all"
    #USE THIS ONE: command = "dir && git remote set-url origin ${azuredevops_git_repository.repository.ssh_url} && git push -u origin --all"
    # git remote -v  will determine if the remote is using ssh keys.  Though below make sure you are referencing the correct remote to return valid information.  
    command = "ls -al && git remote set-url origin ${azuredevops_git_repository.repository.remote_url} && git remote -v"
    working_dir = "/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scipts/tmpRepoStorage/terraform-aws-simple-example/" 
  }  

}

resource "azuredevops_build_definition" "build" {
  project_id = azuredevops_project.project.id
  name       = "Sample Build Definition"
  
  ci_trigger {
    use_yaml = true
  }

  repository {
    repo_type   = "TfsGit"
    repo_id     = azuredevops_git_repository.repository.id
    repo_name     = azuredevops_git_repository.repository.id
    #branch_name = azuredevops_git_repository.repository.default_branch
    yml_path    = "azure-pipelines.yml"
  }

}
