# Manual EC2 Instance Launch Script (PowerShell)
# Use this when Terraform is blocked by organizational policies

$ErrorActionPreference = "Stop"

Write-Host "[*] Launching EC2 Instance with manual AWS CLI..." -ForegroundColor Cyan

# Configuration
$AwsRegion = "us-east-1"
$ProjectName = "emotion-detector"
$InstanceType = "t3.large"
$KeyPairName = "emotion-detector-key-20260329"
$SubnetId = "subnet-050c1e32d2e071fe4"
$SgId = "sg-087551163b2814c02"
$IamInstanceProfile = "emotion-detector-ec2-profile"
$VolumeSize = 30
$EcrAccountId = "767397965014"

# Get latest Amazon Linux 2023 AMI
Write-Host "[*] Finding latest AL2023 AMI..." -ForegroundColor Cyan
$AmiId = (aws ec2 describe-images `
  --region $AwsRegion `
  --owners amazon `
  --filters "Name=name,Values=al2023-ami-*-x86_64" "Name=virtualization-type,Values=hvm" `
  --query "sort_by(Images, &CreationDate)[-1].ImageId" `
  --output text)

Write-Host "[*] Using AMI: $AmiId" -ForegroundColor Cyan

# Read and substitute user_data script
$UserDataFile = ".\user_data.sh.tpl"
if (-not (Test-Path $UserDataFile)) {
    Write-Host "ERROR: $UserDataFile not found" -ForegroundColor Red
    exit 1
}

$UserData = (Get-Content $UserDataFile -Raw) `
    -replace '\$\{aws_region\}', $AwsRegion `
    -replace '\$\{ecr_repo_url\}', "$EcrAccountId.dkr.ecr.$AwsRegion.amazonaws.com/$ProjectName" `
    -replace '\$\{image_tag\}', "latest"

# Base64 encode user data
$UserDataBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($UserData))

# Launch instance
Write-Host "[*] Launching instance..." -ForegroundColor Cyan
$InstanceId = (aws ec2 run-instances `
  --region $AwsRegion `
  --image-id $AmiId `
  --instance-type $InstanceType `
  --key-name $KeyPairName `
  --subnet-id $SubnetId `
  --security-group-ids $SgId `
  --iam-instance-profile "Name=$IamInstanceProfile" `
  --user-data $UserDataBase64 `
  --block-device-mappings "DeviceName=/dev/xvda,Ebs={VolumeSize=$VolumeSize,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}" `
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$ProjectName-ec2},{Key=Project,Value=$ProjectName}]" `
  --query "Instances[0].InstanceId" `
  --output text)

Write-Host "[+] Instance created: $InstanceId" -ForegroundColor Green
Write-Host "[*] Waiting for instance to get public IP..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Get public IP
$PublicIp = (aws ec2 describe-instances `
  --region $AwsRegion `
  --instance-ids $InstanceId `
  --query "Reservations[0].Instances[0].PublicIpAddress" `
  --output text)

Write-Host "[+] Public IP: $PublicIp" -ForegroundColor Green
Write-Host "[+] Application URL: http://$PublicIp" -ForegroundColor Green
Write-Host ""
Write-Host "SSH Access:" -ForegroundColor Yellow
Write-Host "  ssh -i emotion-detector-key-20260329.pem ec2-user@$PublicIp" -ForegroundColor Gray
Write-Host ""
Write-Host "User Data logs:" -ForegroundColor Yellow
Write-Host "  ssh -i emotion-detector-key-20260329.pem ec2-user@$PublicIp sudo tail -f /var/log/user_data.log" -ForegroundColor Gray
