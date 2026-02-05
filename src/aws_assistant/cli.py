import click
from rich.console import Console
from rich.table import Table
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

console = Console()

@click.group()
def main():
    """AWS Integration Assistant - Fix AWS problems with one command"""
    pass

@main.command()
def scan():
    """Scan your AWS account for Lambda functions"""
    console.print("\n🔍 [bold blue]Scanning your AWS account for Lambda functions...[/bold blue]\n")
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name='us-west-2')
        
        # List all Lambda functions
        response = lambda_client.list_functions()
        
        # Check if there are any functions
        functions = response.get('Functions', [])
        
        if not functions:
            console.print("[yellow]No Lambda functions found in your account.[/yellow]")
            console.print("\n💡 [dim]Tip: Create a Lambda function in the AWS Console first, then run this command again.[/dim]\n")
            return
        
        # Create a nice table
        table = Table(title="Lambda Functions")
        table.add_column("Function Name", style="cyan", no_wrap=True)
        table.add_column("Runtime", style="magenta")
        table.add_column("Last Modified", style="green")
        
        # Add each function to the table
        for function in functions:
            name = function['FunctionName']
            runtime = function['Runtime']
            last_modified = function['LastModified']
            table.add_row(name, runtime, last_modified)
        
        # Display the table
        console.print(table)
        console.print(f"\n✅ [green]Found {len(functions)} Lambda function(s)[/green]\n")
        
    except NoCredentialsError:
        console.print("\n❌ [red]Error: No AWS credentials found[/red]")
        console.print("\n💡 [yellow]Please run 'aws configure' to set up your AWS credentials.[/yellow]\n")
    
    except ClientError as e:
        console.print(f"\n❌ [red]AWS Error: {e.response['Error']['Message']}[/red]\n")
    
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {str(e)}[/red]\n")

if __name__ == "__main__":
    main()