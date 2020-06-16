resource "azurerm_storage_account" "terraformBknd" {
  name                = var.storageAccountNameTerraformBackend
  resource_group_name = azurerm_resource_group.pipelines.name

  location                 = azurerm_resource_group.pipelines.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
#CHANGE THE FOLLOWING TO "Deny" FOR PRODUCTION.
    default_action             = "Allow"
    #ip_rules                   = [var.myRemoteIP, azurerm_public_ip.myterraformpublicip.ip_address]
    virtual_network_subnet_ids = [azurerm_subnet.pipelines.id]
  }

  tags = {
    environment = "dev"
  }
}

# Create storage account for boot diagnostics
resource "azurerm_storage_account" "mystorageaccount" {
    name                        = "diag${random_id.randomId.hex}"
    location                    = azurerm_resource_group.pipelines.location
    resource_group_name         = azurerm_resource_group.pipelines.name
    account_tier                = "Standard"
    account_replication_type    = "LRS"

    tags = {
        environment = "Terraform Demo"
    }
}

# Generate random text for a unique storage account name
resource "random_id" "randomId" {
    keepers = {
        # Generate a new ID only when a new resource group is defined
        resource_group = azurerm_resource_group.pipelines.name
    }
    
    byte_length = 8
}
