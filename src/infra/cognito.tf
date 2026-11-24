# ── Cognito User Pool ─────────────────────────────────────────────────────────

resource "aws_cognito_user_pool" "main" {
  name = "${var.app_name}-users"

  # Users sign in with email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length                   = 8
    require_uppercase                = true
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = false
    temporary_password_validity_days = 7
  }

  # Email verification message
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "Your Cigar Log verification code"
    email_message        = "Your verification code is {####}"
  }

  # Standard attributes
  schema {
    name                     = "email"
    attribute_data_type      = "String"
    required                 = true
    mutable                  = true
    string_attribute_constraints {
      min_length = 3
      max_length = 254
    }
  }

  schema {
    name                     = "name"
    attribute_data_type      = "String"
    required                 = false
    mutable                  = true
    string_attribute_constraints {
      min_length = 1
      max_length = 100
    }
  }

  # Account recovery via email
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Allow self-registration
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  tags = {
    Name = "${var.app_name}-users"
  }
}

# ── App Client (SPA — no client secret, PKCE) ─────────────────────────────────

resource "aws_cognito_user_pool_client" "spa" {
  name         = "${var.app_name}-spa"
  user_pool_id = aws_cognito_user_pool.main.id

  # Public client — no secret (SPA uses PKCE)
  generate_secret = false

  # Auth flows
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]

  # OAuth2 / OIDC
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  callback_urls = var.cognito_callback_urls
  logout_urls   = var.cognito_logout_urls

  supported_identity_providers = ["COGNITO"]

  # Token lifetimes
  access_token_validity  = 60   # minutes
  id_token_validity      = 60   # minutes
  refresh_token_validity = 30   # days

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Prevent user existence errors leaking in auth responses
  prevent_user_existence_errors = "ENABLED"
}

# ── Hosted UI domain ──────────────────────────────────────────────────────────
# Uses a Cognito-managed subdomain: https://{prefix}.auth.{region}.amazoncognito.com

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.app_name}-${var.cognito_domain_prefix}"
  user_pool_id = aws_cognito_user_pool.main.id
}
