# AWS Integration Assistant

**Automate AWS Lambda CORS configuration in seconds.**

Stop wasting hours debugging CORS errors. This CLI tool scans your AWS account, detects CORS issues, and fixes them automatically.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/yourusername/AWS_assistance/releases)

---

## The Problem

You're building a web app with AWS Lambda. Your frontend can't connect to your backend:
```
Access to fetch at 'https://xxx.lambda-url.us-west-2.on.aws/' 
from origin 'https://myapp.com' has been blocked by CORS policy
```

You spend hours:
- Googling CORS documentation
- Clicking through AWS Console
- Testing different configurations
- Still getting errors

**There has to be a better way.**

---

## The Solution
```bash
# Scan your AWS account
aws-assistant scan

# Fix CORS issues automatically
aws-assistant fix-cors MyFunction --origin https://myapp.com

# Done! Your app works now.
```

**That's it. 30 seconds instead of 30 minutes.**

---

## Features

### v1.0 (Current)

 **Lambda Function URL CORS**
- Automatic detection across all AWS regions
- One-command fix with proper configuration
- Smart origin detection from your project files

 **API Gateway HTTP API CORS**
- Detects Lambda functions behind HTTP APIs
- Configures CORS automatically
- Supports multiple origins

 **Smart Origin Detection**
- Reads from package.json
- Reads from .env files
- Supports Vercel, React, Next.js, Vite, Vue

 **Multi-Region Support**
- Scans all AWS regions automatically
- Finds functions wherever they are
- No manual region specification needed

 **Developer-Friendly**
- Clear, colorful output
- Helpful error messages
- Example code generation

---

## Installation

### Requirements
- Python 3.8 or higher
- AWS credentials configured

### Install
```bash
# Clone the repository
git clone https://github.com/yourusername/AWS_assistance.git
cd AWS_assistance

# Install in development mode
pip install -e .
```

---

## Quick Start

### 1. Configure AWS Credentials

Make sure you have AWS credentials set up:
```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

### 2. Scan Your Account
```bash
aws-assistant scan
```

You'll see a table showing all your Lambda functions and their CORS status:
```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Function Name      ┃ Region    ┃ Runtime    ┃ Access Type   ┃ CORS Status    ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ myFunction         │ us-west-2 │ nodejs20.x │ Function URL  │ NOT CONFIGURED │
│ apiFunction        │ us-west-2 │ python3.12 │ HTTP API      │ CONFIGURED     │
└────────────────────┴───────────┴────────────┴───────────────┴────────────────┘
```

### 3. Fix CORS Issues

**Automatic origin detection:**
```bash
aws-assistant fix-cors myFunction
```

The tool will detect your app's origin from:
- `package.json` (homepage field)
- `.env` files (REACT_APP_URL, NEXT_PUBLIC_URL, etc.)
- `vercel.json`

**Manual origin specification:**
```bash
aws-assistant fix-cors myFunction --origin https://myapp.com
```

**Multiple origins:**
```bash
aws-assistant fix-cors myFunction --origin http://localhost:3000 --origin https://myapp.com
```

**Development (wildcard):**
```bash
aws-assistant fix-cors myFunction --wildcard
```
 **Warning:** Only use wildcard in development. Not recommended for production.

---

## Usage Examples

### Scenario 1: React App in Development
```bash
# Your React app runs on localhost:3000
# Fix CORS for local development
aws-assistant fix-cors myBackendFunction --origin http://localhost:3000
```

### Scenario 2: Production Deployment
```bash
# Your production app is at https://myapp.com
# Fix CORS for production
aws-assistant fix-cors myBackendFunction --origin https://myapp.com
```

### Scenario 3: Multiple Environments
```bash
# Support both local development and production
aws-assistant fix-cors myFunction \
  --origin http://localhost:3000 \
  --origin https://staging.myapp.com \
  --origin https://myapp.com
```

### Scenario 4: Function Behind API Gateway
```bash
# Your function is behind API Gateway HTTP API
# Tool detects this automatically and fixes both
aws-assistant fix-cors myFunction --target all --origin https://myapp.com
```

---

## Advanced Usage

### Target Specific Access Methods

If your Lambda has both Function URL and API Gateway:
```bash
# Fix only Function URL CORS
aws-assistant fix-cors myFunction --target url --origin https://myapp.com

# Fix only API Gateway CORS
aws-assistant fix-cors myFunction --target api --origin https://myapp.com

# Fix both
aws-assistant fix-cors myFunction --target all --origin https://myapp.com
```

### Specify Region
```bash
# If you know which region your function is in
aws-assistant fix-cors myFunction --region us-west-2 --origin https://myapp.com
```

---

## Required AWS Permissions

Your AWS credentials need these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionUrlConfig",
        "lambda:UpdateFunctionUrlConfig",
        "apigatewayv2:GetApis",
        "apigatewayv2:GetIntegrations",
        "apigatewayv2:UpdateApi",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## How It Works

### CORS Detection

1. **Scans all AWS regions** to find your Lambda functions
2. **Checks Function URL configuration** to see if CORS is enabled
3. **Scans API Gateway** (HTTP and REST APIs) to find connected Lambdas
4. **Reports CORS status** for each access method

### CORS Fixing

1. **Detects or prompts for allowed origins** from your project files
2. **Applies CORS configuration** via AWS API:
   - AllowOrigins: Your specified origins
   - AllowMethods: All HTTP methods
   - AllowHeaders: All headers
   - MaxAge: 24 hours
3. **Verifies the fix** and shows example code

### Smart Origin Detection

The tool automatically detects your app's URL from:

**package.json:**
```json
{
  "homepage": "https://myapp.com"
}
```

**.env files:**
```bash
REACT_APP_URL=https://myapp.com
NEXT_PUBLIC_URL=https://myapp.com
VITE_URL=https://myapp.com
```

**vercel.json:**
```json
{
  "env": {
    "NEXT_PUBLIC_URL": "https://myapp.com"
  }
}
```

---

## Known Limitations

### v1.0 Does NOT Support:

❌ **REST API CORS** - Manual configuration required (coming in v2.0)
❌ **Proxy Integration Detection** - Cannot detect if backend must return CORS headers
❌ **IAM Permission Fixing** - Only handles CORS (other features planned)
❌ **CloudFormation Integration** - Manual resource management only

### Current Workarounds:

**For REST APIs:**
1. Use AWS Console → API Gateway → Your API → CORS
2. Enable CORS manually
3. Deploy to stage

**For Proxy Integrations:**
If using Lambda proxy integration, your function must return CORS headers:
```python
# Python example
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': 'https://myapp.com',
        'Content-Type': 'application/json'
    },
    'body': json.dumps(your_data)
}
```

---

## Roadmap

### v2.0 (Planned)
-  Full REST API CORS support with automatic deployment
-  Proxy integration detection and guidance
-  Credential testing (verify permissions before scanning)

### v3.0 (Planned)
-  IAM permission detection and fixing
-  CloudFormation error diagnosis
-  AWS resource cost optimization suggestions

### Future Considerations
-  CloudWatch log analysis
-  API rate limiting detection
-  Security best practices scanner

---

## Troubleshooting

### "No AWS credentials found"

**Solution:** Configure AWS credentials:
```bash
aws configure
```

### "Function not found"

**Solution:** Make sure the function name is correct and you have permissions:
```bash
aws lambda list-functions --region us-west-2
```

### "CORS still not working"

**Check:**
1. Is your origin URL correct? (https vs http, www vs non-www)
2. Did you clear browser cache?
3. Is your Lambda behind a proxy integration? (Check AWS Console)
4. Are you testing from the correct origin?

### "Access Denied" errors

**Solution:** Add required permissions to your IAM user/role. See [Required AWS Permissions](#required-aws-permissions).

---

## Contributing

Contributions are welcome! 

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/AWS_assistance.git
cd AWS_assistance

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Author

**Tinsae** 
Built because I was tired of debugging CORS errors on my project.

---

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) (CLI framework)
- Styled with [Rich](https://rich.readthedocs.io/) (terminal formatting)
- Powered by [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (AWS SDK)

---

## Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/Tinaaaa111/AWS_assistance/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/Tinaaaa111/AWS_assistance/discussions)


---

## Star History

If this tool saved you time, please ⭐ star the repo!
