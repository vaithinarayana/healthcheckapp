"""
Flask API for To-Do List Application
Provides REST endpoints for managing to-do items with local storage
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from todo_list import TodoList, TodoItem
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.json.sort_keys = False

# Initialize to-do list manager
todo_manager = TodoList(storage_file="todos.json")


@app.route('/', methods=['GET'])
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all to-do items with optional filtering"""
    try:
        filter_by = request.args.get('filter', 'all')
        sort_by = request.args.get('sort', 'created')
        
        todos = todo_manager.get_all_todos(filter_by=filter_by)
        
        # Sort options
        if sort_by == 'priority':
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            todos.sort(key=lambda x: priority_order.get(x.priority, 3))
        elif sort_by == 'due_date':
            todos.sort(key=lambda x: x.due_date or '9999-12-31')
        
        return jsonify({
            "success": True,
            "data": [todo.to_dict() for todo in todos],
            "count": len(todos)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching todos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new to-do item"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({
                "success": False,
                "error": "Title is required"
            }), 400
        
        todo = todo_manager.add_todo(
            title=data.get('title'),
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            priority=data.get('priority', 'medium')
        )
        
        return jsonify({
            "success": True,
            "data": todo.to_dict(),
            "message": "To-do item created successfully"
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific to-do item"""
    try:
        todo = todo_manager.get_todo(todo_id)
        if not todo:
            return jsonify({
                "success": False,
                "error": "To-do item not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": todo.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching todo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a to-do item"""
    try:
        data = request.get_json()
        todo = todo_manager.update_todo(todo_id, **data)
        
        if not todo:
            return jsonify({
                "success": False,
                "error": "To-do item not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": todo.to_dict(),
            "message": "To-do item updated successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error updating todo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<todo_id>/toggle', methods=['PUT'])
def toggle_todo(todo_id):
    """Toggle completion status of a to-do item"""
    try:
        todo = todo_manager.toggle_todo(todo_id)
        
        if not todo:
            return jsonify({
                "success": False,
                "error": "To-do item not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": todo.to_dict(),
            "message": f"To-do item marked as {'completed' if todo.completed else 'pending'}"
        }), 200
    except Exception as e:
        logger.error(f"Error toggling todo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a to-do item"""
    try:
        success = todo_manager.delete_todo(todo_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": "To-do item not found"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "To-do item deleted successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error deleting todo: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/bulk/delete', methods=['POST'])
def bulk_delete():
    """Delete multiple to-do items"""
    try:
        data = request.get_json()
        todo_ids = data.get('ids', [])
        
        deleted_count = 0
        for todo_id in todo_ids:
            if todo_manager.delete_todo(todo_id):
                deleted_count += 1
        
        return jsonify({
            "success": True,
            "deleted": deleted_count,
            "message": f"Deleted {deleted_count} to-do items"
        }), 200
    except Exception as e:
        logger.error(f"Error bulk deleting: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get statistics about to-do items"""
    try:
        stats = todo_manager.get_statistics()
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/export', methods=['GET'])
def export_todos():
    """Export all to-do items as JSON"""
    try:
        success = todo_manager.export_to_json("todos_export.json")
        if success:
            return jsonify({
                "success": True,
                "message": "To-do items exported successfully",
                "file": "todos_export.json"
            }), 200
        return jsonify({
            "success": False,
            "error": "Export failed"
        }), 500
    except Exception as e:
        logger.error(f"Error exporting todos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/import', methods=['POST'])
def import_todos():
    """Import to-do items from JSON file"""
    try:
        data = request.get_json()
        filename = data.get('filename', 'todos_import.json')
        
        success = todo_manager.import_from_json(filename)
        if success:
            return jsonify({
                "success": True,
                "message": "To-do items imported successfully",
                "count": len(todo_manager.todos)
            }), 200
        return jsonify({
            "success": False,
            "error": "Import failed - file not found"
        }), 404
    except Exception as e:
        logger.error(f"Error importing todos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_todos():
    """Clear all to-do items"""
    try:
        todo_manager.clear_all()
        return jsonify({
            "success": True,
            "message": "All to-do items cleared"
        }), 200
    except Exception as e:
        logger.error(f"Error clearing todos: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
