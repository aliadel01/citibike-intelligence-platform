# Azure Data Lake Gen2

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = true # Hierarchical Namespace = ADLS Gen2
}

resource "azurerm_storage_container" "trip-data" {
  name                  = "trip-data"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "station-metadata" {
  name                  = "station-metadata"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

# Snowflake Infrastructure

# Warehouse
resource "snowflake_warehouse" "citibike-dwh" {
  name                 = "CITIBIKE_DWH"
  warehouse_size       = "XSMALL"
  auto_suspend         = 60
  auto_resume          = true
  initially_suspended  = true
}

# Database
resource "snowflake_database" "citibike-db" {
  name = "CITIBIKE_DB"
}

# Schemas
resource "snowflake_schema" "bronze" {
  name     = "BRONZE"
  database = snowflake_database.citibike-db.name
}

resource "snowflake_schema" "silver" {
  name     = "SILVER"
  database = snowflake_database.citibike-db.name
}

resource "snowflake_schema" "gold" {
  name     = "GOLD"
  database = snowflake_database.citibike-db.name
}