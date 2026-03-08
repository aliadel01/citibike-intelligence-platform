terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.87"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "snowflake" {
  account_name = var.snowflake_account
  organization_name = var.snowflake_organization  
  user = var.snowflake_username
  password = var.snowflake_password
  role     = "ACCOUNTADMIN"
}