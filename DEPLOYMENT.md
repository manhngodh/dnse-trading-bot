# Terraform Docker Deployment Instructions

This project includes a GitHub Actions workflow for automatic deployment to the server at `173.249.7.24` using Terraform and Docker.

## Prerequisites

The target server should have:

- Docker installed
- Docker Compose installed
- SSH access configured

To enable the automated deployment, you need to set up the following secrets in your GitHub repository:

### Required GitHub Secrets

1. `SSH_PRIVATE_KEY`: The SSH private key used to connect to the deployment server
2. `DEPLOY_USER`: The username to use when connecting to the deployment server
3. `DEPLOY_PATH`: The path on the server where the application should be deployed (default: `/opt/dnse-trading-bot`)

## How to Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings"
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click on "New repository secret" to add each of the required secrets

## Deployment Architecture

The deployment uses:

- Terraform to manage the infrastructure as code
- Docker for containerization
- Docker Compose for container orchestration
- GitHub Actions for CI/CD pipeline automation

The application is deployed as two Docker containers:

1. Backend (Flask API)
2. Frontend (UI served by Nginx)

## Manual Deployment

If you prefer to deploy manually, you can use the following commands:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd dnse-trading-bot

# 2. Copy files to the server
rsync -avz --exclude '.git' --exclude 'node_modules' . your-username@173.249.7.24:/opt/dnse-trading-bot/

# 3. SSH into the server and deploy using Docker Compose
ssh your-username@173.249.7.24
cd /opt/dnse-trading-bot/
docker-compose down || true
docker-compose up -d --build
```

## Manual Terraform Deployment

To deploy using Terraform manually:

```bash
# 1. Navigate to the terraform directory
cd terraform

# 2. Copy and edit the terraform.tfvars.example file
cp terraform.tfvars.example terraform.tfvars
# Edit the terraform.tfvars file with your SSH username and private key path

# 3. Initialize Terraform
terraform init

# 4. Plan and apply
terraform plan -out=tfplan
terraform apply tfplan
```

## Accessing the Application

Once deployed, the application will be accessible at:

- Frontend: `http://173.249.7.24`
- Backend API: `http://173.249.7.24/api`

## Monitoring and Logs

To check the status of your Docker containers:

```bash
ssh your-username@173.249.7.24
docker ps
```

To view logs:

```bash
# Backend logs
docker logs dnse-trading-bot_backend_1

# Frontend logs
docker logs dnse-trading-bot_frontend_1
```

## Troubleshooting

If you encounter any issues with the deployment:

1. Check the logs in the GitHub Actions workflow
2. Inspect the Docker container logs on the server
3. Verify that Docker and Docker Compose are properly installed
4. Ensure the server has necessary permissions to run Docker
5. Check network connectivity between containers using `docker network inspect app-network`
