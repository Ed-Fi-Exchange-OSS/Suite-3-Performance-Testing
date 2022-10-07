/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

output "vnet_name" {
  value = azurerm_virtual_network.base_vnet.name
}

output "vnet_id" {
  value = azurerm_virtual_network.base_vnet.id
}

output "vnet_rg" {
  value = azurerm_virtual_network.base_vnet.resource_group_name
}

output "vnet_location" {
  value = azurerm_virtual_network.base_vnet.location
}

output "vnet_address_space" {
  value = azurerm_virtual_network.base_vnet.address_space
}

output "vnet_subnet_id" {
  value = azurerm_virtual_network.base_vnet.subnet[*].id
}


output "vm_sg_name" {
  value = azurerm_network_security_group.vm_sg.name
}

output "vm_sg_id" {
  value = azurerm_network_security_group.vm_sg.id
}

