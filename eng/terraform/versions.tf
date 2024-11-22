/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

terraform {
  required_version = "~> 1.2"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.32.0"
    }
    random = {
      version = "~> 3.4"
    }
  }
}
