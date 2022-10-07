/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

variable "resource_group_name" {
  type = string
  description = "Name of the existing resource group to deploy into."
}
variable "location" {
  type = string
  description = "The location to deploy into."
  default = "centralus"
}
variable "subnet_id" {
  type = string
  description = "Name of the existing subnet to deploy into."
  default = "default"
}

variable "prefix" {
  type = string
  description = "Naming prefix for resources."
}
variable "application" {
  type = string
  description = "Short description of the resources."
}

variable "vm_sg_id" {
  description = "ID of the security group to attach the vm to."
  type = string
}
variable "admin_username" {
  description = "VM administrator username"
  type        = string
  sensitive   = true
}

variable "admin_password" {
  description = "VM administrator password"
  type        = string
  sensitive   = true
}

variable "vm_size" {
  type = string
  description = "Size of the VM to deploy."
  default = "Standard_D2s_v3"
}

variable "vm_image_publisher" {
  default = "MicrosoftWindowsServer"
  description = "Publisher of the VM image."
  type = string
}
variable "vm_image_offer" {
  default = "WindowsServer"
  description = "Offer of the VM image."
  type = string
}

variable "vm_image_sku" {
  default = "2022-datacenter-azure-edition"
  description = "SKU of the VM image."
  type = string
}


variable "os_disk_size" {
  type = number
  description = "Size of the OS disk to create."
  default = 16
}
