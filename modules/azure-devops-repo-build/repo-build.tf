#the azure devops repository and build

resource "azuredevops_git_repository" "repository" {
  project_id = azuredevops_project.project.id
  name = var.repoName
  initialization {
    init_type = "Uninitialized"
  }
  provisioner "local-exec" {
    command = "az repos import create --git-source-url \"${var.sourceRepo}\" --repository \"${azuredevops_git_repository.repository.name}\" --organization \"${var.azdoOrgServiceURL}\" --project \"${azuredevops_project.project.project_name}\""
    working_dir = "/home/agile-cloud/cloned-repos/agile-cloud-manager/pipeline-tasks/"
  }
}

resource "azuredevops_build_definition" "build" {
  project_id = azuredevops_project.project.id
  name       = var.buildName
  ci_trigger {
    use_yaml = true
  }

  repository {
    repo_type   = "TfsGit"
    repo_id     = azuredevops_git_repository.repository.id
    yml_path    = "azure-pipelines.yml"
  }
}
