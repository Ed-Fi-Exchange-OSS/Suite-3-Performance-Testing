/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */
variable "location" {
  type        = string
  description = "The location to deploy into."
  default     = "centralus"
}
variable "prefix" {
  type        = string
  description = "First part of the naming prefix for resources."
}
variable "label" {
  type        = string
  description = "Descriptive label. Secnd part of the naming prefix for resources."
}
variable "base_subnet" {
  type        = string
  description = "Name of the existing tools subnet to deploy into."
  default     = "default"
}
variable "web_vm_size" {
  type        = string
  description = "VM size for the web and runner VMs"
  default     = "Standard_D2s_v3"
}
variable "sql_vm_size" {
  type        = string
  description = "VM size for the sql VM"
  default     = "Standard_DS11_v2"
}

variable "web_vm_data_disk_size" {
  type        = number
  description = "Data disk size for the web and runner VM"
  default     = 16
}
variable "sql_vm_data_disk_size" {
  type        = number
  description = "Data disk size for the sql VM"
  default     = 28
}

variable "web_vm_image_publisher" {
  default     = "MicrosoftWindowsServer"
  description = "Publisher of the web VM image."
  type        = string
}
variable "web_vm_image_offer" {
  default     = "WindowsServer"
  description = "Offer of the web VM image."
  type        = string
}

variable "web_vm_image_sku" {
  default     = "2022-datacenter-azure-edition"
  description = "SKU of the web VM image."
  type        = string
}

variable "sql_vm_image_publisher" {
  default     = "microsoftsqlserver"
  description = "Publisher of the sql VM image."
  type        = string
}
variable "sql_vm_image_offer" {
  default     = "sql2022-ws2022"
  description = "Offer of the sql VM image."
  type        = string
}

variable "sql_vm_image_sku" {
  default     = "sqldev-gen2"
  description = "SKU of the sql VM image."
  type        = string
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

variable "web_vm_computer_name" {
  type        = string
  description = "Computer name for the ODS Web VM"
  default     = "EDFI-ODS"
  validation {
    condition     = length(var.web_vm_computer_name) < 16
    error_message = "computer_name can be at most 15 characters"
  }
}

variable "runner_vm_computer_name" {
  type        = string
  description = "Computer name for the Runner VM"
  default     = "EDFI-RUNNER"
  validation {
    condition     = length(var.runner_vm_computer_name) < 16
    error_message = "computer_name can be at most 15 characters"
  }
}

variable "sql_vm_computer_name" {
  type        = string
  description = "Computer name for the SQL Web VM"
  default     = "EDFI-DB"
  validation {
    condition     = length(var.sql_vm_computer_name) < 16
    error_message = "computer_name can be at most 15 characters"
  }
}
