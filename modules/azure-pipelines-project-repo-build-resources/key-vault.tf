

data "azurerm_key_vault" "pipeKeyVault" {
  name                = var.pipeKeyVaultName
  resource_group_name = var.pipeResourceGroupName
}


resource "azurerm_key_vault_access_policy" "azdo-project-access-key-vault" {
  key_vault_id = data.azurerm_key_vault.pipeKeyVault.id
  #Test of a second access_policy.  The following block contains the ID of the AzureDevops project with which this release is associated, so this release can access the key vault.  
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = azuredevops_project.project.id
  certificate_permissions = [ "create", "delete", "deleteissuers", "get", "getissuers", "import", "list", "listissuers", "managecontacts", "manageissuers", "setissuers", "update", ]
  key_permissions = [ "backup", "create", "decrypt", "delete", "encrypt", "get", "import", "list", "purge", "recover", "restore", "sign", "unwrapKey", "update", "verify", "wrapKey", ]
  secret_permissions = [ "backup", "delete", "get", "list", "purge", "recover", "restore", "set", ]
  storage_permissions = [ "get", ]
}

resource "azurerm_key_vault_secret" "awsPublicAccessKey" {
  name         = "-aws-public-access-key"
  value        = var.awsPublicAccessKey
  key_vault_id = data.azurerm_key_vault.pipeKeyVault.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.azdo-project-access-key-vault]
}

resource "azurerm_key_vault_secret" "awsSecretAccessKey" {
  name         = "-aws-secret-access-key"
  value        = var.awsSecretAccessKey
  key_vault_id = data.azurerm_key_vault.pipeKeyVault.id
  tags = { environment = "Testing" }
  depends_on = [azurerm_key_vault_access_policy.azdo-project-access-key-vault]
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

