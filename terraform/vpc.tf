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