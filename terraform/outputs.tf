output "app_url" {
  description = "URL where the application is accessible"
  value       = "http://173.249.7.24"
}

output "deployment_path" {
  description = "Path where the application is deployed"
  value       = var.remote_dir
}
