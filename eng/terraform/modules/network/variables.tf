/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

variable "resource_group_name" {
  type = string
  description = "Name of the resource group to deploy into."
}

variable "location" {
  type = string
  default = "centralus"
}
variable "prefix" {
  type = string
  description = "Naming prefix for resources."
}
variable "vnet_name" {
  type = string
  description = "Name of the vnet to create."
}
variable "subnet_name" {
  type = string
  description = "Name of the subnet to create."
  default = "default"
}

variable "vnet_cidr" {
  type = string
  description = "Address space of the vnet to create."
  default = "10.1.0.0/16"
}

variable "subnet_cidr" {
  type = string
  description = "Address space of the subnet to create."
  default = "10.1.0.0/24"
}
