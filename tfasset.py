still       = '''
provider "aws" {{
    profile = "aws_provider"
    region  = var.my_region
    access_key = var.my_access_key
    secret_key = var.my_secret_key
}}

resource "aws_subnet" "Dev_public1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.224.0/19"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public1"}}
}}

resource "aws_subnet" "Dev_public2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.128.0/19"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public2"}}
}}

resource "aws_subnet" "Dev_private1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.160.0/19"
    availability_zone = "ap-northeast-2a"
    tags = {{ Name = "Dev_private1"}}
}}

resource "aws_subnet" "Dev_private2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.192.0/19"
    availability_zone = "ap-northeast-2c"
    tags = {{ Name = "Dev_private2"}}
}}

resource "aws_eip" "Dev_nat_ip" {{
    vpc = true
    depends_on  = [var.igw]
    tags = {{ Name = "Dev_nat_ip"}}
}}

resource "aws_nat_gateway" "Dev_natgw" {{
    allocation_id = aws_eip.Dev_nat_ip.id
    subnet_id     = aws_subnet.Dev_public1.id
    tags = {{ Name = "Dev_natgw"}}
}}

resource "aws_route_table" "Dev_public" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = var.igw
  }}
  tags = {{ Name = "Dev_public" }}
}}

resource "aws_route_table" "Dev_private" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id =  aws_nat_gateway.Dev_natgw.id
  }}
  tags = {{ Name = "Dev_private" }}
}}

resource "aws_route_table_association" "Dev_public1" {{
  subnet_id      = aws_subnet.Dev_public1.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_public2" {{
  subnet_id      = aws_subnet.Dev_public2.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_private1" {{
  subnet_id      = aws_subnet.Dev_private1.id
  route_table_id = aws_route_table.Dev_private.id
}}

resource "aws_route_table_association" "Dev_private2" {{
  subnet_id      = aws_subnet.Dev_private2.id
  route_table_id = aws_route_table.Dev_private.id
}}


resource "aws_security_group" "Dev_sg1" {{
    name        = "Dev_sg1"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg2" {{
    name        = "Dev_sg2"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg3" {{
    name        = "Dev_sg3"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_instance" "Dev_Front1" {{
    instance_type           = "t2.micro"
    ami                     = "{0}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private1.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front1"}}
}}

resource "aws_instance" "Dev_Front2" {{
    instance_type           = "t2.micro"
    ami                     = "{1}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private2.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front2"  }}
}}

resource "aws_instance" "Dev_Back1" {{
    instance_type           = "t2.micro"
    ami                     = "{2}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private1.id
    tags = {{  Name = "Dev_Back1"  }}
}}

resource "aws_instance" "Dev_Back2" {{
    instance_type           = "t2.micro"
    ami                     = "{3}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private2.id
    tags = {{ Name = "Dev_Back2"}}
}}

resource "aws_lb" "Dev_external" {{
  name                  = "Dev-external"
  idle_timeout          = "300"
  load_balancer_type    = "application"
  subnets               = [aws_subnet.Dev_public1.id, aws_subnet.Dev_public2.id]
  security_groups       = [aws_security_group.Dev_sg1.id]
  enable_deletion_protection = false
}}

resource "aws_lb" "Dev_internal" {{
  name                    = "Dev-internal"
  internal                = true
  idle_timeout            = "300"
  load_balancer_type      = "application"
  subnets                 = [aws_subnet.Dev_private1.id, aws_subnet.Dev_private2.id]
  security_groups         = [aws_security_group.Dev_sg3.id]
  enable_deletion_protection = false
}}

resource "aws_security_group" "Dev_external_alb" {{
    name = "Dev_externalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_external"
    }}
}}

resource "aws_security_group" "Dev_internal_alb" {{
    name = "Dev_internalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_internal"
    }}
}}

resource "aws_alb_target_group" "Dev-Front" {{
    name     = "Dev-Front"
    port     = 8080
    protocol = "HTTP"
    vpc_id   = "vpc-3a61a851"

    health_check {{
        healthy_threshold   = 5
        unhealthy_threshold = 3
        timeout             = 5
        path                = var.target_group_path
        interval            = 30
        port                = 80
    }}
    tags = {{ Name   = "Dev_Front" }}
}}

resource "aws_alb_target_group" "Dev-Back" {{
  name     = "Dev-Back"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-3a61a851"

 health_check {{
    healthy_threshold   = 5
    unhealthy_threshold = 3
    timeout             = 5
    path                = var.target_group_path
    interval            = 30
    port                = 8080
  }}
  tags = {{ Name  = "Dev_Back"}}
}}

resource "aws_alb_target_group_attachment" "Dev_Front1" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Front2" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front2.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back1" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back2" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back2.id
    port             = 8080
}}

resource "aws_autoscaling_group" "front_old_auto" {{
    name                        = "front_old_auto"
    launch_configuration        = aws_launch_configuration.Front_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_old_auto" {{
    name                        = "back_old_auto"
    launch_configuration        = aws_launch_configuration.Back_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_attachment" "asg_front_old" {{
    autoscaling_group_name    = aws_autoscaling_group.front_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Front.arn
}}

resource "aws_autoscaling_attachment" "asg_back_old" {{
    autoscaling_group_name    = aws_autoscaling_group.back_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Back.arn
}}

resource "aws_launch_configuration" "Front_end_old" {{
    image_id                = "{0}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Front_end_new" {{
    image_id                = "{1}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_old" {{
    image_id                = "{2}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_new" {{
    image_id                = "{3}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}
'''

frontDeploy1 = '''
provider "aws" {{
    profile = "aws_provider"
    region  = var.my_region
    access_key = var.my_access_key
    secret_key = var.my_secret_key
}}

resource "aws_subnet" "Dev_public1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.224.0/19"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public1"}}
}}

resource "aws_subnet" "Dev_public2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.128.0/19"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public2"}}
}}

resource "aws_subnet" "Dev_private1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.160.0/19"
    availability_zone = "ap-northeast-2a"
    tags = {{ Name = "Dev_private1"}}
}}

resource "aws_subnet" "Dev_private2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.192.0/19"
    availability_zone = "ap-northeast-2c"
    tags = {{ Name = "Dev_private2"}}
}}

resource "aws_eip" "Dev_nat_ip" {{
    vpc = true
    depends_on  = [var.igw]
    tags = {{ Name = "Dev_nat_ip"}}
}}

resource "aws_nat_gateway" "Dev_natgw" {{
    allocation_id = aws_eip.Dev_nat_ip.id
    subnet_id     = aws_subnet.Dev_public1.id
    tags = {{ Name = "Dev_natgw"}}
}}

resource "aws_route_table" "Dev_public" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = var.igw
  }}
  tags = {{ Name = "Dev_public" }}
}}

resource "aws_route_table" "Dev_private" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id =  aws_nat_gateway.Dev_natgw.id
  }}
  tags = {{ Name = "Dev_private" }}
}}

resource "aws_route_table_association" "Dev_public1" {{
  subnet_id      = aws_subnet.Dev_public1.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_public2" {{
  subnet_id      = aws_subnet.Dev_public2.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_private1" {{
  subnet_id      = aws_subnet.Dev_private1.id
  route_table_id = aws_route_table.Dev_private.id
}}

resource "aws_route_table_association" "Dev_private2" {{
  subnet_id      = aws_subnet.Dev_private2.id
  route_table_id = aws_route_table.Dev_private.id
}}


resource "aws_security_group" "Dev_sg1" {{
    name        = "Dev_sg1"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg2" {{
    name        = "Dev_sg2"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg3" {{
    name        = "Dev_sg3"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_instance" "Dev_Front1" {{
    instance_type           = "t2.micro"
    ami                     = "{0}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private1.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front1"}}
}}

resource "aws_instance" "Dev_Front2" {{
    instance_type           = "t2.micro"
    ami                     = "{1}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private2.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front2"  }}
}}

resource "aws_instance" "Dev_Back1" {{
    instance_type           = "t2.micro"
    ami                     = "{2}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private1.id
    tags = {{  Name = "Dev_Back1"  }}
}}

resource "aws_instance" "Dev_Back2" {{
    instance_type           = "t2.micro"
    ami                     = "{3}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private2.id
    tags = {{ Name = "Dev_Back2"}}
}}

resource "aws_lb" "Dev_external" {{
  name                  = "Dev-external"
  idle_timeout          = "300"
  load_balancer_type    = "application"
  subnets               = [aws_subnet.Dev_public1.id, aws_subnet.Dev_public2.id]
  security_groups       = [aws_security_group.Dev_sg1.id]
  enable_deletion_protection = false
}}

resource "aws_lb" "Dev_internal" {{
  name                    = "Dev-internal"
  internal                = true
  idle_timeout            = "300"
  load_balancer_type      = "application"
  subnets                 = [aws_subnet.Dev_private1.id, aws_subnet.Dev_private2.id]
  security_groups         = [aws_security_group.Dev_sg3.id]
  enable_deletion_protection = false
}}

resource "aws_security_group" "Dev_external_alb" {{
    name = "Dev_externalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_external"
    }}
}}

resource "aws_security_group" "Dev_internal_alb" {{
    name = "Dev_internalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_internal"
    }}
}}

resource "aws_alb_target_group" "Dev-Front" {{
    name     = "Dev-Front"
    port     = 8080
    protocol = "HTTP"
    vpc_id   = "vpc-3a61a851"

    health_check {{
        healthy_threshold   = 5
        unhealthy_threshold = 3
        timeout             = 5
        path                = var.target_group_path
        interval            = 30
        port                = 80
    }}
    tags = {{ Name   = "Dev_Front" }}
}}

resource "aws_alb_target_group" "Dev-Back" {{
  name     = "Dev-Back"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-3a61a851"

 health_check {{
    healthy_threshold   = 5
    unhealthy_threshold = 3
    timeout             = 5
    path                = var.target_group_path
    interval            = 30
    port                = 8080
  }}
  tags = {{ Name  = "Dev_Back"}}
}}

resource "aws_alb_target_group_attachment" "Dev_Front1" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back1" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back2" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back2.id
    port             = 8080
}}

resource "aws_autoscaling_group" "front_old_auto" {{
    name                        = "front_old_auto"
    launch_configuration        = aws_launch_configuration.Front_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "front_new_auto" {{
    name                        = "front_new_auto"
    launch_configuration        = aws_launch_configuration.Front_end_new.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_old_auto" {{
    name                        = "back_old_auto"
    launch_configuration        = aws_launch_configuration.Back_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_attachment" "asg_front_old" {{
    autoscaling_group_name    = aws_autoscaling_group.front_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Front.arn
}}

resource "aws_autoscaling_attachment" "asg_back_old" {{
    autoscaling_group_name    = aws_autoscaling_group.back_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Back.arn
}}


resource "aws_launch_configuration" "Front_end_old" {{
    image_id                = "{0}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Front_end_new" {{
    image_id                = "{1}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_old" {{
    image_id                = "{2}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

'''

frontDeploy2 = '''
provider "aws" {{
    profile = "aws_provider"
    region  = var.my_region
    access_key = var.my_access_key
    secret_key = var.my_secret_key
}}

resource "aws_subnet" "Dev_public1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.224.0/19"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public1"}}
}}

resource "aws_subnet" "Dev_public2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.128.0/19"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public2"}}
}}

resource "aws_subnet" "Dev_private1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.160.0/19"
    availability_zone = "ap-northeast-2a"
    tags = {{ Name = "Dev_private1"}}
}}

resource "aws_subnet" "Dev_private2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.192.0/19"
    availability_zone = "ap-northeast-2c"
    tags = {{ Name = "Dev_private2"}}
}}

resource "aws_eip" "Dev_nat_ip" {{
    vpc = true
    depends_on  = [var.igw]
    tags = {{ Name = "Dev_nat_ip"}}
}}

resource "aws_nat_gateway" "Dev_natgw" {{
    allocation_id = aws_eip.Dev_nat_ip.id
    subnet_id     = aws_subnet.Dev_public1.id
    tags = {{ Name = "Dev_natgw"}}
}}

resource "aws_route_table" "Dev_public" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = var.igw
  }}
  tags = {{ Name = "Dev_public" }}
}}

resource "aws_route_table" "Dev_private" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id =  aws_nat_gateway.Dev_natgw.id
  }}
  tags = {{ Name = "Dev_private" }}
}}

resource "aws_route_table_association" "Dev_public1" {{
  subnet_id      = aws_subnet.Dev_public1.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_public2" {{
  subnet_id      = aws_subnet.Dev_public2.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_private1" {{
  subnet_id      = aws_subnet.Dev_private1.id
  route_table_id = aws_route_table.Dev_private.id
}}

resource "aws_route_table_association" "Dev_private2" {{
  subnet_id      = aws_subnet.Dev_private2.id
  route_table_id = aws_route_table.Dev_private.id
}}


resource "aws_security_group" "Dev_sg1" {{
    name        = "Dev_sg1"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg2" {{
    name        = "Dev_sg2"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg3" {{
    name        = "Dev_sg3"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_instance" "Dev_Front1" {{
    instance_type           = "t2.micro"
    ami                     = "{0}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private1.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front1"}}
}}

resource "aws_instance" "Dev_Front2" {{
    instance_type           = "t2.micro"
    ami                     = "{1}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private2.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front2"  }}
}}

resource "aws_instance" "Dev_Back1" {{
    instance_type           = "t2.micro"
    ami                     = "{2}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private1.id
    tags = {{  Name = "Dev_Back1"  }}
}}

resource "aws_instance" "Dev_Back2" {{
    instance_type           = "t2.micro"
    ami                     = "{3}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private2.id
    tags = {{ Name = "Dev_Back2"}}
}}

resource "aws_lb" "Dev_external" {{
  name                  = "Dev-external"
  idle_timeout          = "300"
  load_balancer_type    = "application"
  subnets               = [aws_subnet.Dev_public1.id, aws_subnet.Dev_public2.id]
  security_groups       = [aws_security_group.Dev_sg1.id]
  enable_deletion_protection = false
}}

resource "aws_lb" "Dev_internal" {{
  name                    = "Dev-internal"
  internal                = true
  idle_timeout            = "300"
  load_balancer_type      = "application"
  subnets                 = [aws_subnet.Dev_private1.id, aws_subnet.Dev_private2.id]
  security_groups         = [aws_security_group.Dev_sg3.id]
  enable_deletion_protection = false
}}

resource "aws_security_group" "Dev_external_alb" {{
    name = "Dev_externalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_external"
    }}
}}

resource "aws_security_group" "Dev_internal_alb" {{
    name = "Dev_internalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_internal"
    }}
}}

resource "aws_alb_target_group" "Dev-Front" {{
    name     = "Dev-Front"
    port     = 8080
    protocol = "HTTP"
    vpc_id   = "vpc-3a61a851"

    health_check {{
        healthy_threshold   = 5
        unhealthy_threshold = 3
        timeout             = 5
        path                = var.target_group_path
        interval            = 30
        port                = 80
    }}
    tags = {{ Name   = "Dev_Front" }}
}}

resource "aws_alb_target_group" "Dev-Back" {{
  name     = "Dev-Back"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-3a61a851"

 health_check {{
    healthy_threshold   = 5
    unhealthy_threshold = 3
    timeout             = 5
    path                = var.target_group_path
    interval            = 30
    port                = 8080
  }}
  tags = {{ Name  = "Dev_Back"}}
}}

resource "aws_alb_target_group_attachment" "Dev_Front2" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front2.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back1" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back2" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back2.id
    port             = 8080
}}

resource "aws_autoscaling_group" "front_old_auto" {{
    name                        = "front_old_auto"
    launch_configuration        = aws_launch_configuration.Front_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "front_new_auto" {{
    name                        = "front_new_auto"
    launch_configuration        = aws_launch_configuration.Front_end_new.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_old_auto" {{
    name                        = "back_old_auto"
    launch_configuration        = aws_launch_configuration.Back_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_attachment" "asg_front_new" {{
    autoscaling_group_name    = aws_autoscaling_group.front_new_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Front.arn
}}

resource "aws_autoscaling_attachment" "asg_back_old" {{
    autoscaling_group_name    = aws_autoscaling_group.back_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Back.arn
}}

resource "aws_launch_configuration" "Front_end_old" {{
    image_id                = "{0}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Front_end_new" {{
    image_id                = "{1}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_old" {{
    image_id                = "{2}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

'''

backDeploy1  = '''
provider "aws" {{
    profile = "aws_provider"
    region  = var.my_region
    access_key = var.my_access_key
    secret_key = var.my_secret_key
}}

resource "aws_subnet" "Dev_public1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.224.0/19"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public1"}}
}}

resource "aws_subnet" "Dev_public2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.128.0/19"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public2"}}
}}

resource "aws_subnet" "Dev_private1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.160.0/19"
    availability_zone = "ap-northeast-2a"
    tags = {{ Name = "Dev_private1"}}
}}

resource "aws_subnet" "Dev_private2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.192.0/19"
    availability_zone = "ap-northeast-2c"
    tags = {{ Name = "Dev_private2"}}
}}

resource "aws_eip" "Dev_nat_ip" {{
   vpc = true
   depends_on  = [var.igw]
   tags = {{ Name = "Dev_nat_ip"}}
}}

resource "aws_nat_gateway" "Dev_natgw" {{
  allocation_id = aws_eip.Dev_nat_ip.id
  subnet_id     = aws_subnet.Dev_public1.id
  tags = {{ Name = "Dev_natgw"}}
}}

resource "aws_route_table" "Dev_public" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = var.igw
  }}
  tags = {{ Name = "Dev_public" }}
}}

resource "aws_route_table" "Dev_private" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id =  aws_nat_gateway.Dev_natgw.id
  }}
  tags = {{ Name = "Dev_private" }}
}}

resource "aws_route_table_association" "Dev_public1" {{
  subnet_id      = aws_subnet.Dev_public1.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_public2" {{
  subnet_id      = aws_subnet.Dev_public2.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_private1" {{
  subnet_id      = aws_subnet.Dev_private1.id
  route_table_id = aws_route_table.Dev_private.id
}}

resource "aws_route_table_association" "Dev_private2" {{
  subnet_id      = aws_subnet.Dev_private2.id
  route_table_id = aws_route_table.Dev_private.id
}}


resource "aws_security_group" "Dev_sg1" {{
    name        = "Dev_sg1"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg2" {{
    name        = "Dev_sg2"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg3" {{
    name        = "Dev_sg3"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_instance" "Dev_Front1" {{
    instance_type           = "t2.micro"
    ami                     = "{0}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private1.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front1"}}
}}

resource "aws_instance" "Dev_Front2" {{
    instance_type           = "t2.micro"
    ami                     = "{1}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private2.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front2"  }}
}}

resource "aws_instance" "Dev_Back1" {{
    instance_type           = "t2.micro"
    ami                     = "{2}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private1.id
    tags = {{  Name = "Dev_Back1"  }}
}}

resource "aws_instance" "Dev_Back2" {{
    instance_type           = "t2.micro"
    ami                     = "{3}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private2.id
    tags = {{ Name = "Dev_Back2"}}
}}

resource "aws_lb" "Dev_external" {{
  name                  = "Dev-external"
  idle_timeout          = "300"
  load_balancer_type    = "application"
  subnets               = [aws_subnet.Dev_public1.id, aws_subnet.Dev_public2.id]
  security_groups       = [aws_security_group.Dev_sg1.id]
  enable_deletion_protection = false
}}

resource "aws_lb" "Dev_internal" {{
  name                    = "Dev-internal"
  internal                = true
  idle_timeout            = "300"
  load_balancer_type      = "application"
  subnets                 = [aws_subnet.Dev_private1.id, aws_subnet.Dev_private2.id]
  security_groups         = [aws_security_group.Dev_sg3.id]
  enable_deletion_protection = false
}}

resource "aws_security_group" "Dev_external_alb" {{
    name = "Dev_externalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_external"
    }}
}}

resource "aws_security_group" "Dev_internal_alb" {{
    name = "Dev_internalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_internal"
    }}
}}

resource "aws_alb_target_group" "Dev-Front" {{
    name     = "Dev-Front"
    port     = 8080
    protocol = "HTTP"
    vpc_id   = "vpc-3a61a851"

    health_check {{
        healthy_threshold   = 5
        unhealthy_threshold = 3
        timeout             = 5
        path                = var.target_group_path
        interval            = 30
        port                = 80
    }}
    tags = {{ Name   = "Dev_Front" }}
}}

resource "aws_alb_target_group" "Dev-Back" {{
  name     = "Dev-Back"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-3a61a851"

 health_check {{
    healthy_threshold   = 5
    unhealthy_threshold = 3
    timeout             = 5
    path                = var.target_group_path
    interval            = 30
    port                = 8080
  }}
  tags = {{ Name  = "Dev_Back"}}
}}

resource "aws_alb_target_group_attachment" "Dev_Front1" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Front2" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front2.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back1" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back1.id
    port             = 8080
}}


resource "aws_autoscaling_group" "front_old_auto" {{
    name                        = "front_old_auto"
    launch_configuration        = aws_launch_configuration.Front_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_old_auto" {{
    name                        = "back_old_auto"
    launch_configuration        = aws_launch_configuration.Back_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_new_auto" {{
    name                        = "back_new_auto"
    launch_configuration        = aws_launch_configuration.Back_end_new.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_attachment" "asg_front_old" {{
    autoscaling_group_name    = aws_autoscaling_group.front_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Front.arn
}}

resource "aws_autoscaling_attachment" "asg_back_old" {{
    autoscaling_group_name    = aws_autoscaling_group.back_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Back.arn
}}

resource "aws_launch_configuration" "Front_end_old" {{
    image_id                = "{0}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_old" {{
    image_id                = "{2}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_new" {{
    image_id                = "{3}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

'''

backDeploy2  = '''
provider "aws" {{
    profile = "aws_provider"
    region  = var.my_region
    access_key = var.my_access_key
    secret_key = var.my_secret_key
}}

resource "aws_subnet" "Dev_public1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.224.0/19"
    availability_zone = "ap-northeast-2a"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public1"}}
}}

resource "aws_subnet" "Dev_public2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.128.0/19"
    availability_zone = "ap-northeast-2c"
    map_public_ip_on_launch = true
    tags = {{ Name = "Dev_public2"}}
}}

resource "aws_subnet" "Dev_private1" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.160.0/19"
    availability_zone = "ap-northeast-2a"
    tags = {{ Name = "Dev_private1"}}
}}

resource "aws_subnet" "Dev_private2" {{
    vpc_id = "vpc-3a61a851"
    cidr_block = "172.31.192.0/19"
    availability_zone = "ap-northeast-2c"
    tags = {{ Name = "Dev_private2"}}
}}

resource "aws_eip" "Dev_nat_ip" {{
   vpc = true
   depends_on  = [var.igw]
   tags = {{ Name = "Dev_nat_ip"}}
}}

resource "aws_nat_gateway" "Dev_natgw" {{
  allocation_id = aws_eip.Dev_nat_ip.id
  subnet_id     = aws_subnet.Dev_public1.id
  tags = {{ Name = "Dev_natgw"}}
}}

resource "aws_route_table" "Dev_public" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = var.igw
  }}
  tags = {{ Name = "Dev_public" }}
}}

resource "aws_route_table" "Dev_private" {{
  vpc_id = "vpc-3a61a851"
  route {{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id =  aws_nat_gateway.Dev_natgw.id
  }}
  tags = {{ Name = "Dev_private" }}
}}

resource "aws_route_table_association" "Dev_public1" {{
  subnet_id      = aws_subnet.Dev_public1.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_public2" {{
  subnet_id      = aws_subnet.Dev_public2.id
  route_table_id = aws_route_table.Dev_public.id
}}

resource "aws_route_table_association" "Dev_private1" {{
  subnet_id      = aws_subnet.Dev_private1.id
  route_table_id = aws_route_table.Dev_private.id
}}

resource "aws_route_table_association" "Dev_private2" {{
  subnet_id      = aws_subnet.Dev_private2.id
  route_table_id = aws_route_table.Dev_private.id
}}


resource "aws_security_group" "Dev_sg1" {{
    name        = "Dev_sg1"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg2" {{
    name        = "Dev_sg2"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_security_group" "Dev_sg3" {{
    name        = "Dev_sg3"
    vpc_id      = "vpc-3a61a851"

    ingress {{
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    ingress {{
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    egress {{
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }}
}}

resource "aws_instance" "Dev_Front1" {{
    instance_type           = "t2.micro"
    ami                     = "{0}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private1.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front1"}}
}}

resource "aws_instance" "Dev_Front2" {{
    instance_type           = "t2.micro"
    ami                     = "{1}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg2.id]
    subnet_id               = aws_subnet.Dev_private2.id
    associate_public_ip_address = true
    tags = {{ Name = "Dev_Front2"  }}
}}

resource "aws_instance" "Dev_Back1" {{
    instance_type           = "t2.micro"
    ami                     = "{2}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private1.id
    tags = {{  Name = "Dev_Back1"  }}
}}

resource "aws_instance" "Dev_Back2" {{
    instance_type           = "t2.micro"
    ami                     = "{3}"
    key_name                = var.key_name
    vpc_security_group_ids  = [aws_security_group.Dev_sg3.id]
    subnet_id               = aws_subnet.Dev_private2.id
    tags = {{ Name = "Dev_Back2"}}
}}

resource "aws_lb" "Dev_external" {{
  name                  = "Dev-external"
  idle_timeout          = "300"
  load_balancer_type    = "application"
  subnets               = [aws_subnet.Dev_public1.id, aws_subnet.Dev_public2.id]
  security_groups       = [aws_security_group.Dev_sg1.id]
  enable_deletion_protection = false
}}

resource "aws_lb" "Dev_internal" {{
  name                    = "Dev-internal"
  internal                = true
  idle_timeout            = "300"
  load_balancer_type      = "application"
  subnets                 = [aws_subnet.Dev_private1.id, aws_subnet.Dev_private2.id]
  security_groups         = [aws_security_group.Dev_sg3.id]
  enable_deletion_protection = false
}}

resource "aws_security_group" "Dev_external_alb" {{
    name = "Dev_externalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_external"
    }}
}}

resource "aws_security_group" "Dev_internal_alb" {{
    name = "Dev_internalALB"
    vpc_id = "vpc-3a61a851"
    ingress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        ingress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
        egress {{
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }}
    tags = {{
        Name = "Dev_internal"
    }}
}}

resource "aws_alb_target_group" "Dev-Front" {{
    name     = "Dev-Front"
    port     = 8080
    protocol = "HTTP"
    vpc_id   = "vpc-3a61a851"

    health_check {{
        healthy_threshold   = 5
        unhealthy_threshold = 3
        timeout             = 5
        path                = var.target_group_path
        interval            = 30
        port                = 80
    }}
    tags = {{ Name   = "Dev_Front" }}
}}

resource "aws_alb_target_group" "Dev-Back" {{
  name     = "Dev-Back"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-3a61a851"

 health_check {{
    healthy_threshold   = 5
    unhealthy_threshold = 3
    timeout             = 5
    path                = var.target_group_path
    interval            = 30
    port                = 8080
  }}
  tags = {{ Name  = "Dev_Back"}}
}}

resource "aws_alb_target_group_attachment" "Dev_Front1" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front1.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Front2" {{
    target_group_arn = aws_alb_target_group.Dev-Front.arn
    target_id        = aws_instance.Dev_Front2.id
    port             = 8080
}}

resource "aws_alb_target_group_attachment" "Dev_Back2" {{
    target_group_arn = aws_alb_target_group.Dev-Back.arn
    target_id        = aws_instance.Dev_Back2.id
    port             = 8080
}}


resource "aws_autoscaling_group" "front_old_auto" {{
    name                        = "front_old_auto"
    launch_configuration        = aws_launch_configuration.Front_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "front_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_old_auto" {{
    name                        = "back_old_auto"
    launch_configuration        = aws_launch_configuration.Back_end_old.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}

resource "aws_autoscaling_group" "back_new_auto" {{
    name                        = "back_new_auto"
    launch_configuration        = aws_launch_configuration.Back_end_new.id
    max_size                    = 4
    min_size                    = 1
    health_check_grace_period   = 300
    health_check_type           = "ELB"
    availability_zones          = ["ap-northeast-2a", "ap-northeast-2c"]
    tag {{
        key                   = "Name"
        value                 = "Back_auto scaling"
        propagate_at_launch   = true
    }}
}}


resource "aws_autoscaling_attachment" "asg_front_old" {{
    autoscaling_group_name    = aws_autoscaling_group.front_old_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Front.arn
}}

resource "aws_autoscaling_attachment" "asg_back_new" {{
    autoscaling_group_name    = aws_autoscaling_group.back_auto.id
    alb_target_group_arn      = aws_alb_target_group.Dev-Back.arn
}}

resource "aws_launch_configuration" "Front_end_old" {{
    image_id                = "{0}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_old" {{
    image_id                = "{2}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

resource "aws_launch_configuration" "Back_end_new" {{
    image_id                = "{3}"
    instance_type           = "t2.micro"
    associate_public_ip_address = true
    lifecycle {{
        create_before_destroy = true
    }}
}}

'''