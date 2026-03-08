variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
}

variable "location" {
  description = "Azure location"
  type        = string
}

variable "storage_account_name" {
  description = "Name of the Azure storage account"
  type        = string
}

variable "snowflake_account" {
  type        = string
  description = "Snowflake account identifier"
}

variable "snowflake_organization" {
  type        = string
  description = "Snowflake organization name"
}


variable "snowflake_username" {
  type        = string
  description = "Snowflake username"
}

variable "snowflake_password" {
  type        = string
  description = "Snowflake password"
  sensitive   = true
}

variable "azure_tenant_id" {
  type        = string
  description = "Azure Active Directory tenant ID (used for Snowflake storage integration)"
}