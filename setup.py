from setuptools import setup, find_packages

setup(
    name="aws-integration-assistant",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.35.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-assistant=aws_assistant.cli:main",
        ],
    },
)