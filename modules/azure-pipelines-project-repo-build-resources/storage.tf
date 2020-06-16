#The terraform backend will be located in this storage container, which will be placed in the imported storage account.

data "azurerm_storage_account" "terraform-backend" {
  name                = var.storageAccountNameTerraformBackend
  resource_group_name = var.pipeResourceGroupName
}

######Each Terraform Backend will require its own storage container as follows:
resource "azurerm_storage_container" "terraformBknd" {
  name                  = var.storageContainerNameTerraformBackend
  storage_account_name  = data.azurerm_storage_account.terraform-backend.name
  #Lock down the following line when this is ready to be made more secure.  See this link: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-manage-access-to-resources?tabs=dotnet
  container_access_type = "container"
}

#resource "azurerm_storage_container" "terraformBkndAZDO" {
#  name                  = "terraform-backend-azdo"
#  storage_account_name  = azurerm_storage_account.terraformBknd.name
#  #Lock down the following line when this is ready to be made more secure.  See this link: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-manage-access-to-resources?tabs=dotnet
#  container_access_type = "container"
#}
