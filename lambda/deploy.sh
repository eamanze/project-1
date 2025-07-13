#!/bin/bash
set -e

AWS_REGION=us-east-2
ECR_REPO=lambda-cdn-callback
IMAGE_NAME=lambda-cdn-callback
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo ">>> Logging in to ECR..."
aws ecr describe-repositories --repository-names $ECR_REPO >/dev/null 2>&1 ||   aws ecr create-repository --repository-name $ECR_REPO

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo ">>> Building image..."
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

echo ">>> Updating Lambda function..."
aws lambda update-function-code   --function-name lambda-cdn-callback   --image-uri $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest   --region $AWS_REGION

echo ">>> Done. Lambda function updated successfully."
