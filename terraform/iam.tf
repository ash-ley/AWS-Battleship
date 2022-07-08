resource "aws_iam_instance_profile" "this" {
  name = "game_ssm_profile"
  role = aws_iam_role.this.name
}

resource "aws_iam_role" "this" {
  name = "game_ssm_role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : {
      "Effect" : "Allow",
      "Principal" : { "Service" : "ec2.amazonaws.com" },
      "Action" : "sts:AssumeRole"
    }
  })
}

resource "aws_iam_policy" "ssm_parameter" {
  name = "ssm_parameter"
  path = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter*",
          "ssm:PutParameter*",
          "sqs:ListQueues",
          "sqs:ReceiveMessage",
          "sqs:SendMessage",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.ssm_parameter.arn
}