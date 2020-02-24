variable "key_name" {
    type    = string
    default = "surim"
}

variable "igw" {
    type     = string
    default  = "igw-b2f946da"
}

variable "my_access_key" {
    type    = string
}

variable "my_secret_key" {
    type    = string
}

variable "my_region" {
    type    = string
    default = "ap-northeast-2"
}

variable "target_group_path" {
    type    = string
    default = "/" # what does it do?
}
