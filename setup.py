from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aws-integration-assistant",
    version="1.0.0",
    author="Tinsae",
    author_email="easteraman1@icloud.com",  
    description="Automate AWS Lambda CORS configuration in seconds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tinaaaa111/AWS_assistance",
    project_urls={
        "Bug Tracker": "https://github.com/Tinaaaa111/AWS_assistance/issues",
        "Documentation": "https://github.com/Tinaaaa111/AWS_assistance",
        "Source Code": "https://github.com/Tinaaaa111/AWS_assistance",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-assistant=aws_assistant.cli:main",
        ],
    },
    keywords="aws lambda cors api-gateway serverless automation cli",
)