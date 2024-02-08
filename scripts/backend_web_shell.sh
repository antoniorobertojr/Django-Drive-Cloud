#!/bin/bash

# List tasks and capture the first task ARN
TASK_ID=$(aws ecs list-tasks --cluster prod --service-name prod-backend-web --query 'taskArns[0]' --output text --region us-east-2)

# Check if TASK_ID is empty
if [ "$TASK_ID" == "None" ] || [ -z "$TASK_ID" ]; then
    echo "No tasks found for the service prod-backend-web in the cluster prod. Ensure the service and cluster names are correct and that there are running tasks."
    exit 1
fi

# Extract the task ID from the task ARN
TASK_ID=$(echo $TASK_ID | awk '{split($0,a,"/"); print a[3]}')

# Execute command in the task
if [ ! -z "$TASK_ID" ]; then
    aws ecs execute-command --task $TASK_ID --command "bash" --interactive --cluster prod --region us-east-2
else
    echo "Error: Task ID could not be determined."
fi

