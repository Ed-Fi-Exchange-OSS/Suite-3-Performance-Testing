variable "base_rg_name" {
  type = string
}

variable "base_vnet" {
  type = string
}

variable "base_subnet" {
  type = string
}

variable "prefix" {
  type = string
}

variable "application" {
  description = "the application label to use at the end of the prefix ie ods"
  type = string
}
variable "sql_server_publisher" {
  default = "microsoftsqlserver"
  type = string
}
variable "sql_server_offer" {
  default = "sql2019-ws2019"
  type = string
}

variable "sql_server_sku" {
  default = "sqldev-gen2"
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

variable "location" {
  type = string
  default = "us-central"
}
