#!/bin/bash
set -euo pipefail

# Manual EC2 Instance Launch Script
# Use this when Terraform is blocked by organizational policies

echo "[*] Launching EC2 Instance with manual AWS CLI..."

# Configuration
AWS_REGION="us-east-1"
PROJECT_NAME="emotion-detector"
INSTANCE_TYPE="t3.large"
KEY_PAIR_NAME="emotion-detector-key-20260329"
SUBNET_ID="subnet-050c1e32d2e071fe4"
SG_ID="sg-087551163b2814c02"
IAM_INSTANCE_PROFILE="emotion-detector-ec2-profile"
VOLUME_SIZE=30

# Get latest Amazon Linux 2023 AMI
echo "[*] Finding latest AL2023 AMI..."
AMI_ID=$(aws ec2 describe-images \
  --region "$AWS_REGION" \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-*-x86_64" "Name=virtualization-type,Values=hvm" \
  --query "sort_by(Images, &CreationDate)[-1].ImageId" \
  --output text)

echo "[*] Using AMI: $AMI_ID"

# Read user_data script (URL-encoded or base64)
USER_DATA_FILE="./user_data.sh.tpl"
if [ ! -f "$USER_DATA_FILE" ]; then
  echo "ERROR: $USER_DATA_FILE not found" >&2
  exit 1
fi

# Substitute template variables
USER_DATA=$(cat "$USER_DATA_FILE" \
  | sed "s|\${aws_region}|$AWS_REGION|g" \
  | sed "s|\${ecr_repo_url}|767397965014.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME|g" \
  | sed "s|\${image_tag}|latest|g")

# Launch instance
echo "[*] Launching instance..."
INSTANCE_ID=$(aws ec2 run-instances \
  --region "$AWS_REGION" \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_PAIR_NAME" \
  --subnet-id "$SUBNET_ID" \
  --security-group-ids "$SG_ID" \
  --iam-instance-profile "Name=$IAM_INSTANCE_PROFILE" \
  --user-data "$(echo "$USER_DATA" | base64 -w0)" \
  --block-device-mappings "DeviceName=/dev/xvda,Ebs={VolumeSize=$VOLUME_SIZE,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-ec2},{Key=Project,Value=$PROJECT_NAME}]" \
  --query "Instances[0].InstanceId" \
  --output text)

echo "[+] Instance created: $INSTANCE_ID"
echo "[*] Waiting for instance to get public IP..."
sleep 10

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --region "$AWS_REGION" \
  --instance-ids "$INSTANCE_ID" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text)

echo "[+] Public IP: $PUBLIC_IP"
echo "[+] Application URL: http://$PUBLIC_IP"
echo ""
echo "SSH Access:"
echo "  ssh -i emotion-detector-key-20260329.pem ec2-user@$PUBLIC_IP"
echo ""
echo "User Data logs:"
echo "  ssh -i emotion-detector-key-20260329.pem ec2-user@$PUBLIC_IP sudo tail -f /var/log/user_data.log"
