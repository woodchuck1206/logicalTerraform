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

variable "db_username" {
    type    = string # needs to set as environ variable #TF_VAR_db_username
}

variable "db_password" {
    type    = string # needs to set as environ variable #TF_VAR_db_password
}

variable "db_port" {
    type    = string
    default = "3306"
}
