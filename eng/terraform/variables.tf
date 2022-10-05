variable "base_rg_name" {
  type = string
  description = "Name of the existing resource group to deploy into."
}

variable "at_vnet_name" {
  type = string
  description = "Name of the existing analytics vnet to deploy into."
}

variable "tools_vnet_name" {
  type = string
  description = "Name of the existing tools vnet to deploy into."

}

variable "at_base_subnet_name" {
  type = string
  description = "Name of the existing analytics subnet to deploy into."
  default = "default"
}

variable "tools_base_subnet_name" {
  type = string
  description = "Name of the existing tools subnet to deploy into."
  default = "default"
}

variable "apt_prefix" {
  type = string
  description = "Naming prefix for analytics resources."
}

variable "tools_prefix" {
  type = string
  description = "Naming prefix for tools resources."
}

variable "at_vm_admin_username" {
  description = "Analytics VM administrator username"
  type        = string
  sensitive   = true
}

variable "at_vm_admin_password" {
  description = "Analytics VM administrator password"
  type        = string
  sensitive   = true
}

variable "ods_vm_admin_username" {
  description = "ODS VM administrator username"
  type        = string
  sensitive   = true
}

variable "ods_vm_admin_password" {
  description = "ODS VM administrator password"
  type        = string
  sensitive   = true
}

variable "di_vm_admin_username" {
  description = "DI VM administrator username"
  type        = string
  sensitive   = true
}

variable "di_vm_admin_password" {
  description = "DI VM administrator password"
  type        = string
  sensitive   = true
}