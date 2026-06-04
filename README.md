# To-Do List Application

A comprehensive to-do list application with local storage functionality, featuring both a REST API backend and an interactive web interface.

## Features

- ✅ **Create, Read, Update, Delete (CRUD)** - Full task management
- 💾 **Local Storage** - All tasks saved to JSON file (persistent storage)
- 🎯 **Priority Levels** - Low, Medium, High priority classification
- 📅 **Due Dates** - Set and track task deadlines
- 🔍 **Filtering** - Filter tasks by status (pending/completed) or priority
- 📊 **Statistics** - Track completion rates and task metrics
- 🌐 **REST API** - Full-featured API for programmatic access
- 💻 **Web Interface** - Beautiful, responsive UI for easy task management
- 🖥️ **CLI Tool** - Command-line interface for power users
- 📤 **Import/Export** - Backup and restore tasks as JSON
- 🎨 **Modern Design** - Clean, intuitive, and accessible interface

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

```bash
# Clone or navigate to the project directory
cd todo-list-app

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Web Application

```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

### Using the CLI Tool

```bash
# Show help
python todo_cli.py --help

# Add a new task
python todo_cli.py add "Buy groceries" --priority high --due 2024-12-25

# List all tasks
python todo_cli.py list

# List pending tasks
python todo_cli.py list --filter pending

# View a specific task
python todo_cli.py view <task-id>

# Mark task as complete
python todo_cli.py done <task-id>

# Edit a task
python todo_cli.py edit <task-id> --title "New title" --priority medium

# Delete a task
python todo_cli.py delete <task-id>

# Show statistics
python todo_cli.py stats

# Export tasks
python todo_cli.py export --file my_tasks.json

# Import tasks
python todo_cli.py import my_tasks.json

# Clear all tasks
python todo_cli.py clear
```

## REST API Endpoints

### Todos Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Get all todos (with optional filtering) |
| POST | `/api/todos` | Create a new todo |
| GET | `/api/todos/<id>` | Get a specific todo |
| PUT | `/api/todos/<id>` | Update a todo |
| PUT | `/api/todos/<id>/toggle` | Toggle todo completion |
| DELETE | `/api/todos/<id>` | Delete a todo |
| POST | `/api/todos/bulk/delete` | Delete multiple todos |

### Statistics & Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/statistics` | Get todo statistics |
| POST | `/api/clear` | Clear all todos |
| GET | `/api/export` | Export todos to JSON |
| POST | `/api/import` | Import todos from JSON |

### Web Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web application |

## API Examples

### Create a Todo

```bash
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy milk",
    "description": "Get 2L milk from grocery store",
    "priority": "high",
    "due_date": "2024-12-25"
  }'
```

### Get All Todos

```bash
curl http://localhost:5000/api/todos
```

### Filter Todos

```bash
# Get pending todos
curl "http://localhost:5000/api/todos?filter=pending"

# Get high priority todos
curl "http://localhost:5000/api/todos?filter=high"

# Get completed todos
curl "http://localhost:5000/api/todos?filter=completed"
```

### Toggle Todo Completion

```bash
curl -X PUT http://localhost:5000/api/todos/<todo-id>/toggle
```

### Update a Todo

```bash
curl -X PUT http://localhost:5000/api/todos/<todo-id> \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "priority": "low",
    "completed": true
  }'
```

### Delete a Todo

```bash
curl -X DELETE http://localhost:5000/api/todos/<todo-id>
```

### Get Statistics

```bash
curl http://localhost:5000/api/statistics
```

### Export Todos

```bash
curl http://localhost:5000/api/export
```

### Bulk Delete

```bash
curl -X POST http://localhost:5000/api/todos/bulk/delete \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["id1", "id2", "id3"]
  }'
```

## Response Format

All API responses follow this format:

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "count": 10
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message here"
}
```

## Todo Item Structure

```json
{
  "id": "uuid-string",
  "title": "Task title",
  "description": "Detailed description",
  "priority": "high|medium|low",
  "due_date": "YYYY-MM-DD",
  "completed": false,
  "created_at": "2024-01-15T10:30:45.123456",
  "updated_at": "2024-01-15T10:30:45.123456"
}
```

## Statistics Response

```json
{
  "total": 15,
  "completed": 8,
  "pending": 7,
  "completion_percentage": 53.33,
  "by_priority": {
    "high": 3,
    "medium": 7,
    "low": 5
  }
}
```

## Local Storage

Todos are automatically saved to `todos.json` file in the application directory. This file contains all your tasks and persists across application restarts.

### Storage File Format

```json
{
  "todos": [
    {
      "id": "...",
      "title": "...",
      "description": "...",
      "priority": "...",
      "due_date": "...",
      "completed": false,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "last_updated": "2024-01-15T10:30:45.123456"
}
```

## Project Structure

```
todo-list-app/
├── app.py                   # Flask REST API
├── todo_list.py             # Core todo logic
├── todo_cli.py              # CLI interface
├── requirements.txt         # Python dependencies
├── todos.json              # Local storage file (auto-created)
├── templates/
│   └── index.html          # Web interface
├── static/
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
└── README.md               # This file
```

## Web Interface Features

### Add Tasks
- Enter task title, description, priority, and due date
- Quick add with Enter key

### Filter & Sort
- Filter by status (All, Pending, Completed)
- Filter by priority (High, Medium, Low)
- Sort by creation date, priority, or due date

### Manage Tasks
- Check/uncheck to mark complete
- Edit tasks inline
- Delete individual tasks
- Clear all tasks at once

### Statistics
- Real-time task count
- Completion percentage
- Priority breakdown

### Import/Export
- Export tasks to JSON backup
- Import tasks from JSON file

## Performance

- **Fast Operations**: All operations are optimized for speed
- **Scalable Storage**: Handles thousands of todos efficiently
- **Responsive UI**: Real-time updates without page reloads
- **Efficient Filtering**: Quick task filtering and sorting

## Data Persistence

All todos are automatically saved to the `todos.json` file:
- Changes are saved immediately after each operation
- Data persists across application restarts
- Backup/restore functionality through import/export

## Browser Compatibility

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Keyboard Shortcuts

- **Enter** in title field - Add new task
- **Escape** - Close modals/dialogs

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, modify `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Import/Export Issues

Ensure the JSON file is in the correct format:

```json
{
  "todos": [ ... ]
}
```

## Future Enhancements

- [ ] Due date reminders
- [ ] Categories/Tags
- [ ] Recurring tasks
- [ ] Collaboration features
- [ ] Dark mode
- [ ] Mobile app
- [ ] Cloud sync

## License

MIT License

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Support

For issues and feature requests, please open a GitHub issue.
