# Ed-Fi Performance Testing in Azure

Terraform scripts to deploy performance testing infrastructure into Azure.

# Description

This terraform script creates resources to deploy the Ed-Fi performance testing Azure environment. This script assumes that you will at start with a resource group for all resources, and VPC(s)/subnet(s) for the VMs and other resources to reside in and connect to.

The main script uses a common module to deploy 3 VMs.

- ODS Web VM
- Runner VM
- SQL Server VM

The common resources created in this module regardless of given variables are:

- network security group
  - allow port 3389 from anywhere
  - attached to VM
- public IP
- network interface
- VM
  - of variable size and image
- OS disk
  - of variable size

A storage account to store the terraform stage is also created.

## Prerequisites

The user needs [Terraform](https://www.terraform.io/downloads). Latest version is recommended.

The user also must have the [az CLI installed](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) and must have the user Credentials set with `az login`.

## Usage

First, plan and apply the Terraform

1. Copy the `terraform.tfvars.example` file renamed to `terraform.tfvars` and replace the values with the correct values. This file will be picked up automatically and used for `terraform` commands.
2. Run `terraform init` to retrieve remote modules.
3. Run `terraform plan` to review pending changes.
4. Run `terraform apply` to deploy the resources.

Finally, migrate the state into the newly created Terraform remote state azure storage account.

1. Create a copy of the `backend.tf.example` file renamed to `backend.tf`
2. Look up the Terraform remote state bucket using `terraform output azure_storage_tfstate`. Note this value for later use.
3. Copy the value from the previous step into the placeholder for the storage account name.
4. Enter the resource group name from your `terraform.tfvars` file in the placeholder for the resource group name.
5. Run `terraform init` and when prompted, allow the state to be copied to the bucket.
