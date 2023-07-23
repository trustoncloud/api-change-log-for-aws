variable "app" {
  type    = string
  default = "apichanges"
}

variable "resource_tags" {
  type = map(any)
  default = {
    "App" = "AWSAPIChanges"
  }
}

variable "domain" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "slack_webhook" {
  type      = map(string)
  sensitive = true
}
