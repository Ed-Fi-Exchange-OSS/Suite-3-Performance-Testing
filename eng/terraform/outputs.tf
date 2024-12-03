/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

output "resource_group_name" {
  value       = azurerm_resource_group.base_rg.name
  description = "Name of the resource group created."
}
output "vnet_name" {
  value       = module.network.vnet_name
  description = "Name of the vnet created."
}

output "vnet_address_space" {
  value       = module.network.vnet_address_space
  description = "Address space of the vnet that was deployed."
}

output "vm_sg_name" {
  value       = module.network.vm_sg_name
  description = "Name of the security group that was deployed."
}

output "vm_sg_id" {
  value       = module.network.vm_sg_id
  description = "ID of the security group that was deployed."
}

output "sql_vm" {
  value = {
    vm_name          = module.sql_vm.vm_name
    vm_computer_name = module.sql_vm.vm_computer_name
    vm_private_ip    = module.sql_vm.vm_private_ip
    vm_public_ip     = module.sql_vm.vm_public_ip
    vm_extension_id  = module.sql_config.vm_extension_id
  }
  description = "SQL VM values"
}
output "web_vm" {
  value = {
    vm_name          = module.web_vm.vm_name
    vm_computer_name = module.web_vm.vm_computer_name
    vm_private_ip    = module.web_vm.vm_private_ip
    vm_public_ip     = module.web_vm.vm_public_ip
    vm_extension_id  = module.web_config.vm_extension_id
  }
  description = "Web VM values"
}

output "runner_vm" {
  value = {
    vm_name          = module.runner_vm.vm_name
    vm_computer_name = module.runner_vm.vm_computer_name
    vm_private_ip    = module.runner_vm.vm_private_ip
    vm_public_ip     = module.runner_vm.vm_public_ip
    vm_extension_id  = module.runner_config.vm_extension_id
  }
  description = "Runner VM values"
}

output "tfstate_storage_account_name" {
  value       = azurerm_storage_account.tf_state.name
  description = "Name of the TF state storage account created (use this for backend)."
}
