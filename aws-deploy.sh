#!/bin/bash

# CountryCompare AWS Deployment Script
# This script deploys the CountryCompare application to AWS using Elastic Beanstalk, RDS, and S3

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="countrycompare"
ENVIRONMENT_NAME="countrycompare-prod"
REGION="us-east-1"
INSTANCE_TYPE="t3.medium"
DB_INSTANCE_CLASS="db.t3.micro"
DB_NAME="countrycompare"
DB_USERNAME="postgres"
DB_PASSWORD="$(openssl rand -base64 32)"
S3_BUCKET_NAME="${APP_NAME}-assets-$(date +%s)"

echo -e "${BLUE}🚀 Starting CountryCompare AWS Deployment${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${RED}❌ EB CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Create S3 bucket for static assets
echo -e "${YELLOW}📦 Creating S3 bucket for static assets...${NC}"
aws s3 mb s3://${S3_BUCKET_NAME} --region ${REGION}
aws s3api put-bucket-cors --bucket ${S3_BUCKET_NAME} --cors-configuration '{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "HEAD"],
            "AllowedHeaders": ["*"]
        }
    ]
}'

# Create RDS PostgreSQL instance
echo -e "${YELLOW}🗄️  Creating RDS PostgreSQL instance...${NC}"
aws rds create-db-instance \
    --db-instance-identifier ${APP_NAME}-db \
    --db-instance-class ${DB_INSTANCE_CLASS} \
    --engine postgres \
    --engine-version 15.4 \
    --master-username ${DB_USERNAME} \
    --master-user-password ${DB_PASSWORD} \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids default \
    --backup-retention-period 7 \
    --storage-encrypted \
    --region ${REGION} \
    --db-name ${DB_NAME}

echo -e "${YELLOW}⏳ Waiting for RDS instance to be available (this may take 10-15 minutes)...${NC}"
aws rds wait db-instance-available --db-instance-identifier ${APP_NAME}-db --region ${REGION}

# Get RDS endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier ${APP_NAME}-db \
    --region ${REGION} \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo -e "${GREEN}✅ RDS instance created: ${DB_ENDPOINT}${NC}"

# Initialize Elastic Beanstalk application
echo -e "${YELLOW}🌱 Initializing Elastic Beanstalk application...${NC}"
cd backend

if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    eb init ${APP_NAME} --region ${REGION} --platform "Python 3.11 running on 64bit Amazon Linux 2023"
fi

# Create environment configuration
cat > .elasticbeanstalk/config.yml << EOF
branch-defaults:
  default:
    environment: ${ENVIRONMENT_NAME}
    group_suffix: null
global:
  application_name: ${APP_NAME}
  branch: null
  default_ec2_keyname: null
  default_platform: Python 3.11 running on 64bit Amazon Linux 2023
  default_region: ${REGION}
  include_git_submodules: true
  instance_profile: null
  platform_name: null
  platform_version: null
  profile: null
  repository: null
  sc: git
  workspace_type: Application
EOF

# Create environment
echo -e "${YELLOW}🏗️  Creating Elastic Beanstalk environment...${NC}"
eb create ${ENVIRONMENT_NAME} \
    --instance-type ${INSTANCE_TYPE} \
    --platform "Python 3.11 running on 64bit Amazon Linux 2023" \
    --region ${REGION} \
    --envvars \
    "DATABASE_URL=postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME}" \
    "SECRET_KEY=$(openssl rand -base64 32)" \
    "FLASK_ENV=production" \
    "S3_BUCKET_NAME=${S3_BUCKET_NAME}" \
    "AWS_REGION=${REGION}"

# Deploy backend
echo -e "${YELLOW}🚀 Deploying backend to Elastic Beanstalk...${NC}"
eb deploy

# Get backend URL
BACKEND_URL=$(eb status --region ${REGION} | grep "CNAME" | awk '{print $2}')

echo -e "${GREEN}✅ Backend deployed: https://${BACKEND_URL}${NC}"

# Deploy frontend to S3
echo -e "${YELLOW}🌐 Building and deploying frontend...${NC}"
cd ../frontend

# Install dependencies and build
npm install
npm run build

# Upload to S3
aws s3 sync dist/ s3://${S3_BUCKET_NAME} --region ${REGION}

# Configure S3 bucket for static website hosting
aws s3 website s3://${S3_BUCKET_NAME} --index-document index.html --error-document index.html

# Get S3 website URL
FRONTEND_URL="http://${S3_BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"

echo -e "${GREEN}✅ Frontend deployed: ${FRONTEND_URL}${NC}"

# Create CloudFront distribution (optional)
echo -e "${YELLOW}☁️  Creating CloudFront distribution for better performance...${NC}"
cat > cloudfront-config.json << EOF
{
    "CallerReference": "${APP_NAME}-$(date +%s)",
    "Comment": "CountryCompare Frontend Distribution",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${S3_BUCKET_NAME}",
                "DomainName": "${S3_BUCKET_NAME}.s3-website-${REGION}.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${S3_BUCKET_NAME}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config file://cloudfront-config.json \
    --query 'Distribution.Id' \
    --output text \
    --region ${REGION})

echo -e "${GREEN}✅ CloudFront distribution created: ${DISTRIBUTION_ID}${NC}"

# Cleanup
rm cloudfront-config.json

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "  Backend URL: https://${BACKEND_URL}"
echo -e "  Frontend URL: ${FRONTEND_URL}"
echo -e "  Database: ${DB_ENDPOINT}"
echo -e "  S3 Bucket: ${S3_BUCKET_NAME}"
echo -e "  CloudFront: ${DISTRIBUTION_ID}"
echo -e "  Database Password: ${DB_PASSWORD}"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "  1. Save the database password securely: ${DB_PASSWORD}"
echo -e "  2. Update your domain DNS to point to the CloudFront distribution"
echo -e "  3. Configure SSL certificate for your custom domain"
echo -e "  4. Set up monitoring and alerts in AWS CloudWatch"
echo ""
echo -e "${GREEN}🚀 Your CountryCompare application is now live!${NC}"
