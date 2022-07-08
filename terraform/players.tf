resource "aws_instance" "players" {
  count                  = 2
  ami                    = "ami-0d71ea30463e0ff8d"
  instance_type          = "t2.micro"
  subnet_id              = module.vpc.public_subnets[0]
  key_name               = aws_key_pair.battleship.key_name
  iam_instance_profile   = aws_iam_instance_profile.this.name
  vpc_security_group_ids = [aws_security_group.this.id]
  user_data              = <<EOT
    #!/bin/bash
    amazon-linux-extras install epel -y
    yum update -y
    yum install python-pip -y
    pip3 install requests
    pip3 install boto3
    BUCKET_URL=${var.bucket_name}
    aws s3 cp s3://$BUCKET_URL/battleship.py /home/ec2-user/
    pip install requests
  EOT

  metadata_options {
    http_endpoint          = "enabled"
    instance_metadata_tags = "enabled"
  }

  depends_on = [
    aws_s3_bucket.game,
    aws_s3_object.this
  ]

  tags = {
    Name = "Player-${count.index + 1}"
  }
}

resource "aws_ssm_parameter" "battle_board" {
  count = 2
  name  = "/battleship/player-${count.index + 1}"
  type  = "String"
  value = file("${path.cwd}/../battleboard")
}

resource "aws_key_pair" "battleship" {
  key_name   = "player-key"
  public_key = var.public_key
}

resource "aws_sqs_queue" "player_queue" {
  name = "player-turn-queue"
}

resource "aws_s3_bucket" "game" {
  bucket = var.bucket_name
  tags = {
    Name = "Battleship Bucket"
  }
}

resource "aws_s3_bucket_acl" "this" {
  bucket = aws_s3_bucket.game.id
  acl    = "private"
}

resource "aws_s3_object" "this" {
  bucket = aws_s3_bucket.game.id
  key    = "battleship.py"
  source = "../battleship.py"
  etag   = filemd5("../battleship.py")
}