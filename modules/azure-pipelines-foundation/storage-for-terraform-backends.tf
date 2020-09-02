#The terraform backend will be located in this storage container, which will be placed in the imported storage account.	
#Another approach here: https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage	

resource "azurerm_storage_account" "terraformBknd" {	
  name                     = var.storageAccountNameTerraformBackend	
  resource_group_name      = azurerm_resource_group.pipelines.name	
  location                 = azurerm_resource_group.pipelines.location	
  account_tier             = "Standard"	
  account_replication_type = "LRS"	
  allow_blob_public_access = false	

  network_rules {	
    default_action             = "Deny"	
    virtual_network_subnet_ids = [azurerm_subnet.pipelines.id]	
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
  depends_on = [azurerm_storage_account.terraformBknd]	
}
