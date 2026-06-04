import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid


class TodoItem:
    """Represents a single to-do item"""
    
    def __init__(self, title: str, description: str = "", due_date: str = None, priority: str = "medium", item_id: str = None):
        self.id = item_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority  # low, medium, high
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TodoItem':
        """Create from dictionary"""
        item = TodoItem(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            item_id=data.get("id")
        )
        item.completed = data.get("completed", False)
        item.created_at = data.get("created_at", datetime.now().isoformat())
        item.updated_at = data.get("updated_at", datetime.now().isoformat())
        return item


class TodoList:
    """Manages a collection of to-do items with local storage"""
    
    def __init__(self, storage_file: str = "todos.json"):
        self.storage_file = storage_file
        self.todos: Dict[str, TodoItem] = {}
        self.load_from_storage()
    
    def add_todo(self, title: str, description: str = "", due_date: str = None, priority: str = "medium") -> TodoItem:
        """Add a new to-do item"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        todo = TodoItem(title=title, description=description, due_date=due_date, priority=priority)
        self.todos[todo.id] = todo
        self.save_to_storage()
        return todo
    
    def get_todo(self, todo_id: str) -> Optional[TodoItem]:
        """Get a specific to-do item"""
        return self.todos.get(todo_id)
    
    def get_all_todos(self, filter_by: str = "all") -> List[TodoItem]:
        """Get all to-do items with optional filtering"""
        todos = list(self.todos.values())
        
        if filter_by == "completed":
            todos = [t for t in todos if t.completed]
        elif filter_by == "pending":
            todos = [t for t in todos if not t.completed]
        elif filter_by in ["low", "medium", "high"]:
            todos = [t for t in todos if t.priority == filter_by]
        
        # Sort by creation date (newest first)
        todos.sort(key=lambda x: x.created_at, reverse=True)
        return todos
    
    def update_todo(self, todo_id: str, **kwargs) -> Optional[TodoItem]:
        """Update a to-do item"""
        todo = self.todos.get(todo_id)
        if not todo:
            return None
        
        # Update allowed fields
        allowed_fields = {"title", "description", "due_date", "priority", "completed"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(todo, key, value)
        
        todo.updated_at = datetime.now().isoformat()
        self.save_to_storage()
        return todo
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a to-do item"""
        if todo_id in self.todos:
            del self.todos[todo_id]
            self.save_to_storage()
            return True
        return False
    
    def toggle_todo(self, todo_id: str) -> Optional[TodoItem]:
        """Toggle completion status of a to-do item"""
        todo = self.todos.get(todo_id)
        if todo:
            todo.completed = not todo.completed
            todo.updated_at = datetime.now().isoformat()
            self.save_to_storage()
        return todo
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about to-do items"""
        total = len(self.todos)
        completed = sum(1 for t in self.todos.values() if t.completed)
        pending = total - completed
        
        by_priority = {
            "low": sum(1 for t in self.todos.values() if t.priority == "low"),
            "medium": sum(1 for t in self.todos.values() if t.priority == "medium"),
            "high": sum(1 for t in self.todos.values() if t.priority == "high")
        }
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_percentage": round((completed / total * 100) if total > 0 else 0, 2),
            "by_priority": by_priority
        }
    
    def save_to_storage(self) -> bool:
        """Save to-do items to JSON file"""
        try:
            data = {
                "todos": [todo.to_dict() for todo in self.todos.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to storage: {str(e)}")
            return False
    
    def load_from_storage(self) -> bool:
        """Load to-do items from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.todos = {
                        todo_data["id"]: TodoItem.from_dict(todo_data)
                        for todo_data in data.get("todos", [])
                    }
            return True
        except Exception as e:
            print(f"Error loading from storage: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all to-do items"""
        self.todos.clear()
        self.save_to_storage()
        return True
    
    def export_to_json(self, filename: str = "todos_export.json") -> bool:
        """Export to-do items to a JSON file"""
        try:
            data = {
                "exported_at": datetime.now().isoformat(),
                "todos": [todo.to_dict() for todo in self.todos.values()]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting: {str(e)}")
            return False
    
    def import_from_json(self, filename: str) -> bool:
        """Import to-do items from a JSON file"""
        try:
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r') as f:
                data = json.load(f)
                for todo_data in data.get("todos", []):
                    todo = TodoItem.from_dict(todo_data)
                    self.todos[todo.id] = todo
            
            self.save_to_storage()
            return True
        except Exception as e:
            print(f"Error importing: {str(e)}")
            return False
