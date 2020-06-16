
# Configure the Microsoft Azure Provider
provider "azurerm" {
    # The "feature" block is required for AzureRM provider 2.x. 
    # If you're using version 1.x, the "features" block is not allowed.
    version = "~>2.0"

    subscription_id = var.subscriptionId
    client_id       = var.clientId
    client_secret   = var.clientSecret
    tenant_id       = var.tenantId

    #The following features block will prevent Azure from retaining the key vault each time you run terraform destroy, provided purge is set to "true".  If remove the key_vault feature, make sure to retain an empty features {} block.
    features {
      key_vault {
        purge_soft_delete_on_destroy = true
        recover_soft_deleted_key_vaults = true
      }
    }
}

# Not required: currently used in conjuction with using icanhazip.com to determine local workstation external IP
provider "http" {}

