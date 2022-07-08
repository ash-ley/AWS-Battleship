module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "battleship-vpc"
  cidr = "10.10.0.0/16"

  azs            = ["eu-west-1b"]
  public_subnets = ["10.10.1.0/24"]

  enable_nat_gateway = false
  enable_vpn_gateway = false

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

resource "aws_vpc_endpoint" "ssm" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.eu-west-1.ssm"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [module.vpc.public_subnets[0]]

  security_group_ids = [
    aws_security_group.this.id
  ]
}