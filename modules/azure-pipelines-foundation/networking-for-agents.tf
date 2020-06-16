
resource "azurerm_virtual_network" "pipelines" {
  name                = "pipelineVirtnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.pipelines.location
  resource_group_name = azurerm_resource_group.pipelines.name
}

resource "azurerm_subnet" "pipelines" {
  name                 = "pipelineSubnet"
  resource_group_name  = azurerm_resource_group.pipelines.name
  virtual_network_name = azurerm_virtual_network.pipelines.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Sql", "Microsoft.Storage", "Microsoft.KeyVault"]
}

# Create public IPs
resource "azurerm_public_ip" "myterraformpublicip" {
    name                = "myPublicIP"
    location            = azurerm_resource_group.pipelines.location
    resource_group_name = azurerm_resource_group.pipelines.name
    allocation_method   = "Dynamic"

    tags = {
        environment = "Terraform Demo"
    }
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "myterraformnsg" {
    name                = "myNetworkSecurityGroup"
    location            = azurerm_resource_group.pipelines.location
    resource_group_name = azurerm_resource_group.pipelines.name
    
    security_rule {
        name                       = "SSH"
        priority                   = 1001
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }

    tags = {
        environment = "Terraform Demo"
    }
}

# Create network interface
resource "azurerm_network_interface" "myterraformnic" {
    name                      = "myNIC"
    location                  = azurerm_resource_group.pipelines.location
    resource_group_name       = azurerm_resource_group.pipelines.name

    ip_configuration {
        name                          = "myNicConfiguration"
        subnet_id                     = azurerm_subnet.pipelines.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.myterraformpublicip.id
    }

    tags = {
        environment = "Terraform Demo"
    }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "example" {
    network_interface_id      = azurerm_network_interface.myterraformnic.id
    network_security_group_id = azurerm_network_security_group.myterraformnsg.id
}

