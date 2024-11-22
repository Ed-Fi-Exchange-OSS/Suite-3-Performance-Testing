/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */
locals {
  base_vm_name = "${var.prefix}-${var.application}"
}

resource "azurerm_public_ip" "vm_pip" {
  name                = "${local.base_vm_name}-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "vm_nic" {
  name                = "${local.base_vm_name}-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "${var.application}_ip_config"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_pip.id
  }
}
resource "azurerm_network_interface_security_group_association" "vm_nsg_assoc" {
  network_interface_id      = azurerm_network_interface.vm_nic.id
  network_security_group_id = var.vm_sg_id
}
resource "azurerm_windows_virtual_machine" "vm" {
  name                = "${local.base_vm_name}-vm"
  computer_name       = var.computer_name
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = var.vm_size
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  network_interface_ids = [
    azurerm_network_interface.vm_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    #disk_size_gb         = var.os_disk_size
  }

  source_image_reference {
    publisher = var.vm_image_publisher
    offer     = var.vm_image_offer
    sku       = var.vm_image_sku
    version   = "latest"
  }
}
resource "azurerm_managed_disk" "vm_data" {
  name                 = "${local.base_vm_name}-VM_Data_0"
  location             = var.location
  resource_group_name  = var.resource_group_name
  storage_account_type = "StandardSSD_LRS"
  create_option        = "Empty"
  disk_size_gb         = var.data_disk_size
}
resource "azurerm_virtual_machine_data_disk_attachment" "vm_data" {
  managed_disk_id    = azurerm_managed_disk.vm_data.id
  virtual_machine_id = azurerm_windows_virtual_machine.vm.id
  lun                = "1"
  caching            = "ReadOnly"
}

# Shutdown at 7:00pm daily
resource "azurerm_dev_test_global_vm_shutdown_schedule" "shutdown_7pm" {
  virtual_machine_id = azurerm_windows_virtual_machine.vm.id
  location           = var.location
  enabled            = true

  daily_recurrence_time = "1900"
  timezone              = "Central Standard Time"
  notification_settings {
    enabled = false
  }
}
