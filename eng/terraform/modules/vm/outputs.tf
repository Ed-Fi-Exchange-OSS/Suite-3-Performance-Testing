/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */
output "base_vm_name" {
  value = local.base_vm_name
  description = "Base name of the VM."
}
output "vm_nic_name" {
  value = azurerm_network_interface.vm_nic.name
  description = "Name of the network interface that was deployed."
}
output "vm_nic_id" {
  value = azurerm_network_interface.vm_nic.id
  description = "ID of the network interface that was deployed."
}

output "vm_pip_id" {
  value = azurerm_public_ip.vm_pip.id
  description = "ID of the public IP that was deployed."
}
output "vm_pip_address" {
  value = azurerm_public_ip.vm_pip.ip_address
  description = "Address of the public IP that was deployed."
}

output "vm_name" {
  value = azurerm_windows_virtual_machine.vm.name
  description = "Name of the VM that was deployed."
}
output "vm_computer_name" {
  value = azurerm_windows_virtual_machine.vm.computer_name
  description = "Full computer name of the VM that was deployed."
}
output "vm_id" {
  value = azurerm_windows_virtual_machine.vm.id
  description = "ID of the VM that was deployed."
}
output "vm_private_ip" {
  value = azurerm_windows_virtual_machine.vm.private_ip_address
  description = "Private IP of the VM that was deployed."
}
output "vm_public_ip" {
  value = azurerm_windows_virtual_machine.vm.public_ip_address
  description = "Public IP of the VM that was deployed."
}
