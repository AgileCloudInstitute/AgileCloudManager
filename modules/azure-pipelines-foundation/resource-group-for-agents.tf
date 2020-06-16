resource "azurerm_resource_group" "pipelines" {
  name     = "pipeline-resources"
  location = var.pipeAzureRegion
}
