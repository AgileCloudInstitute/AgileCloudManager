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
  provisioner "local-exec" {
    command = "ls -al"
    #command = "ls -al && B64_PAT=$(echo \"pat:$AZ_PAT\" | base64) && git remote set-url origin ${azuredevops_git_repository.repository.ssh_url} && git -u http.extraHeader=\"Authorization: Bearer ${B64_PAT}\" push ${azuredevops_git_repository.repository.ssh_url} --al"
    working_dir = "/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-scipts/" 
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
    #repo_name     = azuredevops_git_repository.repository.id
    #branch_name = azuredevops_git_repository.repository.default_branch
    yml_path    = "azure-pipelines.yml"
  }

}
