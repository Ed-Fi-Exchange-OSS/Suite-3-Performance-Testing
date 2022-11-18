output "vm_extension_id" {
  description = "The azure ID of the custom script extension."
  value       = azurerm_virtual_machine_extension.script_install.id
}
