#The terraform backend will be located in this storage container, which will be placed in the imported storage account.

resource "azurerm_storage_account" "terraformBknd" {
  name                     = var.storageAccountNameTerraformBackend
  resource_group_name      = var.pipeResourceGroupName
  location                 = var.pipeResourceGroupRegion
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
    #CHANGE THE FOLLOWING TO "Deny" FOR PRODUCTION.
    default_action             = "Allow"
    #ip_rules                   = [var.myRemoteIP, azurerm_public_ip.myterraformpublicip.ip_address]
    virtual_network_subnet_ids = [var.pipeSubnetId]
  }

  tags = {
    environment = "dev"
  }
}


######Each Terraform Backend will require its own storage container as follows:
resource "azurerm_storage_container" "terraformBknd" {
  name                  = var.storageContainerNameTerraformBackend
  storage_account_name  = azurerm_storage_account.terraformBknd.name
  #Lock down the following line when this is ready to be made more secure.  See this link: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-manage-access-to-resources?tabs=dotnet
  container_access_type = "container"
}

#resource "azurerm_storage_container" "terraformBkndAZDO" {
#  name                  = "terraform-backend-azdo"
#  storage_account_name  = azurerm_storage_account.terraformBknd.name
#  #Lock down the following line when this is ready to be made more secure.  See this link: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-manage-access-to-resources?tabs=dotnet
#  container_access_type = "container"
#}
