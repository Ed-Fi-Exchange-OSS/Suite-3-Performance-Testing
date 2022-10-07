/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

output "vnet_name" {
  value       = azurerm_virtual_network.base_vnet.name
  description = "Name of the vnet created."
}

output "vnet_id" {
  value       = azurerm_virtual_network.base_vnet.id
  description = "ID of the vnet created."
}

output "vnet_rg" {
  value       = azurerm_virtual_network.base_vnet.resource_group_name
  description = "Name of the resource group that the vnet was deployed into."
}

output "vnet_location" {
  value       = azurerm_virtual_network.base_vnet.location
  description = "Location of the resource group that the vnet was deployed into."
}

output "vnet_address_space" {
  value       = azurerm_virtual_network.base_vnet.address_space
  description = "Address space of the vnet that was deployed."
}

output "vnet_subnet_id" {
  value       = azurerm_virtual_network.base_vnet.subnet[*].id
  description = "Subnet ID of the subnet that was deployed."
}


output "vm_sg_name" {
  value       = azurerm_network_security_group.vm_sg.name
  description = "Name of the security group that was deployed."
}

output "vm_sg_id" {
  value       = azurerm_network_security_group.vm_sg.id
  description = "ID of the security group that was deployed."
}

