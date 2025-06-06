terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    remote = {
      source  = "tenstad/remote"
      version = "~> 0.1.1"
    }
  }
}

# Define the SSH connection
provider "remote" {
  alias  = "dnse_server"
  host   = "173.249.7.24"
  user   = var.ssh_user
  private_key = file(var.private_key_path)
}

# Create the deployment directory
resource "remote_file" "create_directory" {
  provider   = remote.dnse_server
  content    = ""
  path       = "${var.remote_dir}/create_dir_placeholder"
  
  provisioner "remote-exec" {
    inline = [
      "mkdir -p ${var.remote_dir}",
    ]
  }
}

# Copy Docker Compose file to the server
resource "remote_file" "docker_compose" {
  provider   = remote.dnse_server
  content    = file("${path.module}/docker-compose.yml")
  path       = "${var.remote_dir}/docker-compose.yml"
  depends_on = [remote_file.create_directory]
}

# Create backend directory and copy files
resource "null_resource" "copy_backend" {
  depends_on = [remote_file.docker_compose]
  
  provisioner "local-exec" {
    command = <<EOT
      tar -czf backend.tar.gz -C ./backend .
      scp -i ${var.private_key_path} backend.tar.gz ${var.ssh_user}@173.249.7.24:${var.remote_dir}/
      ssh -i ${var.private_key_path} ${var.ssh_user}@173.249.7.24 "mkdir -p ${var.remote_dir}/backend && tar -xzf ${var.remote_dir}/backend.tar.gz -C ${var.remote_dir}/backend && rm ${var.remote_dir}/backend.tar.gz"
      rm backend.tar.gz
    EOT
  }
}

# Create UI directory and copy files
resource "null_resource" "copy_ui" {
  depends_on = [remote_file.docker_compose]
  
  provisioner "local-exec" {
    command = <<EOT
      tar -czf ui.tar.gz -C ./ui .
      scp -i ${var.private_key_path} ui.tar.gz ${var.ssh_user}@173.249.7.24:${var.remote_dir}/
      ssh -i ${var.private_key_path} ${var.ssh_user}@173.249.7.24 "mkdir -p ${var.remote_dir}/ui && tar -xzf ${var.remote_dir}/ui.tar.gz -C ${var.remote_dir}/ui && rm ${var.remote_dir}/ui.tar.gz"
      rm ui.tar.gz
    EOT
  }
}

# Deploy with Docker Compose
resource "null_resource" "deploy" {
  depends_on = [null_resource.copy_backend, null_resource.copy_ui]
  
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(var.private_key_path)
      host        = "173.249.7.24"
    }
    
    inline = [
      "cd ${var.remote_dir}",
      "docker-compose -f docker-compose.yml down || true",
      "docker-compose -f docker-compose.yml up -d --build"
    ]
  }
}
