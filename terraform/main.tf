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

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}


# Snowflake Infrastructure

# Warehouse
resource "snowflake_warehouse" "citibike_dwh" {
  name                 = "CITIBIKE_DWH"
  warehouse_size       = "XSMALL"
  auto_suspend         = 60
  auto_resume          = true
  initially_suspended  = true
}

# Database
resource "snowflake_database" "citibike_db" {
  name = "CITIBIKE_DB"
}

# Schemas
resource "snowflake_schema" "external" {
  name     = "EXTERNAL"
  database = snowflake_database.citibike_db.name
}

resource "snowflake_schema" "silver" {
  name     = "SILVER"
  database = snowflake_database.citibike_db.name
}

resource "snowflake_schema" "gold" {
  name     = "GOLD"
  database = snowflake_database.citibike_db.name
}



# Storage Integration — allows Snowflake to read Azure ADLS Gen2 without SAS tokens
resource "snowflake_storage_integration" "azure" {
  name    = "CITIBIKE_AZURE_INTEGRATION"
  type    = "EXTERNAL_STAGE"
  enabled = true

  storage_provider          = "AZURE"
  azure_tenant_id           = var.azure_tenant_id
  storage_allowed_locations = [
    "azure://${azurerm_storage_account.datalake.name}.blob.core.windows.net/${azurerm_storage_container.bronze.name}/"
  ]
}

# Look up the Snowflake service principal in Azure AD (created after first apply + consent)
data "azuread_service_principal" "snowflake" {
  display_name = snowflake_storage_integration.azure.azure_multi_tenant_app_name
}

# Grant Snowflake's service principal read access to the storage account
resource "azurerm_role_assignment" "snowflake_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = data.azuread_service_principal.snowflake.object_id
}

# File Formats
resource "snowflake_file_format" "csv_format" {
  name     = "CSV_FORMAT"
  database = snowflake_database.citibike_db.name
  schema   = snowflake_schema.external.name
  
  format_type = "CSV"
  skip_header = 1
}

resource "snowflake_file_format" "json_format" {
  name     = "JSON_FORMAT"
  database = snowflake_database.citibike_db.name
  schema   = snowflake_schema.external.name
  
  format_type = "JSON"
}

# Stage
resource "snowflake_stage" "bronze_stage" {
  name     = "BRONZE_STAGE"
  database = snowflake_database.citibike_db.name
  schema   = snowflake_schema.external.name

  url                 = "azure://${azurerm_storage_account.datalake.name}.blob.core.windows.net/${azurerm_storage_container.bronze.name}/"
  storage_integration = snowflake_storage_integration.azure.name
}