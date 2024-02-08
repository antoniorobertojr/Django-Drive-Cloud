[
  {
    "name": "${name}",
    "image": "${image}",
    "essential": true,
    "links": [],
    "portMappings": [
      {
        "containerPort": 8000,
        "hostPort": 8000,
        "protocol": "tcp"
      }
    ],
    "command": ${jsonencode(command)},
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${log_group}",
        "awslogs-region": "${region}",
        "awslogs-stream-prefix": "${log_stream}"
      }
    },
    "environment": [
      {
        "name": "DATABASE_URL",
        "value": "postgresql://${rds_username}:${rds_password}@${rds_hostname}:5432/${rds_db_name}"
      },
      {
        "name": "DEFAULT_FILE_STORAGE",
        "value": "storages.backends.s3boto3.S3Boto3Storage"
      },
      {
        "name": "AWS_ACCESS_KEY_ID",
        "value": "${s3_access_key}"
      },
      {
        "name": "AWS_SECRET_ACCESS_KEY",
        "value": "${s3_secret_key}"
      },
      {
        "name": "AWS_STORAGE_BUCKET_NAME",
        "value": "${s3_media_bucket}"
      },
      {
        "name": "AWS_S3_REGION_NAME",
        "value": "${region}"
      },
      {
       "name": "AWS_S3_ENDPOINT_URL",
       "value": "https://${s3_media_bucket}.s3.${region}.amazonaws.com/"
      }
    ]
  }
]

