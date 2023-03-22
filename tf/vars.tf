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

variable "subnets" {
  type = string
}
