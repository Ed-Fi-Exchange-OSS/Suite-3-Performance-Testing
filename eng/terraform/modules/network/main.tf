/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */
provider "azurerm" {
  features {}
  skip_provider_registration = "true"
}
resource "azurerm_network_security_group" "vm_sg" {
  name                = "${var.prefix}-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name
}
resource "azurerm_network_security_rule" "rdp_rule" {
  name                        = "RDPRule"
  resource_group_name         = var.resource_group_name
  priority                    = 1000
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = 3389
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  network_security_group_name = azurerm_network_security_group.vm_sg.name
}
resource "azurerm_network_security_rule" "sql_rule" {
  name                        = "MSSQLRule"
  resource_group_name         = var.resource_group_name
  priority                    = 1100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = 1433
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  network_security_group_name = azurerm_network_security_group.vm_sg.name
}
resource "azurerm_virtual_network" "base_vnet" {
  name                = var.vnet_name
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = [var.vnet_cidr]

  subnet {
    name           = var.subnet_name
    address_prefix = var.subnet_cidr
    security_group = azurerm_network_security_group.vm_sg.id
  }
}

