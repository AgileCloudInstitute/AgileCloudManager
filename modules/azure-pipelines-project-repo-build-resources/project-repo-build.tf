#The Azure DevOps resources, including a project, a repository, and a build.

resource "azuredevops_project" "project" {
  project_name       = "Sample Project"
  visibility         = "private"
  version_control    = "Git"
  work_item_template = "Agile"
}

resource "azuredevops_git_repository" "repository" {
  project_id = azuredevops_project.project.id
  name = "my-simple-repo"
  initialization {
    init_type = "Uninitialized"
  }
  provisioner "local-exec" {
    command = "az repos import create --git-source-url \"${var.sourceRepo}\" --repository \"${azuredevops_git_repository.repository.name}\" --organization \"${var.azdoOrgServiceURL}\" --project \"${azuredevops_project.project.project_name}\""
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
