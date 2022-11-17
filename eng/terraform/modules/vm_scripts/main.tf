data "template_file" "script_file" {

  template = "${file("./${var.script_filename}")}"
}
resource "azurerm_virtual_machine_extension" "script_install" {
  name                 = var.vm_computer_name
  virtual_machine_id   = var.vm_id
  publisher            = "Microsoft.Compute"
  type                 = "CustomScriptExtension"
  type_handler_version = "1.9"
  failure_suppression_enabled = false
  #type_handler_version = "1.10"
  settings = <<SETTINGS
 {
  "commandToExecute": "powershell -command \"[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('${base64encode(data.template_file.script_file.rendered)}')) | Out-File -filepath ${var.script_filename}\" && powershell -ExecutionPolicy Unrestricted -File ${var.script_filename}"
 }
SETTINGS

}
