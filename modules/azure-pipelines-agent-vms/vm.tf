


# Create virtual machine
resource "azurerm_linux_virtual_machine" "myterraformvm" {
    name                  = "pipelineAgentVM"
    location              = data.azurerm_resource_group.pipeline-resources.location
    resource_group_name   = data.azurerm_resource_group.pipeline-resources.name
    network_interface_ids = [data.azurerm_network_interface.myterraformnic.id]
    size                  = "Standard_DS1_v2"

    os_disk {
        name              = "myOsDisk"
        caching           = "ReadWrite"
        storage_account_type = "Premium_LRS"
    }

    source_image_reference {
        publisher = "RedHat"
        offer     = "RHEL"
        #sku       = "7-RAW-CI"
        #version   = "7.6.2019072418"
        sku       = "8.2"
        version   = "8.2.2020050811"
    }

    computer_name  = "myvm"
    admin_username = var.adminUser
    admin_password = var.adminPwd
    disable_password_authentication = false
    custom_data = base64encode(file(var.pathToCloudInitScript))

    boot_diagnostics {
        storage_account_uri = data.azurerm_storage_account.mystorageaccount.primary_blob_endpoint
    }

    tags = {
        environment = "Terraform Demo"
    }
}
