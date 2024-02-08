import boto3

# Prompt for user inputs
region = input("Enter the AWS region (e.g., us-east-2): ")
cluster = input("Enter the cluster name (e.g., prod): ")
task_arn = input("Enter the task ARN (e.g., arn:aws:ecs:us-east-2:123456789012:task/prod/unique_task_id): ")
container_name = input("Enter the container name (e.g., prod-backend-web): ")
command_to_execute = input("Enter the command to execute (e.g., /bin/bash): ")

# Initialize the boto3 ECS client
ecs_client = boto3.client('ecs', region_name=region)

# Execute the command
response = ecs_client.execute_command(
    cluster=cluster,
    task=task_arn,
    container=container_name,
    command=command_to_execute,
    interactive=True
)

print(response)

