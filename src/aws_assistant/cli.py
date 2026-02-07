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

def check_function_url_and_cors(lambda_client, function_name, region):
    """
    Check if a Lambda function has a Function URL and if CORS is configured.
    Returns a tuple: (has_url, cors_configured, url)
    """
    try:
        # Try to get the Function URL configuration
        response = lambda_client.get_function_url_config(FunctionName=function_name)
        
        # If we get here, the function has a URL
        function_url = response.get('FunctionUrl', '')
        cors_config = response.get('Cors', {})
        
        # Check if CORS is actually configured
        # CORS is considered configured if it has AllowOrigins set
        allow_origins = cors_config.get('AllowOrigins', [])
        
        if allow_origins:
            # CORS is configured
            return (True, True, function_url)
        else:
            # Has URL but no CORS
            return (True, False, function_url)
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'ResourceNotFoundException':
            # Function doesn't have a Function URL
            return (False, False, None)
        else:
            # Some other error, treat as no URL
            return (False, False, None)

@main.command()
def scan():
    """Scan your AWS account for Lambda functions and check CORS status"""
    console.print("\n [bold blue]Scanning your AWS account for Lambda functions in all regions...[/bold blue]\n")
    
    try:
        # First, get a list of all AWS regions
        console.print(" [dim]Discovering available regions...[/dim]")
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        regions_response = ec2_client.describe_regions()
        all_regions = [region['RegionName'] for region in regions_response['Regions']]
        
        console.print(f" [dim]Found {len(all_regions)} regions to scan[/dim]\n")
        
        # Now scan each region for Lambda functions
        all_functions = []
        
        for region in all_regions:
            # Show progress
            console.print(f" [dim]Scanning {region}...[/dim]", end="\r")
            
            try:
                # Create a Lambda client for this specific region
                lambda_client = boto3.client('lambda', region_name=region)
                
                # List functions in this region
                response = lambda_client.list_functions()
                functions = response.get('Functions', [])
                
                # For each function, check CORS status
                for function in functions:
                    function['Region'] = region
                    
                    # Check Function URL and CORS status
                    has_url, cors_configured, url = check_function_url_and_cors(
                        lambda_client, 
                        function['FunctionName'],
                        region
                    )
                    
                    function['HasFunctionUrl'] = has_url
                    function['CorsConfigured'] = cors_configured
                    function['FunctionUrl'] = url
                    
                    all_functions.append(function)
                    
            except ClientError as e:
                # Some regions might not be enabled for the account, skip them
                if 'OptInRequired' in str(e):
                    continue
                else:
                    console.print(f"\n  [yellow]Warning: Could not scan {region}: {e.response['Error']['Message']}[/yellow]")
        
        # Clear the progress line
        console.print(" " * 50, end="\r")
        
        # Check if we found any functions
        if not all_functions:
            console.print("[yellow]No Lambda functions found in any region.[/yellow]")
            console.print("\n [dim]Tip: Create a Lambda function in the AWS Console first, then run this command again.[/dim]\n")
            return
        
        # Create a table with CORS status column
        table = Table(title=f"Lambda Functions (Found in {len(set(f['Region'] for f in all_functions))} regions)")
        table.add_column("Function Name", style="cyan", no_wrap=True)
        table.add_column("Region", style="blue")
        table.add_column("Runtime", style="magenta")
        table.add_column("CORS Status", style="white")
        
        # Sort functions by region, then by name
        all_functions.sort(key=lambda x: (x['Region'], x['FunctionName']))
        
        # Add each function to the table with CORS status
        for function in all_functions:
            name = function['FunctionName']
            region = function['Region']
            runtime = function['Runtime']
            
            # Determine CORS status display
            if not function['HasFunctionUrl']:
                cors_status = "  [yellow]No Function URL[/yellow]"
            elif function['CorsConfigured']:
                cors_status = " [green]Configured[/green]"
            else:
                cors_status = " [red]Not configured[/red]"
            
            table.add_row(name, region, runtime, cors_status)
        
        # Display the table
        console.print(table)
        
        # Show summary statistics
        total = len(all_functions)
        with_url = sum(1 for f in all_functions if f['HasFunctionUrl'])
        with_cors = sum(1 for f in all_functions if f['HasFunctionUrl'] and f['CorsConfigured'])
        without_cors = sum(1 for f in all_functions if f['HasFunctionUrl'] and not f['CorsConfigured'])
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"   Total functions: {total}")
        console.print(f"   With Function URLs: {with_url}")
        console.print(f"   CORS configured: {with_cors}")
        console.print(f"    CORS issues: {without_cors}")
        console.print()
        
    except NoCredentialsError:
        console.print("\n [red]Error: No AWS credentials found[/red]")
        console.print("\n [yellow]Please set up your AWS credentials.[/yellow]\n")
    
    except ClientError as e:
        console.print(f"\n[red]AWS Error: {e.response['Error']['Message']}[/red]\n")
    
    except Exception as e:
        console.print(f"\n [red]Unexpected error: {str(e)}[/red]\n")

if __name__ == "__main__":
    main()