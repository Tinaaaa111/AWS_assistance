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
    """Scan your AWS account for Lambda functions across all regions"""
    console.print("\n🔍 [bold blue]Scanning your AWS account for Lambda functions in all regions...[/bold blue]\n")
    
    try:
        # First, get a list of all AWS regions
        console.print("📍 [dim]Discovering available regions...[/dim]")
        ec2_client = boto3.client('ec2', region_name='us-east-1')  # Any region works to get the list
        regions_response = ec2_client.describe_regions()
        all_regions = [region['RegionName'] for region in regions_response['Regions']]
        
        console.print(f"📍 [dim]Found {len(all_regions)} regions to scan[/dim]\n")
        
        # Now scan each region for Lambda functions
        all_functions = []
        
        for region in all_regions:
            # Show progress
            console.print(f"🔍 [dim]Scanning {region}...[/dim]", end="\r")
            
            try:
                # Create a Lambda client for this specific region
                lambda_client = boto3.client('lambda', region_name=region)
                
                # List functions in this region
                response = lambda_client.list_functions()
                functions = response.get('Functions', [])
                
                # Add region info to each function
                for function in functions:
                    function['Region'] = region
                    all_functions.append(function)
                    
            except ClientError as e:
                # Some regions might not be enabled for the account, skip them
                if 'OptInRequired' in str(e):
                    continue
                else:
                    console.print(f"\n⚠️  [yellow]Warning: Could not scan {region}: {e.response['Error']['Message']}[/yellow]")
        
        # Clear the progress line
        console.print(" " * 50, end="\r")
        
        # Check if we found any functions
        if not all_functions:
            console.print("[yellow]No Lambda functions found in any region.[/yellow]")
            console.print("\n💡 [dim]Tip: Create a Lambda function in the AWS Console first, then run this command again.[/dim]\n")
            return
        
        # Create a table with region column
        table = Table(title=f"Lambda Functions (Found in {len(set(f['Region'] for f in all_functions))} regions)")
        table.add_column("Function Name", style="cyan", no_wrap=True)
        table.add_column("Region", style="blue")
        table.add_column("Runtime", style="magenta")
        table.add_column("Last Modified", style="green")
        
        # Sort functions by region, then by name
        all_functions.sort(key=lambda x: (x['Region'], x['FunctionName']))
        
        # Add each function to the table
        for function in all_functions:
            name = function['FunctionName']
            region = function['Region']
            runtime = function['Runtime']
            last_modified = function['LastModified']
            table.add_row(name, region, runtime, last_modified)
        
        # Display the table
        console.print(table)
        console.print(f"\n✅ [green]Found {len(all_functions)} Lambda function(s) across all regions[/green]\n")
        
    except NoCredentialsError:
        console.print("\n❌ [red]Error: No AWS credentials found[/red]")
        console.print("\n💡 [yellow]Please set up your AWS credentials.[/yellow]\n")
    
    except ClientError as e:
        console.print(f"\n❌ [red]AWS Error: {e.response['Error']['Message']}[/red]\n")
    
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {str(e)}[/red]\n")

if __name__ == "__main__":
    main()