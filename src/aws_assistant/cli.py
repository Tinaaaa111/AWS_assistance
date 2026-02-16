import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import json

console = Console()

@click.group()
def main():
    """AWS Integration Assistant - Fix AWS problems with one command"""
    pass

def detect_origins():
    """Smart detection of allowed origins from project files"""
    detected_origins = []
    detection_source = None
    
    if os.path.exists('package.json'):
        try:
            with open('package.json', 'r') as f:
                package_data = json.load(f)
                if 'homepage' in package_data:
                    detected_origins.append(package_data['homepage'])
                    detection_source = 'package.json (homepage)'
        except:
            pass
    
    env_files = ['.env', '.env.local', '.env.production', '.env.development']
    env_vars = [
        'REACT_APP_URL',
        'NEXT_PUBLIC_URL', 
        'VITE_URL',
        'VUE_APP_URL',
        'PUBLIC_URL',
        'APP_URL',
        'FRONTEND_URL'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            for var in env_vars:
                                if line.startswith(f'{var}='):
                                    url = line.split('=', 1)[1].strip().strip('"').strip("'")
                                    if url and url not in detected_origins:
                                        detected_origins.append(url)
                                        detection_source = f'{env_file} ({var})'
            except:
                pass
    
    for var in env_vars:
        if var in os.environ:
            url = os.environ[var]
            if url and url not in detected_origins:
                detected_origins.append(url)
                detection_source = f'environment variable ({var})'
    
    if os.path.exists('vercel.json'):
        try:
            with open('vercel.json', 'r') as f:
                vercel_data = json.load(f)
                if 'env' in vercel_data and 'NEXT_PUBLIC_URL' in vercel_data['env']:
                    url = vercel_data['env']['NEXT_PUBLIC_URL']
                    if url and url not in detected_origins:
                        detected_origins.append(url)
                        detection_source = 'vercel.json'
        except:
            pass
    
    return detected_origins, detection_source

def check_function_url_and_cors(lambda_client, function_name, region):
    try:
        response = lambda_client.get_function_url_config(FunctionName=function_name)
        function_url = response.get('FunctionUrl', '')
        cors_config = response.get('Cors', {})
        allow_origins = cors_config.get('AllowOrigins', [])
        
        if allow_origins:
            return (True, True, function_url)
        else:
            return (True, False, function_url)
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            return (False, False, None)
        else:
            return (False, False, None)

def get_api_gateway_lambda_mappings(region):
    mappings = {}
    
    try:
        apigw2_client = boto3.client('apigatewayv2', region_name=region)
        
        apis_response = apigw2_client.get_apis()
        http_apis = apis_response.get('Items', [])
        
        for api in http_apis:
            api_id = api['ApiId']
            api_name = api['Name']
            cors_config = api.get('CorsConfiguration', {})
            has_cors = bool(cors_config.get('AllowOrigins'))
            
            try:
                integrations_response = apigw2_client.get_integrations(ApiId=api_id)
                
                for integration in integrations_response.get('Items', []):
                    integration_uri = integration.get('IntegrationUri', '')
                    
                    if integration_uri and 'lambda' in integration_uri.lower():
                        lambda_arn = None
                        
                        if 'arn:aws:lambda' in integration_uri:
                            parts = integration_uri.split('/')
                            for part in parts:
                                if part.startswith('arn:aws:lambda'):
                                    lambda_arn = part
                                    break
                        
                        if lambda_arn:
                            base_arn = lambda_arn.split(':invocations')[0]
                            base_arn = base_arn.split(':$')[0]
                            base_arn = base_arn.split(':alias')[0]
                            
                            if base_arn not in mappings:
                                mappings[base_arn] = []
                            
                            mappings[base_arn].append({
                                'type': 'HTTP API',
                                'api_id': api_id,
                                'api_name': api_name,
                                'cors_configured': has_cors
                            })
                            
            except Exception as e:
                pass
                
    except Exception as e:
        pass
    
    try:
        apigw_client = boto3.client('apigateway', region_name=region)
        
        apis_response = apigw_client.get_rest_apis()
        rest_apis = apis_response.get('items', [])
        
        for api in rest_apis:
            api_id = api['id']
            api_name = api['name']
            
            has_cors = False
            
            try:
                resources_response = apigw_client.get_resources(restApiId=api_id)
                
                for resource in resources_response.get('items', []):
                    resource_id = resource['id']
                    methods = resource.get('resourceMethods', {})
                    
                    if 'OPTIONS' in methods:
                        has_cors = True
                    
                    for method in methods.keys():
                        if method == 'OPTIONS':
                            continue
                            
                        try:
                            integration = apigw_client.get_integration(
                                restApiId=api_id,
                                resourceId=resource_id,
                                httpMethod=method
                            )
                            
                            integration_uri = integration.get('uri', '')
                            
                            if integration_uri and 'lambda' in integration_uri.lower():
                                lambda_arn = None
                                
                                if 'arn:aws:lambda' in integration_uri:
                                    parts = integration_uri.split('/')
                                    for part in parts:
                                        if part.startswith('arn:aws:lambda'):
                                            lambda_arn = part
                                            break
                                
                                if lambda_arn:
                                    base_arn = lambda_arn.split(':invocations')[0]
                                    base_arn = base_arn.split(':$')[0]
                                    base_arn = base_arn.split(':alias')[0]
                                    
                                    if base_arn not in mappings:
                                        mappings[base_arn] = []
                                    
                                    if not any(m['api_id'] == api_id for m in mappings[base_arn]):
                                        mappings[base_arn].append({
                                            'type': 'REST API',
                                            'api_id': api_id,
                                            'api_name': api_name,
                                            'cors_configured': has_cors
                                        })
                                        
                        except Exception as e:
                            pass
                            
            except Exception as e:
                pass
                
    except Exception as e:
        pass
    
    return mappings

@main.command()
def scan():
    """Scan your AWS account for Lambda functions and check CORS status"""
    console.print("\n[bold blue]Scanning your AWS account for Lambda functions in all regions...[/bold blue]\n")
    
    try:
        console.print("[dim]Discovering available regions...[/dim]")
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        regions_response = ec2_client.describe_regions()
        all_regions = [region['RegionName'] for region in regions_response['Regions']]
        
        console.print(f"[dim]Found {len(all_regions)} regions to scan[/dim]\n")
        
        all_functions = []
        
        for region in all_regions:
            console.print(f"[dim]Scanning {region}...[/dim]", end="\r")
            
            try:
                lambda_client = boto3.client('lambda', region_name=region)
                
                api_mappings = get_api_gateway_lambda_mappings(region)
                
                response = lambda_client.list_functions()
                functions = response.get('Functions', [])
                
                for function in functions:
                    function['Region'] = region
                    function_arn = function['FunctionArn']
                    
                    has_url, cors_configured, url = check_function_url_and_cors(
                        lambda_client, 
                        function['FunctionName'],
                        region
                    )
                    
                    function['HasFunctionUrl'] = has_url
                    function['FunctionUrlCorsConfigured'] = cors_configured
                    function['FunctionUrl'] = url
                    
                    function['ApiGateways'] = api_mappings.get(function_arn, [])
                    function['HasApiGateway'] = len(function['ApiGateways']) > 0
                    
                    all_functions.append(function)
                    
            except ClientError as e:
                if 'OptInRequired' in str(e):
                    continue
                else:
                    console.print(f"\n[yellow]Warning: Could not scan {region}: {e.response['Error']['Message']}[/yellow]")
        
        console.print(" " * 50, end="\r")
        
        if not all_functions:
            console.print("[yellow]No Lambda functions found in any region.[/yellow]")
            console.print("\n[dim]Tip: Create a Lambda function in the AWS Console first, then run this command again.[/dim]\n")
            return
        
        table = Table(title=f"Lambda Functions (Found in {len(set(f['Region'] for f in all_functions))} regions)")
        table.add_column("Function Name", style="cyan", no_wrap=True)
        table.add_column("Region", style="blue")
        table.add_column("Runtime", style="magenta")
        table.add_column("Access Type", style="yellow")
        table.add_column("CORS Status", style="white")
        
        all_functions.sort(key=lambda x: (x['Region'], x['FunctionName']))
        
        for function in all_functions:
            name = function['FunctionName']
            region = function['Region']
            runtime = function['Runtime']
            
            access_types = []
            cors_statuses = []
            
            if function['HasFunctionUrl']:
                access_types.append("Function URL")
                if function['FunctionUrlCorsConfigured']:
                    cors_statuses.append("[green]CONFIGURED[/green]")
                else:
                    cors_statuses.append("[red]NOT CONFIGURED[/red]")
            
            if function['HasApiGateway']:
                for api in function['ApiGateways']:
                    access_types.append(f"{api['type']}")
                    if api['cors_configured']:
                        cors_statuses.append(f"[green]{api['api_name'][:15]}[/green]")
                    else:
                        cors_statuses.append(f"[red]{api['api_name'][:15]}[/red]")
            
            if not access_types:
                access_type = "[yellow]Private[/yellow]"
                cors_status = "[dim]N/A[/dim]"
            else:
                access_type = ", ".join(access_types)
                cors_status = " | ".join(cors_statuses)
            
            table.add_row(name, region, runtime, access_type, cors_status)
        
        console.print(table)
        
        total = len(all_functions)
        with_function_url = sum(1 for f in all_functions if f['HasFunctionUrl'])
        with_api_gateway = sum(1 for f in all_functions if f['HasApiGateway'])
        with_function_url_cors = sum(1 for f in all_functions if f['HasFunctionUrl'] and f['FunctionUrlCorsConfigured'])
        with_api_gateway_cors = sum(1 for f in all_functions if f['HasApiGateway'] and any(api['cors_configured'] for api in f['ApiGateways']))
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"   Total functions: {total}")
        console.print(f"   With Function URLs: {with_function_url} ({with_function_url_cors} with CORS)")
        console.print(f"   Behind API Gateway: {with_api_gateway} ({with_api_gateway_cors} with CORS)")
        console.print()
        
    except NoCredentialsError:
        console.print("\n[red]Error: No AWS credentials found[/red]")
        console.print("\n[yellow]Please set up your AWS credentials.[/yellow]\n")
    
    except ClientError as e:
        console.print(f"\n[red]AWS Error: {e.response['Error']['Message']}[/red]\n")
    
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {str(e)}[/red]\n")

@main.command()
@click.argument('function_name')
@click.option('--region', default=None, help='AWS region (defaults to scanning all regions)')
@click.option('--target', type=click.Choice(['url', 'api', 'all']), default=None, help='What to fix: url (Function URL), api (API Gateway), or all')
@click.option('--origin', multiple=True, help='Allowed origins (can specify multiple)')
@click.option('--wildcard', is_flag=True, help='Use wildcard (*) for all origins')
def fix_cors(function_name, region, target, origin, wildcard):
    """Fix CORS configuration for a Lambda function"""
    console.print(f"\n[bold blue]Fixing CORS for {function_name}...[/bold blue]\n")
    
    try:
        if region:
            regions_to_check = [region]
        else:
            console.print("[dim]Searching for function across all regions...[/dim]")
            ec2_client = boto3.client('ec2', region_name='us-east-1')
            regions_response = ec2_client.describe_regions()
            regions_to_check = [r['RegionName'] for r in regions_response['Regions']]
        
        function_region = None
        lambda_client = None
        
        for check_region in regions_to_check:
            try:
                temp_client = boto3.client('lambda', region_name=check_region)
                temp_client.get_function(FunctionName=function_name)
                function_region = check_region
                lambda_client = temp_client
                break
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    continue
                else:
                    raise
        
        if not function_region:
            console.print(f"[red]Function '{function_name}' not found in any region[/red]\n")
            return
        
        console.print(f"[green]Found function in region: {function_region}[/green]\n")
        
        function_info = lambda_client.get_function(FunctionName=function_name)
        function_arn = function_info['Configuration']['FunctionArn']
        
        has_url, url_cors_configured, function_url = check_function_url_and_cors(
            lambda_client, function_name, function_region
        )
        
        api_mappings = get_api_gateway_lambda_mappings(function_region)
        apis = api_mappings.get(function_arn, [])
        has_apis = len(apis) > 0
        
        if not has_url and not has_apis:
            console.print(f"[red]This function has no public access (no Function URL or API Gateway)[/red]\n")
            return
        
        if target is None:
            if has_url and has_apis:
                console.print("[yellow]This function has multiple access methods:[/yellow]")
                if has_url:
                    status = "CONFIGURED" if url_cors_configured else "NOT CONFIGURED"
                    console.print(f"   Function URL: {status}")
                for api in apis:
                    status = "CONFIGURED" if api['cors_configured'] else "NOT CONFIGURED"
                    console.print(f"   {api['type']}: {api['api_name']} - {status}")
                console.print(f"\n[dim]Use --target flag to specify what to fix:[/dim]")
                console.print(f"   [dim]--target url       Fix Function URL CORS[/dim]")
                console.print(f"   [dim]--target api       Fix API Gateway CORS[/dim]")
                console.print(f"   [dim]--target all       Fix both[/dim]\n")
                return
            elif has_url:
                target = 'url'
            elif has_apis:
                target = 'api'
        
        if origin:
            allow_origins = list(origin)
            console.print(f"[bold]Using specified origins:[/bold]")
            for orig in allow_origins:
                console.print(f"   {orig}")
            console.print()
        elif wildcard:
            allow_origins = ['*']
            console.print("[yellow bold]Using wildcard origin (*)[/yellow bold]")
            console.print("[yellow]This allows ANY website to access your API[/yellow]")
            console.print("[yellow]Recommended for development only![/yellow]\n")
        else:
            console.print("[bold]Detecting origins from your project...[/bold]\n")
            detected_origins, detection_source = detect_origins()
            
            if detected_origins and detection_source != 'common development defaults':
                console.print(f"[green]Found origin(s) in {detection_source}:[/green]")
                for orig in detected_origins:
                    console.print(f"   [cyan]{orig}[/cyan]")
                console.print()
                
                use_detected = click.confirm("Use this origin?", default=True)
                
                if use_detected:
                    allow_origins = detected_origins
                else:
                    console.print("\n[dim]Enter the origin URL for your frontend app[/dim]")
                    console.print("[dim]Examples: https://myapp.com, http://localhost:3000[/dim]\n")
                    manual_origin = click.prompt("Origin URL")
                    allow_origins = [manual_origin]
                    
                    if click.confirm("Add more origins?", default=False):
                        while True:
                            additional = click.prompt("Additional origin URL (or press Enter to finish)", default="", show_default=False)
                            if not additional:
                                break
                            allow_origins.append(additional)
            else:
                console.print("[yellow]No origin detected in project files[/yellow]")
                console.print("\n[dim]Common options:[/dim]")
                console.print("[dim]  http://localhost:3000  (React development)[/dim]")
                console.print("[dim]  http://localhost:5173  (Vite development)[/dim]")
                console.print("[dim]  https://myapp.com      (Production)[/dim]")
                console.print("[dim]  *                      (All origins - development only!)[/dim]\n")
                
                origin_choice = click.prompt(
                    "Select an option",
                    type=click.Choice(['localhost:3000', 'localhost:5173', 'custom', 'wildcard']),
                    default='localhost:3000'
                )
                
                if origin_choice == 'localhost:3000':
                    allow_origins = ['http://localhost:3000']
                elif origin_choice == 'localhost:5173':
                    allow_origins = ['http://localhost:5173']
                elif origin_choice == 'wildcard':
                    allow_origins = ['*']
                    console.print("\n[yellow]Warning: Wildcard allows ANY site to access your API[/yellow]")
                else:
                    manual_origin = click.prompt("Enter origin URL")
                    allow_origins = [manual_origin]
                
                console.print()
            
            console.print(f"[bold green]Will configure CORS for:[/bold green]")
            for orig in allow_origins:
                console.print(f"   {orig}")
            console.print()
        
        allow_credentials = False
        
        if target in ['url', 'all'] and has_url:
            console.print("[bold]Fixing Function URL CORS...[/bold]")
            
            if url_cors_configured:
                console.print(f"   [dim]CORS already configured, updating...[/dim]")
            
            cors_config = {
                'AllowOrigins': allow_origins,
                'AllowMethods': ['*'],
                'AllowHeaders': ['*'],
                'MaxAge': 86400,
                'AllowCredentials': allow_credentials
            }
            
            lambda_client.update_function_url_config(
                FunctionName=function_name,
                Cors=cors_config
            )
            
            console.print("   [green]Function URL CORS configured![/green]\n")
        
        if target in ['api', 'all'] and has_apis:
            console.print("[bold]Fixing API Gateway CORS...[/bold]")
            
            for api in apis:
                api_id = api['api_id']
                api_name = api['api_name']
                api_type = api['type']
                
                console.print(f"\n   Configuring {api_type}: {api_name}")
                
                if api_type == 'HTTP API':
                    apigw2_client = boto3.client('apigatewayv2', region_name=function_region)
                    
                    apigw2_client.update_api(
                        ApiId=api_id,
                        CorsConfiguration={
                            'AllowOrigins': allow_origins,
                            'AllowMethods': ['*'],
                            'AllowHeaders': ['*'],
                            'MaxAge': 86400,
                            'AllowCredentials': allow_credentials
                        }
                    )
                    
                    console.print(f"      AllowOrigins: {', '.join(allow_origins)}")
                    console.print(f"      AllowMethods: * (all methods)")
                    console.print(f"      AllowHeaders: * (all headers)")
                    console.print(f"   [green]{api_name} CORS configured![/green]")
                
                elif api_type == 'REST API':
                    console.print(f"   [yellow]REST API CORS requires manual configuration[/yellow]")
                    console.print(f"   [dim]REST API CORS is complex and varies by resource[/dim]")
                    console.print(f"   [dim]Please configure in AWS Console: API Gateway -> {api_name} -> CORS[/dim]")
        
        console.print("\n[bold green]CORS configuration complete![/bold green]\n")
        
        if has_url and target in ['url', 'all']:
            react_code = f"""// In your React app:

fetch('{function_url}', {{
  method: 'POST',
  headers: {{
    'Content-Type': 'application/json'
  }},
  body: JSON.stringify({{ 
    // Your data here
  }})
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));"""
            
            console.print(Panel(
                react_code,
                title="Use this in your React app",
                border_style="green"
            ))
        
        console.print(f"\n[bold]All done![/bold]\n")
        
    except NoCredentialsError:
        console.print("\n[red]Error: No AWS credentials found[/red]")
        console.print("\n[yellow]Please set up your AWS credentials.[/yellow]\n")
    
    except ClientError as e:
        console.print(f"\n[red]AWS Error: {e.response['Error']['Message']}[/red]\n")
    
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {str(e)}[/red]\n")

if __name__ == "__main__":
    main()