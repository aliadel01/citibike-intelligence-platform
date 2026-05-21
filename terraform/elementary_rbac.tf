# 1. Create the Isolated Schema
resource "snowflake_schema" "elementary" {
  name     = "ELEMENTARY"
  database = snowflake_database.citibike_db.name
}

# 2. Create the Account Role (Updated from snowflake_role)
resource "snowflake_account_role" "elementary_role" {
  name    = "ELEMENTARY_ROLE"
  comment = "Role for Elementary data observability tool"
}

# 3. Create the User
resource "snowflake_user" "elementary_user" {
  name         = "ELEMENTARY_USER"
  login_name   = "ELEMENTARY_USER"
  comment      = "User for Elementary data observability tool"
  default_role = snowflake_account_role.elementary_role.name
  password     = var.elementary_user_password 
}

# 4. Grant the Account Role to the User (Updated syntax)
resource "snowflake_grant_account_role" "elementary_user_grant" {
  role_name        = snowflake_account_role.elementary_role.name
  user_name        = snowflake_user.elementary_user.name
}

# 5. Grant Warehouse and Database USAGE privileges to the Role
resource "snowflake_grant_privileges_to_account_role" "elementary_wh_grant" {
  account_role_name = snowflake_account_role.elementary_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.citibike_dwh.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "elementary_db_grant" {
  account_role_name = snowflake_account_role.elementary_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.citibike_db.name
  }
}

# 6. Grant ALL Schema Privileges
resource "snowflake_grant_privileges_to_account_role" "elementary_schema_access" {
  account_role_name = snowflake_account_role.elementary_role.name
  privileges        = ["ALL PRIVILEGES"]
  on_schema {
    schema_name = "\"${snowflake_database.citibike_db.name}\".\"${snowflake_schema.elementary.name}\""
  }
}

# 7. Grant Future Table/View SELECT Privileges in the Schema
resource "snowflake_grant_privileges_to_account_role" "elementary_future_tables" {
  account_role_name = snowflake_account_role.elementary_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.citibike_db.name}\".\"${snowflake_schema.elementary.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "elementary_future_views" {
  account_role_name = snowflake_account_role.elementary_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    future {
      object_type_plural = "VIEWS"
      in_schema          = "\"${snowflake_database.citibike_db.name}\".\"${snowflake_schema.elementary.name}\""
    }
  }
}