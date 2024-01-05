variable "vm_computer_name" {
  type        = string
  description = "VM computer name, names the custom script extension."
}
variable "vm_id" {
  type        = string
  description = "VM ID, to specify which VM to install to."
}
variable "script_filename" {
  type        = string
  description = "Filename of the script to install on the vm. Must be in the same directory as the top-level main.tf"
}
