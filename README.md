# # AWS Integration Assistant

**Automate AWS Lambda CORS configuration in seconds.**

![Version](https://img.shields.io/badge/version-0.1.0--beta-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)

##  What it does

Automatically detects and fixes CORS configuration issues for AWS Lambda Function URLs.

**Current features (v0.1.0):**
-  Scan all Lambda functions across all AWS regions
-  Detect CORS configuration status
-  Auto-fix CORS for Lambda Function URLs
-  Generate React integration code

**Coming soon:**
-  API Gateway CORS support (v0.2.0 - this week!)
-  IAM permission detection & fixing (v0.3.0)
-  CloudFormation error diagnosis (v0.4.0)

##  Installation
```bash
git clone https://github.com/yourusername/AWS_assistance
cd AWS_assistance
pip install -e .
```

## 🔧 Quick Start

### Scan for CORS issues
```bash
aws-assistant scan
```

### Fix CORS on a function
```bash
aws-assistant fix-cors MyFunctionName
```

## 📋 Requirements

- Python 3.8+
- AWS credentials configured (`~/.aws/credentials`)
- AWS permissions:
  - `lambda:ListFunctions`
  - `lambda:GetFunctionUrlConfig`
  - `lambda:UpdateFunctionUrlConfig`

## 🎯 Use Cases

**Perfect for:**
- Developers using Lambda Function URLs
- Fixing "blocked by CORS policy" errors
- Serverless app development

**Not yet supported (coming in v0.2.0):**
- API Gateway CORS configuration

## 🛣️ Roadmap

- **Week 1 (Feb 11):** v0.1.0 - Function URL CORS ✅
- **Week 1 (Feb 14):** v0.2.0 - API Gateway CORS support
- **Week 2:** v0.3.0 - IAM permission automation
- **Week 3:** v0.4.0 - CloudFormation error diagnosis

## 🤝 Contributing

This is an early beta. Feedback and contributions welcome!

## 📄 License

MIT

## 🏗️ Built in Public

Follow the development journey: [@YourTwitter](#buildinpublic)

---

**Note:** This is a beta release. API Gateway support coming this week!AWS_assistance
CORS, IAM and AUTH fixer
