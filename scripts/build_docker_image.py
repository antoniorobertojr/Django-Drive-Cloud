import subprocess
import os
import sys

def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def main(aws_account_id, region, project_name):
    docker_image_name = f"{aws_account_id}.dkr.ecr.{region}.amazonaws.com/{project_name}-backend:latest"
    dockerfile_dir = "../"

    build_command = f"docker build {dockerfile_dir} -t {docker_image_name}"
    print(f"Building Docker image with command: {build_command}")
    run_command(build_command)

    # Login to ECR
    login_command = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{region}.amazonaws.com"
    print("Logging into Amazon ECR...")
    run_command(login_command)

    push_command = f"docker push {docker_image_name}"
    print(f"Pushing Docker image to ECR with command: {push_command}")
    run_command(push_command)
    print("Docker image pushed successfully.")

if __name__ == "__main__":
    if "AWS_ACCOUNT_ID" not in os.environ or "AWS_REGION" not in os.environ or "PROJECT_NAME" not in os.environ:
        print("AWS_ACCOUNT_ID, AWS_REGION and PROJECT_NAME environment variables must be set.")
        sys.exit(1)

    aws_account_id = os.environ["AWS_ACCOUNT_ID"]
    region = os.environ["AWS_REGION"]
    project_name = os.environ["PROJECT_NAME"]
    main(aws_account_id, region, project_name)

