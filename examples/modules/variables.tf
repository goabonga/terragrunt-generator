variable "required" {
    type = string
    description = "required value"
}

variable "optional" {
    type = string
    default = "optional"
    description = "optional value"
}

variable "nullable" {
    type = string
    default = null
    description = "nullable value"
}
