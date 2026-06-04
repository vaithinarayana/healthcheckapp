/**
 * To-Do List Application - Frontend JavaScript
 * Handles all client-side interactions and API communication
 */

const API_BASE_URL = '/api';
let currentFilter = 'all';
let todos = [];

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

/**
 * Format timestamp
 */
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Create a todo item element
 */
function createTodoElement(todo) {
    const div = document.createElement('div');
    div.className = `todo-item ${todo.completed ? 'completed' : ''}`;
    div.dataset.id = todo.id;
    div.dataset.priority = todo.priority;
    
    const priorityEmoji = {
        high: '🔴',
        medium: '🟡',
        low: '🟢'
    };
    
    const description = todo.description ? `<div class="todo-description">${todo.description}</div>` : '';
    const dueDate = todo.due_date ? `<span class="meta-item">📅 ${formatDate(todo.due_date)}</span>` : '';
    
    div.innerHTML = `
        <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
        <div class="todo-content">
            <div class="todo-header">
                <span class="todo-title">${escapeHtml(todo.title)}</span>
                <span class="todo-priority ${todo.priority}">${priorityEmoji[todo.priority]} ${todo.priority}</span>
            </div>
            ${description}
            <div class="todo-meta">
                ${dueDate}
                <span class="meta-item">📝 ${formatTime(todo.created_at)}</span>
            </div>
        </div>
        <div class="todo-actions">
            <button class="todo-btn edit" title="Edit">✏️</button>
            <button class="todo-btn delete" title="Delete">🗑️</button>
        </div>
    `;
    
    // Event listeners
    div.querySelector('.todo-checkbox').addEventListener('change', () => toggleTodo(todo.id));
    div.querySelector('.edit').addEventListener('click', () => editTodo(todo));
    div.querySelector('.delete').addEventListener('click', () => deleteTodo(todo.id));
    
    return div;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Load and display todos
 */
async function loadTodos() {
    try {
        const response = await fetch(`${API_BASE_URL}/todos?filter=${currentFilter}`);
        const result = await response.json();
        
        if (result.success) {
            todos = result.data;
            renderTodos();
            updateStatistics();
        }
    } catch (error) {
        console.error('Error loading todos:', error);
        showToast('Error loading todos', 'error');
    }
}

/**
 * Render todos in the DOM
 */
function renderTodos() {
    const container = document.getElementById('todosContainer');
    
    if (todos.length === 0) {
        container.innerHTML = '<div class="empty-state">✨ No tasks yet. Add one to get started!</div>';
        return;
    }
    
    container.innerHTML = '';
    todos.forEach(todo => {
        container.appendChild(createTodoElement(todo));
    });
}

/**
 * Update statistics
 */
async function updateStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        const result = await response.json();
        
        if (result.success) {
            const stats = result.data;
            document.getElementById('statTotal').textContent = stats.total;
            document.getElementById('statCompleted').textContent = stats.completed;
            document.getElementById('statPending').textContent = stats.pending;
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

/**
 * Add a new todo
 */
async function addTodo() {
    const title = document.getElementById('todoTitle').value.trim();
    const description = document.getElementById('todoDescription').value.trim();
    const priority = document.getElementById('todoPriority').value;
    const dueDate = document.getElementById('todoDueDate').value;
    
    if (!title) {
        showToast('Please enter a title', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/todos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                description,
                priority,
                due_date: dueDate || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('todoTitle').value = '';
            document.getElementById('todoDescription').value = '';
            document.getElementById('todoDueDate').value = '';
            document.getElementById('todoPriority').value = 'medium';
            
            showToast('Task added successfully');
            loadTodos();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error adding todo:', error);
        showToast('Error adding task', 'error');
    }
}

/**
 * Toggle todo completion
 */
async function toggleTodo(todoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}/toggle`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadTodos();
            showToast(result.message);
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling todo:', error);
        showToast('Error updating task', 'error');
    }
}

/**
 * Edit todo
 */
function editTodo(todo) {
    const newTitle = prompt('Edit title:', todo.title);
    if (newTitle === null) return;
    
    if (!newTitle.trim()) {
        showToast('Title cannot be empty', 'error');
        return;
    }
    
    updateTodoItem(todo.id, { title: newTitle.trim() });
}

/**
 * Update a todo item
 */
async function updateTodoItem(todoId, updates) {
    try {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Task updated successfully');
            loadTodos();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error updating todo:', error);
        showToast('Error updating task', 'error');
    }
}

/**
 * Delete a todo
 */
async function deleteTodo(todoId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Task deleted successfully');
            loadTodos();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting todo:', error);
        showToast('Error deleting task', 'error');
    }
}

/**
 * Clear all todos
 */
async function clearAllTodos() {
    if (!confirm('Are you sure you want to delete ALL tasks? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/clear`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('All tasks cleared');
            loadTodos();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing todos:', error);
        showToast('Error clearing tasks', 'error');
    }
}

/**
 * Export todos
 */
async function exportTodos() {
    try {
        const response = await fetch(`${API_BASE_URL}/export`);
        const result = await response.json();
        
        if (result.success) {
            showToast('Tasks exported successfully');
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Error exporting todos:', error);
        showToast('Error exporting tasks', 'error');
    }
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Add todo button
    document.getElementById('addTodoBtn').addEventListener('click', addTodo);
    
    // Enter key to add todo
    document.getElementById('todoTitle').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTodo();
    });
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            loadTodos();
        });
    });
    
    // Action buttons
    document.getElementById('exportBtn').addEventListener('click', exportTodos);
    document.getElementById('importBtn').addEventListener('click', () => {
        showToast('Import feature - save todos_import.json in the app folder', 'info');
    });
    document.getElementById('clearBtn').addEventListener('click', clearAllTodos);
}

/**
 * Initialize app
 */
function init() {
    initializeEventListeners();
    loadTodos();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
