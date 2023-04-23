data "aws_caller_identity" "current" {}

variable "project_id" {
  description = "Overall project name"
  type        = string
  default     = "discord-diffusion"
}

variable "unique_id" {
  description = "Unique identifier for this project"
  type        = string
  default     = "prod"
}

variable "huggingface_username" {
  description = "Username to the website hugging face. Used to download models."
  type        = string
}

variable "huggingface_password" {
  description = "Password to the website hugging face. Used to download models."
  type        = string
}

variable "vpc_id" {
  description = "Pre-exisiting VPC ARN"
  type        = string
}
