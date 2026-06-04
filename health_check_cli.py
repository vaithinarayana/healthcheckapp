"""
Command Line Interface for Health Check Application
Provides CLI tools to run health checks and monitor system health
"""

import argparse
import json
import sys
from tabulate import tabulate
from health_check import HealthChecker, HealthStatus


def format_output(data, output_format='table'):
    """Format output based on requested format"""
    if output_format == 'json':
        print(json.dumps(data, indent=2))
    elif output_format == 'table':
        print_table_output(data)


def print_table_output(results):
    """Print results in table format"""
    print("\n" + "="*60)
    print(f"Health Check Report - {results['service']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Overall Status: {results['overall_status'].upper()}")
    print("="*60 + "\n")
    
    # Create table data
    table_data = []
    for check_name, check_result in results['checks'].items():
        row = [
            check_result.get('name', check_name),
            check_result.get('status', 'N/A'),
            check_result.get('value', 'N/A'),
            check_result.get('message', '')
        ]
        table_data.append(row)
    
    headers = ['Check', 'Status', 'Value', 'Message']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\nResponse Time: {results['response_time_ms']}ms\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Health Check Application - System Health Monitoring Tool'
    )
    
    parser.add_argument(
        '--service',
        type=str,
        default='MyApplication',
        help='Service name (default: MyApplication)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Full health check command
    subparsers.add_parser(
        'check',
        help='Run full health check'
    )
    
    # Summary command
    subparsers.add_parser(
        'summary',
        help='Show health summary'
    )
    
    # CPU check command
    subparsers.add_parser(
        'cpu',
        help='Check CPU usage'
    )
    
    # Memory check command
    subparsers.add_parser(
        'memory',
        help='Check memory usage'
    )
    
    # Disk check command
    disk_parser = subparsers.add_parser(
        'disk',
        help='Check disk usage'
    )
    disk_parser.add_argument(
        '--path',
        type=str,
        default='/',
        help='Path to check disk usage (default: /)'
    )
    
    # Network check command
    subparsers.add_parser(
        'network',
        help='Check network connectivity'
    )
    
    # Output format argument
    parser.add_argument(
        '--format',
        type=str,
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    
    args = parser.parse_args()
    
    # Initialize health checker
    checker = HealthChecker(service_name=args.service)
    
    # Execute commands
    if args.command == 'check':
        results = checker.run_all_checks()
        format_output(results, args.format)
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_status'] == HealthStatus.HEALTHY else 1)
    
    elif args.command == 'summary':
        summary = checker.get_summary()
        if args.format == 'json':
            print(json.dumps(summary, indent=2))
        else:
            print("\nHealth Summary:")
            print(f"  Service: {summary['service']}")
            print(f"  Status: {summary['overall_status']}")
            print(f"  Healthy Checks: {summary['healthy_checks']}/{summary['total_checks']}")
            print(f"  Timestamp: {summary['timestamp']}\n")
        
        sys.exit(0 if summary['overall_status'] == HealthStatus.HEALTHY else 1)
    
    elif args.command == 'cpu':
        result = checker.check_cpu()
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"\nCPU Check:")
            print(f"  Status: {result['status']}")
            print(f"  Usage: {result['value']}%")
            print(f"  Threshold: {result['threshold']}%\n")
        
        sys.exit(0 if result['status'] == HealthStatus.HEALTHY else 1)
    
    elif args.command == 'memory':
        result = checker.check_memory()
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"\nMemory Check:")
            print(f"  Status: {result['status']}")
            print(f"  Usage: {result['value']}%")
            print(f"  Available: {result['available_gb']}GB / {result['total_gb']}GB")
            print(f"  Threshold: {result['threshold']}%\n")
        
        sys.exit(0 if result['status'] == HealthStatus.HEALTHY else 1)
    
    elif args.command == 'disk':
        result = checker.check_disk(args.path)
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"\nDisk Check ({args.path}):")
            print(f"  Status: {result['status']}")
            print(f"  Usage: {result['value']}%")
            print(f"  Free: {result['free_gb']}GB / {result['total_gb']}GB")
            print(f"  Threshold: {result['threshold']}%\n")
        
        sys.exit(0 if result['status'] == HealthStatus.HEALTHY else 1)
    
    elif args.command == 'network':
        result = checker.check_network()
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"\nNetwork Check:")
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message']}\n")
        
        sys.exit(0 if result['status'] == HealthStatus.HEALTHY else 1)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
