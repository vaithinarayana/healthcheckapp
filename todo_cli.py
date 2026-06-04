"""
Command Line Interface for To-Do List Application
Provides CLI tools to manage to-do items
"""

import argparse
import json
import sys
from tabulate import tabulate
from todo_list import TodoList
from datetime import datetime


def print_todo(todo, show_id=False):
    """Print a single to-do item in a formatted way"""
    status = "✓" if todo.completed else "○"
    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    
    print(f"  {status} {priority_emoji.get(todo.priority, '●')} {todo.title}")
    if todo.description:
        print(f"     Description: {todo.description}")
    if todo.due_date:
        print(f"     Due: {todo.due_date}")
    if show_id:
        print(f"     ID: {todo.id}")


def print_todos_table(todos):
    """Print todos in a table format"""
    if not todos:
        print("No to-do items found.\n")
        return
    
    table_data = []
    for todo in todos:
        status = "✓" if todo.completed else "○"
        table_data.append([
            status,
            todo.title[:30],
            todo.priority,
            todo.due_date or "N/A",
            todo.created_at[:10]
        ])
    
    headers = ["Status", "Title", "Priority", "Due Date", "Created"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='To-Do List Application - Manage your tasks efficiently',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python todo_cli.py add "Buy groceries" --priority high
  python todo_cli.py list --filter pending
  python todo_cli.py done task-id
  python todo_cli.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new to-do item')
    add_parser.add_argument('title', help='Title of the to-do item')
    add_parser.add_argument('--description', '-d', help='Description of the to-do')
    add_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    add_parser.add_argument('--priority', '-p', choices=['low', 'medium', 'high'], 
                           default='medium', help='Priority level')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List to-do items')
    list_parser.add_argument('--filter', '-f', 
                            choices=['all', 'pending', 'completed', 'low', 'medium', 'high'],
                            default='all', help='Filter by status or priority')
    list_parser.add_argument('--sort', '-s',
                            choices=['created', 'priority', 'due'],
                            default='created', help='Sort by field')
    list_parser.add_argument('--format', choices=['table', 'detail'],
                            default='table', help='Output format')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View a specific to-do item')
    view_parser.add_argument('id', help='To-do item ID')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a to-do item')
    edit_parser.add_argument('id', help='To-do item ID')
    edit_parser.add_argument('--title', help='New title')
    edit_parser.add_argument('--description', help='New description')
    edit_parser.add_argument('--due', help='New due date')
    edit_parser.add_argument('--priority', choices=['low', 'medium', 'high'], help='New priority')
    
    # Done/Toggle command
    done_parser = subparsers.add_parser('done', help='Mark to-do as completed/pending')
    done_parser.add_argument('id', help='To-do item ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a to-do item')
    delete_parser.add_argument('id', help='To-do item ID')
    delete_parser.add_argument('--confirm', '-y', action='store_true', help='Skip confirmation')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all to-do items')
    clear_parser.add_argument('--confirm', '-y', action='store_true', help='Skip confirmation')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export to-do items')
    export_parser.add_argument('--file', '-f', default='todos_export.json', help='Export file')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import to-do items')
    import_parser.add_argument('file', help='Import file')
    
    args = parser.parse_args()
    
    # Initialize todo manager
    todo_manager = TodoList(storage_file="todos.json")
    
    # Execute commands
    if args.command == 'add':
        todo = todo_manager.add_todo(
            title=args.title,
            description=args.description or "",
            due_date=args.due,
            priority=args.priority
        )
        print(f"\n✓ To-do item added (ID: {todo.id})\n")
        print_todo(todo, show_id=True)
        print()
    
    elif args.command == 'list':
        todos = todo_manager.get_all_todos(filter_by=args.filter)
        
        if not todos:
            print("\nNo to-do items found.\n")
        else:
            print(f"\nYour To-Do Items ({len(todos)} total):\n")
            if args.format == 'table':
                print_todos_table(todos)
            else:
                for todo in todos:
                    print_todo(todo, show_id=True)
                    print()
    
    elif args.command == 'view':
        todo = todo_manager.get_todo(args.id)
        if not todo:
            print(f"\n✗ To-do item not found (ID: {args.id})\n")
            sys.exit(1)
        print()
        print_todo(todo, show_id=True)
        print()
    
    elif args.command == 'edit':
        updates = {}
        if args.title:
            updates['title'] = args.title
        if args.description:
            updates['description'] = args.description
        if args.due:
            updates['due_date'] = args.due
        if args.priority:
            updates['priority'] = args.priority
        
        todo = todo_manager.update_todo(args.id, **updates)
        if not todo:
            print(f"\n✗ To-do item not found (ID: {args.id})\n")
            sys.exit(1)
        
        print(f"\n✓ To-do item updated\n")
        print_todo(todo, show_id=True)
        print()
    
    elif args.command == 'done':
        todo = todo_manager.toggle_todo(args.id)
        if not todo:
            print(f"\n✗ To-do item not found (ID: {args.id})\n")
            sys.exit(1)
        
        status = "completed" if todo.completed else "pending"
        print(f"\n✓ To-do marked as {status}\n")
        print_todo(todo, show_id=True)
        print()
    
    elif args.command == 'delete':
        if not args.confirm:
            response = input(f"Are you sure you want to delete this item? (y/n): ")
            if response.lower() != 'y':
                print("\nCancelled\n")
                sys.exit(0)
        
        success = todo_manager.delete_todo(args.id)
        if not success:
            print(f"\n✗ To-do item not found (ID: {args.id})\n")
            sys.exit(1)
        
        print(f"\n✓ To-do item deleted\n")
    
    elif args.command == 'stats':
        stats = todo_manager.get_statistics()
        print(f"\n{'='*50}")
        print(f"To-Do Statistics")
        print(f"{'='*50}\n")
        print(f"Total Items:        {stats['total']}")
        print(f"Completed:          {stats['completed']}")
        print(f"Pending:            {stats['pending']}")
        print(f"Completion Rate:    {stats['completion_percentage']}%\n")
        print(f"By Priority:")
        print(f"  High:   {stats['by_priority']['high']}")
        print(f"  Medium: {stats['by_priority']['medium']}")
        print(f"  Low:    {stats['by_priority']['low']}")
        print(f"\n{'='*50}\n")
    
    elif args.command == 'clear':
        if not args.confirm:
            response = input(f"Are you sure you want to delete ALL items? (y/n): ")
            if response.lower() != 'y':
                print("\nCancelled\n")
                sys.exit(0)
        
        todo_manager.clear_all()
        print("\n✓ All to-do items cleared\n")
    
    elif args.command == 'export':
        success = todo_manager.export_to_json(args.file)
        if success:
            print(f"\n✓ To-do items exported to {args.file}\n")
        else:
            print(f"\n✗ Export failed\n")
            sys.exit(1)
    
    elif args.command == 'import':
        success = todo_manager.import_from_json(args.file)
        if success:
            print(f"\n✓ To-do items imported from {args.file}\n")
        else:
            print(f"\n✗ Import failed - file not found\n")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
