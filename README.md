# django-drive-cloud

## Introduction

django-drive-cloud is a Django-based cloud storage solution similar to Google Drive, designed to allow users to create folders, upload files, and share them with specific permissions. This project is deployed on AWS, utilizing a range of services managed through Terraform to ensure scalable, secure, and efficient operations.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Infrastructure](#infrastructure)
- [Installation](#installation)
- [Usage](#usage)


## Features

- User authentication and authorization.
- Folder and file management.
- File sharing with granular permissions.
- Scalable cloud deployment with AWS and Terraform.

## Infrastructure

The infrastructure is defined and managed using Terraform, ensuring reproducible and scalable deployments. It includes:

- **Networking**: Setup with VPC, subnets, NAT Gateway, and Internet Gateway to secure and manage network traffic.
- **Application Load Balancer (ALB)**: Directs user traffic to the ECS (Elastic Container Service) instances for high availability and fault tolerance.
- **ECS**: Hosts the Django application in Docker containers, allowing for easy scaling and management.
- **RDS**: Provides a managed relational database service for storing application data.
- **S3 Bucket**: Stores media files uploaded by users, offering scalable and secure object storage.

## Installation

### Setting Up the Infrastructure with Terraform
Ensure you have Terraform installed on your machine.

Clone the project repository:
```
git clone https://github.com/juniormach96/Django-Drive-Cloud.git .
```

Navigate to the Terraform configuration directory:
```
cd aws-infrastructure
```

Initialize the Terraform environment:
```
terraform init
```

Apply the Terraform configuration. This step will output the Load Balancer's URL and the ECR repository URL, which you will need in the subsequent steps:
```
terraform apply
```

### Configuring Docker with AWS ECR
Retrieve an authentication token and authenticate your Docker client to your registry using the AWS CLI. Replace your-region with your AWS region and your-ecr-repo-name with the name of your ECR repository output by Terraform:

```
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-ecr-repo-url
```

Build your Docker image:
```
docker build -t django-file-manager-backend .
```

Tag your Docker image to prepare for pushing it to the ECR repository. Replace your-ecr-repo-url with your repository URL:

```
docker tag django-file-manager-backend:latest your-ecr-repo-url/django-file-manager-backend:latest
```

Push the Docker image to your ECR repository:
```
docker push your-ecr-repo-url/django-file-manager-backend:latest
```

### Finalizing the Setup
Discover the task name through the AWS CLI to use in subsequent commands:

```
aws ecs list-tasks --cluster your-cluster-name
```

SSH into your task
```
aws ecs execute-command \
  --region us-east-2 \
  --cluster prod \
  --task your-task-arn\
  --container prod-backend-web \
  --command "/bin/bash" \
  --interactive
```

Apply migrations:

```
python3 manage.py makemigrations
python3 manage.py migrate
```

Create the superuser for Django admin:
```
python3 manage.py createsuperuser
```


### Usage

After successfully installing and setting up `django-drive-cloud`, open a web browser and navigate to the Load Balancer's URL provided by the Terraform output during the installation process. Then, access the `api/docs` documentation to see the available endpoints.
