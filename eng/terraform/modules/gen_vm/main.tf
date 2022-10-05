
locals {
  base_vm_name = "${var.prefix}-vm-${var.application}"
  short_prefix = substr(var.prefix, 0, 17)
  short_vm_name = substr(local.base_vm_name, 0, 15)
}
data "azurerm_resource_group" "base_rg" {
  name     = var.base_rg_name
}

data "azurerm_virtual_network" "base_vnet" {
  name                = var.base_vnet
  resource_group_name = data.azurerm_resource_group.base_rg.name
}

data "azurerm_subnet" "base_subnet" {
  name                 = var.base_subnet
  virtual_network_name = data.azurerm_virtual_network.base_vnet.name
  resource_group_name  = data.azurerm_resource_group.base_rg.name
}
resource "random_id" "suffix" {
  byte_length = 3
}

resource "azurerm_public_ip" "sql_pip" {
  name                = "${local.base_vm_name}-ip"
  location            = var.location
  resource_group_name = data.azurerm_resource_group.base_rg.name
  allocation_method   = "Dynamic"
}


resource "azurerm_network_security_group" "sql_sg" {
  name                = "${local.base_vm_name}-nsg"
  location            = var.location
  resource_group_name = data.azurerm_resource_group.base_rg.name
}

resource "azurerm_network_security_rule" "RDPRule" {
  name                        = "RDPRule"
  resource_group_name         = data.azurerm_resource_group.base_rg.name
  priority                    = 1000
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = 3389
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  network_security_group_name = azurerm_network_security_group.sql_sg.name
}

resource "azurerm_network_interface" "sql_nic" {
  name                = "${local.short_prefix}-${random_id.suffix.hex}"
  location            = var.location
  resource_group_name = data.azurerm_resource_group.base_rg.name

  ip_configuration {
    name                          = "sql_ip_config"
    subnet_id                     = data.azurerm_subnet.base_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.sql_pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "example" {
  network_interface_id      = azurerm_network_interface.sql_nic.id
  network_security_group_id = azurerm_network_security_group.sql_sg.id
}
resource "random_string" "ran_str" {
  length           = 32
  special          = false
  upper            = false
}
resource "azurerm_virtual_machine" "sql_vm_vm" {
  name                  = local.base_vm_name
  location              = var.location
  resource_group_name   = data.azurerm_resource_group.base_rg.name
  network_interface_ids = [azurerm_network_interface.sql_nic.id]
  vm_size               = "Standard_DS11_v2"

  storage_image_reference {
    publisher = var.sql_server_publisher
    offer     = var.sql_server_offer
    sku       = var.sql_server_sku
    version   = "latest"
  }

  storage_os_disk {
    name              = "${var.prefix}-OSDisk_1_${random_string.ran_str.result}"
    caching           = "ReadOnly"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_data_disk {
    lun = 0
    name              = "${local.base_vm_name}_DataDisk_0"
    caching           = "ReadOnly"
    create_option     = "attach"
    managed_disk_type = "Premium_LRS"
    disk_size_gb      = 8
  }

  os_profile {
    computer_name  = local.short_vm_name
    admin_username = var.admin_username
    admin_password = var.admin_password
  }

  os_profile_windows_config {
    provision_vm_agent        = true
    enable_automatic_upgrades = true
  }
}

resource "azurerm_mssql_virtual_machine" "sql_vm" {
  virtual_machine_id = azurerm_virtual_machine.sql_vm_vm.id
  sql_license_type   = "PAYG"
  storage_configuration {
    disk_type = "NEW"
    storage_workload_type = "OLTP"
    data_settings {
        default_file_path = "F:\\data"
        luns = [0]
      }
    log_settings {
        default_file_path = "F:\\log"
        luns = [0]
      }
    temp_db_settings  {
        default_file_path = "F:\\tempDb"
        luns = [0]
    }
  }
}