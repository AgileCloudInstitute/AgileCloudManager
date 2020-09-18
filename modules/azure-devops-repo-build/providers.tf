
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
    features { }
}

provider "azuredevops" {
  version = ">= 0.0.1"
  personal_access_token = var.azdoOrgPAT
  org_service_url = var.azdoOrgServiceURL
}
