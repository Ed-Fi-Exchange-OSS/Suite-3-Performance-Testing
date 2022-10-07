/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */
output "base_vm_name" {
  value = local.base_vm_name
}
output "vm_nic_name" {
  value = azurerm_network_interface.vm_nic.name
}
output "vm_nic_id" {
  value = azurerm_network_interface.vm_nic.id
}
output "vm_sg_name" {
  value = azurerm_network_security_group.vm_sg.name
}

output "vm_sg_id" {
  value = azurerm_network_security_group.vm_sg.id
}

output "vm_pip_id" {
  value = azurerm_public_ip.vm_pip.id
}
output "vm_pip_ip" {
  value = azurerm_public_ip.vm_pip.ip_address
}

output "vm_name" {
  value = azurerm_windows_virtual_machine.vm.name
}
output "vm_computer_name" {
  value = azurerm_windows_virtual_machine.vm.computer_name
}
output "vm_id" {
  value = azurerm_windows_virtual_machine.vm.id
}
output "vm_private_ip" {
  value = azurerm_windows_virtual_machine.vm.private_ip_address
}
output "vm_public_ip" {
  value = azurerm_windows_virtual_machine.vm.public_ip_address
}