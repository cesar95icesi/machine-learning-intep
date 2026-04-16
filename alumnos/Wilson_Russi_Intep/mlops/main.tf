# ============================================
# Clase 7 - Despliegue de Modelo ML en AWS
# Lambda + API Gateway con Terraform
# ============================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# ── Variables ──
variable "region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "ml-fraude"
}

# ── Data: cuenta actual ──
data "aws_caller_identity" "current" {}

# ── S3 Bucket: almacena paquete Lambda ──
resource "aws_s3_bucket" "ml_bucket" {
  bucket        = "${var.project_name}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = { Name = "${var.project_name}-bucket" }
}

# ── IAM Role para Lambda ──
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# ── Lambda Function ──
resource "aws_lambda_function" "fraud_detector" {
  function_name = "${var.project_name}-detector"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 512

  s3_bucket = aws_s3_bucket.ml_bucket.id
  s3_key    = "lambda/lambda_package.zip"

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_s3
  ]
}

# ── API Gateway REST API ──
resource "aws_api_gateway_rest_api" "fraud_api" {
  name        = "${var.project_name}-api"
  description = "API para prediccion de fraude con ML"
}

# Recurso /predecir
resource "aws_api_gateway_resource" "predecir" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id
  parent_id   = aws_api_gateway_rest_api.fraud_api.root_resource_id
  path_part   = "predecir"
}

# Metodo POST sin autenticacion
resource "aws_api_gateway_method" "post_predecir" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_api.id
  resource_id   = aws_api_gateway_resource.predecir.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integracion con Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.fraud_api.id
  resource_id             = aws_api_gateway_resource.predecir.id
  http_method             = aws_api_gateway_method.post_predecir.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fraud_detector.invoke_arn
}

# Permiso para que API Gateway invoque Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fraud_detector.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fraud_api.execution_arn}/*/*"
}

# Despliegue del API
resource "aws_api_gateway_deployment" "fraud_deployment" {
  rest_api_id = aws_api_gateway_rest_api.fraud_api.id

  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# Stage "prod"
resource "aws_api_gateway_stage" "prod" {
  rest_api_id   = aws_api_gateway_rest_api.fraud_api.id
  deployment_id = aws_api_gateway_deployment.fraud_deployment.id
  stage_name    = "prod"
}

# ── Outputs ──
output "s3_bucket_name" {
  description = "Nombre del bucket S3"
  value       = aws_s3_bucket.ml_bucket.id
}

output "lambda_function_name" {
  description = "Nombre de la funcion Lambda"
  value       = aws_lambda_function.fraud_detector.function_name
}

output "api_url" {
  description = "URL del endpoint de prediccion"
  value       = "${aws_api_gateway_stage.prod.invoke_url}/predecir"
}
