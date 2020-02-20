import os

class Terraform:
    body = ""
    tf_file = ""
    elements = []

    def __init__(self, credentials_path=os.path.join(os.environ["HOME"], ".aws", "credentials"), region="ap-northeast-2"):
        self.body = '''
        provider "aws" {{
            profile     = "aws_provider"
            region      = {}
            credentials = {}
        }}
        
        '''.format(region, credentials_path)

    def publish(self):
        if len(self.body) == 0: 
            print("Body is empty, please documentise before you publish")
            return

        with open(self.tf_file, "w+") as f:
            f.write(self.body)

    def documentise(self):
        while True:
            if len(self.elements) == 0: break
            entry = self.elements.pop()
            self.body += "\n" + entry["text"]

    def add(self, element):
        self.elements.append(element)

    def gen_vpc(self, name, cidr):
        return {
            "kind"  : "vpc",
            "name"  : name,
            "cidr"  : cidr,
            "text"  : '''
            resource "aws_vpc" "{}" {{
                cidr_block              = "{}"
                enable_dns_hostnames    = "true"
            }}
            '''.format(name, cidr)
        }
    
    def gen_igw(self, name, vpc_name): 
        return {
            "kind"      : "igw",
            "name"      : name,
            "vpc_name"  : vpc_name,
            "text"      : '''
            resource "aws_internet_gateway" "{}" {{
                vpc_id = aws_vpc.{}.id
            }}
            '''.format(name, vpc_name)
        }
    
    def gen_subnet(self, name, vpc_name, cidr, az, public=True):
        public_ip = "false"
        if public: public_ip = "true"
        return {
            "kind"      : "subnet",
            "name"      : name,
            "vpc_name"  : vpc_name,
            "cidr"      : cidr,
            "az"        : az,
            "public"    : public,
            "text"      : '''
            resource "aws_subnet" "{}" {{
                vpc_id                  = aws_vpc.{}.id
                cidr_block              = "{}"
                availability_zone       = "{}"
                map_public_ip_on_launch = {}
            }}
            '''.format(name, vpc_name, cidr, az, public_ip)
        }

    def gen_eip(self, name, depend_igw_name, vpc=True):
        in_vpc = "false"
        if vpc: in_vpc = "true"
        return {
            "kind"  : "eip",
            "name"  : name,
            "vpc"   : vpc,
            "depend": depend_igw_name,
            "text"  : '''
            resource "aws_eip" "{}" {{
                vpc         = {}
                depends_on  = [aws_internet_gateway.{}]
            }}
            '''.format(name, in_vpc, depend_igw_name)
        }

    def gen_natgw(self, name, eip_name, subnet_name):
        return {
            "kind"          : "natgw",
            "name"          : name,
            "eip_name"      : eip_name,
            "subnet_name"   : subnet_name,
            "text"          : '''
            resource "aws_nat_gateway" "{}" {{
                allocation_id   = aws_eip.{}.id
                subnet_id       = aws_subnet.{}.id
            }}
            '''.format(name, eip_name, subnet_name)
        }

    def gen_route_table(self, name, vpc_name, route_cidr, igw_name=None, natgw_name=None):
        if (not (igw_name or natgw_name)) or (igw_name and natgw_name): raise ValueError
        
        text = '''
        resource "aws_route_table" "{}" {{
            vpc_id = aws_vpc.{}.id
            route {{
                cidr_block = "{}"
                nat_gateway_id = aws_nat_gateway.{}.id
            }}
        }}
        '''.format(name, vpc_name, route_cidr, natgw_name)
       
        if igw_name: text = '''
            resource "aws_route_table" "{}" {{
                vpc_id = aws_vpc.{}.id
                route {{
                    cidr_block = "{}"
                    gateway_id = aws_internet_gateway.{}.id
                }}
            }}
        '''.format(name, vpc_name, route_cidr, igw_name)

        return {
            "kind"      : "route_table",
            "name"      : name,
            "vpc_name"  : vpc_name,
            "route_cidr": route_cidr,
            "igw_name"  : igw_name,
            "natgw_name": natgw_name,
            "text"      : text
        }

    def gen_route_table_association(self, name, subnet_name, route_table_name):
        return {
            "kind"              : "route_table_association",
            "name"              : name,
            "subnet_name"       : subnet_name,
            "route_table_name"  : route_table_name,
            "text"              : '''
            resource "aws_route_table_association" "{}" {{
                subnet_id       = aws_subnet.{}.id
                route_table_id  = aws_route_table.{}.id
            }}
            '''.format(name, subnet_name, route_table_name)
        }
    
    def gen_security_group(self, name, vpc_name, route):
        text = '''
        resource "aws_security_group" "{}" {{
            name    = "{}"
            vpc_id  = aws_vpc.{}.id
     
        '''.format(name, name, vpc_name)

        for entry in route:
            
            blocks = "["

            for block in entry["cidr_blocks"]:
                blocks += '''"{}",'''.format(block)

            blocks = blocks[:-1] + "]"

            text += '''
                {} {{
                    from_port   = {}
                    to_port     = {}
                    protocol    = "{}"
                    cidr_blocks = {}
                }}
            '''.format(entry["direction"], entry["from"], entry["to"], entry["protocol"], blocks)
        
        text += '''
        }}
        '''
        
        return {
            "kind"      : "security_group",
            "name"      : name,
            "vpc_name"  : vpc_name,
            "route"     : route,
            "text"      : text
        }
        
    def gen_ec2(self, name, instance_type, ami, security_group_name, subnet_name, public=True):
        public_ip = "false"
        if public: public_ip = "true"

        return {
            "kind"                  : "ec2",
            "name"                  : name,
            "instance_type"         : instance_type,
            "ami"                   : ami,
            "security_group_name"   : security_group_name,
            "subnet_name"           : subnet_name,
            "public"                : public,
            "text"                  : '''
            resource "aws_instance" "{}" {{
                instance_type               = "{}"
                ami                         = "{}"
                key_name                    = var.key_name
                vpc_security_group_ids      = [aws_security_group.{}.id]
                subnet_id                   = aws_subnet.{}.id
                associate_public_ip_address = {}
            }}
            '''.format(name, instance_type, ami, security_group_name, subnet_name, public_ip)
        }

    def gen_alb_target_group(self, name, port, protocol, vpc_name, health_port):
        return {
            "kind"          : "alb_target_group",
            "name"          : name,
            "port"          : port,
            "protocol"      : protocol,
            "vpc_name"      : vpc_name,
            "health_port"   : health_port,
            "text"          : '''
            resource "aws_alb_target_group" "{}" {{
                name    = "{}"
                port    = {}
                protocol= "{}"
                vpc_id  = aws_vpc.{}.id

                health_check {{
                    healthy_threshold   = 5
                    unhealthy_threashold= 3
                    timeout             = 5
                    path                = var.target_group_path
                    interval            = 30
                    port                = {}
                }}
            }}
            '''.format(name, name, port, protocol, vpc_name, health_port)
        }
    
    def gen_alb_target_group_attachment(self, name, target_group_name, target_name, port):
        return {
            "kind"              : "alb_target_group_attachment",
            "name"              : name,
            "target_group_name" : target_group_name,
            "target_name"       : target_name,
            "port"              : port,
            "text"              : '''
            resource "aws_alb_target_group_attachment" "{}" {{
                target_group_arn    = aws_alb_target_group.{}.arn
                target_id           = aws_instance.{}.id
                port                = {}
            }}
            '''.format(name, target_group_name, target_name, port)
        }

    def gen_load_balancer(self, name, load_balancer_type, subnets_names, security_group_name, internal=True):
        internal_text = "false"
        if internal: internal_text = "true"

        subnets = "["
        
        for name in subnets_names:
            subnets += "aws_subnet.{}.id,".format(name)
        subnets = subnets[:-1] + "]"

        text = '''
        resource "aws_lb" "{}" {{
            name                = "{}"
            internal            = {}
            load_balancer_type  = "{}"
            subnets             = {}
            security_groups     = [aws_security_group.{}.id]
        }}
        '''.format(name, name, internal_text, load_balancer_type, subnets, security_group_name)
        
        return {
            "kind"                  : "load_balancer",
            "name"                  : name,
            "type"                  : type,
            "internal"              : internal,
            "subnet_names"          : subnets_names,
            "security_group_name"   : security_group_name,
            "text"                  : text
        }

    def gen_rds(self, name, security_group_name):
        return {
            "kind"                  : "rds",
            "name"                  : name,
            "security_group_name"   : security_group_name,
            "text"                  : '''
            resource "aws_db_instance" "{}" {{
                allocated_storage       = 20
                engine                  = "mysql"
                engine_version          = "5.7.26"
                instance_class          = "db.t2.micro"
                username                = var.db_username
                password                = var.db_password
                port                    = var.db_port
                vpc_security_group_ids  = [aws_security_group.{}.id]
                skip_final_snapshot     = true
                multi_az                = true
            }}
            '''.format(name, security_group_name)
        }

    def gen_launch_template(self, name, ami, az):
        return {
            "kind"  : "launch_template",
            "name"  : name,
            "ami"   : ami,
            "az"    : az,
            "text"  : '''
            resource "aws_launch_template" "{}" {{
                name            = "{}"
                image_id        = "{}"
                instance_type   = "t2.micro"

                placement {{
                    availability_zone   = "{}"
                }}
            }}
            '''.format(name, name, ami, az)
        }

    def gen_autoscaling_group(self, name, azs, launch_template_name):
        
        az_list = "["

        for az in azs:
            az_list += '''"{}",'''.format(az)

        az_list = az_list[:-1] + "]"

        return {
            "kind"                  : "autoscaling_group",
            "name"                  : name,
            "azs"                   : azs,
            "launch_template_name"  : launch_template_name,
            "text"                  : '''
            resource "aws_autoscaling_group" "{}" {{
                name                        = "{}"
                desired_capacity            = 4
                max_size                    = 2
                min_size                    = 1
                health_check_grace_period   = 300
                health_check_type           = "ELB"
                availability_zones          = {}

                launch_template {{
                    id      = aws_launch_template.{}.id
                    version = "latest"
                }}
            }}
            '''.format(name, name, az_list, launch_template_name)
        }