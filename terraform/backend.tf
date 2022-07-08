terraform {
  backend "s3" {
    bucket = "talentacademy-ashley-battleship-be"
    key    = "terraform.tfstates"
  }
}