variable "ssh_user" {
  description = "SSH username for the remote server"
  type        = string
}

variable "private_key_path" {
  description = "Path to the private SSH key"
  type        = string
}

variable "remote_dir" {
  description = "Remote directory to deploy application"
  type        = string
  default     = "/opt/dnse-trading-bot"
}
