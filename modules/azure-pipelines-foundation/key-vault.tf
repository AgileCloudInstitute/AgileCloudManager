
## #Use this data source to access the configuration of the azurerm provider, which you configured separately in this module.
## data "azurerm_client_config" "current" {}

#Now create a key vault as an experiment.  The following will need to be matured later:
resource "azurerm_key_vault" "infraPipes" {
  name                        = "testvlt789"
  location                    = azurerm_resource_group.pipelines.location
  resource_group_name         = azurerm_resource_group.pipelines.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_enabled         = true
  purge_protection_enabled    = false
  sku_name = "standard"

  network_acls {
##CHANGE THE FOLLOWING LINE TO "Deny" FOR PRODUCTION.
    default_action = "Allow"
    bypass         = "AzureServices"
    ip_rules       = [local.admin-external-cidr]
    virtual_network_subnet_ids = [azurerm_subnet.pipelines.id]
  }

  tags = { environment = "Testing" }
}

#Use this data source to access the configuration of the azurerm provider, which you configured above:
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_access_policy" "userCreatedSP" {
  key_vault_id = azurerm_key_vault.infraPipes.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_client_config.current.object_id
  certificate_permissions = [ "create", "delete", "deleteissuers", "get", "getissuers", "import", "list", "listissuers", "managecontacts", "manageissuers", "setissuers", "update", ]
  key_permissions = [ "backup", "create", "decrypt", "delete", "encrypt", "get", "import", "list", "purge", "recover", "restore", "sign", "unwrapKey", "update", "verify", "wrapKey", ]
  secret_permissions = [ "backup", "delete", "get", "list", "purge", "recover", "restore", "set", ]
  storage_permissions = [ "get", ]
}


#Now create secrets and attach to the new key vault.
resource "azurerm_key_vault_secret" "subscriptionId" {
  name         = "subscription-id"
  value        = data.azurerm_client_config.current.subscription_id
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

resource "azurerm_key_vault_secret" "tenantId" {
  name         = "tenant-id"
  value        = var.tenantId
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

resource "azurerm_key_vault_secret" "clientId" {
  name         = "client-id"
  value        = var.clientId
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

resource "azurerm_key_vault_secret" "clientSecret" {
  name         = "client-secret"
  value        = var.clientSecret
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

resource "azurerm_key_vault_secret" "storageAccountNameTerraformBackend" {
  name         = "storageAccountNameTerraformBackend"
  value        = var.storageAccountNameTerraformBackend
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

resource "azurerm_key_vault_secret" "terraBackendKey" {
  name         = "terra-backend-key"
  value        = azurerm_storage_account.terraformBknd.primary_access_key
  key_vault_id = azurerm_key_vault.infraPipes.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.userCreatedSP]
}

