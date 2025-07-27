/**
 * Dashboard JavaScript Module
 * Clean, modular frontend code for SprintSync dashboard
 */

class DashboardController {
    constructor() {
        this.state = {
            showCreateModal: false,
            aiTaskTitle: '',
            aiResponse: '',
            filter: 'all',
            newTask: { title: '', description: '', status: 'todo' }
        };

        this.init();
    }

    // Global function for deleting tasks
    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            const token = this.getToken();
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                // Remove the task card from the DOM
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`) ||
                                document.querySelector(`.task-card:has(button[onclick*="${taskId}"])`);
                if (taskCard) {
                    taskCard.remove();
                }
                this.showToast('Task deleted successfully!', 'success');
            } else {
                this.showToast('Failed to delete task', 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showToast('Error deleting task', 'error');
        }
    }

    init() {
        console.log('Dashboard controller initialized');
        this.setupEventListeners();
        this.setupKeyboardHandlers();
    }

    setupEventListeners() {
        // Modal controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="open-modal"]')) {
                this.openModal();
            }
            if (e.target.matches('[data-action="close-modal"]')) {
                this.closeModal();
            }
        });

        // Form submission
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#createTaskForm')) {
                e.preventDefault();
                this.createTask();
            }
        });

        // AI suggestion buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="ai-suggest"]')) {
                const mode = e.target.dataset.mode || 'draft';
                this.getAISuggestion(mode);
            }
        });

        // Test button
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="test-create"]')) {
                this.testTaskCreation();
            }
        });
    }

    setupKeyboardHandlers() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.showCreateModal) {
                this.closeModal();
            }
        });
    }

    // Modal Management
    openModal() {
        console.log('Opening modal...');
        this.state.showCreateModal = true;
        this.updateModalVisibility();
    }

    closeModal() {
        console.log('Closing modal...');
        this.state.showCreateModal = false;
        this.resetForm();
        this.updateModalVisibility();
    }

    updateModalVisibility() {
        const modal = document.getElementById('createTaskModal');
        if (modal) {
            modal.style.display = this.state.showCreateModal ? 'flex' : 'none';
        }
    }

    resetForm() {
        this.state.newTask = { title: '', description: '', status: 'todo' };
        this.state.aiResponse = '';
        this.state.aiTaskTitle = '';

        // Reset form inputs
        const form = document.getElementById('createTaskForm');
        if (form) {
            form.reset();
        }
    }

    // Task Management
    async createTask() {
        // Get form data
        const title = document.getElementById('taskTitle')?.value?.trim();
        const description = document.getElementById('taskDescription')?.value?.trim();
        const status = document.getElementById('taskStatus')?.value || 'todo';

        if (!title) {
            this.showToast('Task title is required', 'error');
            return;
        }

        try {
            console.log('Creating task:', this.state.newTask);
            const token = this.getToken();

            const response = await fetch('/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    status: status
                })
            });

            if (response.ok) {
                this.showToast('Task created successfully!', 'success');
                this.closeModal();
                setTimeout(() => window.location.reload(), 1000);
            } else {
                const errorText = await response.text();
                this.showToast(`Failed to create task: ${response.status}`, 'error');
                console.error('Task creation error:', errorText);
            }
        } catch (error) {
            console.error('Task creation error:', error);
            this.showToast('Network error creating task', 'error');
        }
    }

    async testTaskCreation() {
        try {
            const response = await fetch('/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: JSON.stringify({
                    title: 'Test Task ' + Date.now(),
                    description: 'This is a test task',
                    status: 'todo'
                })
            });

            if (response.ok) {
                this.showToast('Test task created successfully!', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast(`Test failed: ${response.status}`, 'error');
            }
        } catch (error) {
            this.showToast('Test failed with error', 'error');
        }
    }

    // AI Integration
    async getAISuggestion(mode) {
        if (mode === 'draft') {
            const title = document.getElementById('aiTaskTitle')?.value?.trim();
            if (!title) {
                this.showToast('Please enter a task title first', 'error');
                return;
            }
            this.state.aiTaskTitle = title;
        }

        try {
            const data = mode === 'draft' ?
                { title: this.state.aiTaskTitle, mode } :
                { mode };

            const response = await fetch('/ai/suggest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.state.aiResponse = result.suggestion;

                // Display AI response
                this.displayAIResponse(result.suggestion);

                if (mode === 'draft') {
                    // Update description field in modal
                    const descriptionField = document.getElementById('taskDescription');
                    if (descriptionField) {
                        descriptionField.value = result.suggestion;
                    }
                }

                this.showToast('AI suggestion received!', 'success');
            } else {
                const errorData = await response.json();
                this.showToast(`Failed to get AI suggestion: ${errorData.detail}`, 'error');
            }
        } catch (error) {
            console.error('AI suggestion error:', error);
            this.showToast('Error getting AI suggestion', 'error');
        }
    }

            displayAIResponse(suggestion) {
            const responseDiv = document.getElementById('aiResponse');
            const responseText = document.getElementById('aiResponseText');

            if (responseDiv && responseText) {
                responseText.textContent = suggestion;
                responseDiv.classList.remove('hidden');

                // Add "Create Task" button after AI response
                this.addCreateTaskButton(suggestion);
            }
        }

        addCreateTaskButton(description) {
            const responseDiv = document.getElementById('aiResponse');
            if (!responseDiv) return;

            // Remove existing button if any
            const existingButton = responseDiv.querySelector('.create-task-btn');
            if (existingButton) {
                existingButton.remove();
            }

            // Create new button
            const button = document.createElement('button');
            button.className = 'create-task-btn mt-3 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm';
            button.textContent = '✨ Create Task with AI Description';
            button.onclick = () => this.createTaskWithAIDescription(description);

            responseDiv.appendChild(button);
        }

        createTaskWithAIDescription(description) {
            // Get the AI task title
            const aiTaskTitle = document.getElementById('aiTaskTitle')?.value?.trim();
            if (!aiTaskTitle) {
                this.showToast('Please enter a task title first', 'error');
                return;
            }

            // Fill the modal with AI-generated content
            const titleField = document.getElementById('taskTitle');
            const descriptionField = document.getElementById('taskDescription');

            if (titleField) titleField.value = aiTaskTitle;
            if (descriptionField) descriptionField.value = description;

            // Open the modal
            this.openModal();

            // Show success message
            this.showToast('AI description applied! Fill in any details and create your task.', 'success');
        }

    updateDescriptionField() {
        const descriptionField = document.getElementById('taskDescription');
        if (descriptionField) {
            descriptionField.value = this.state.newTask.description;
        }
    }

    // Utility Functions
    getToken() {
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('token='))
            ?.split('=')[1];
    }

    showToast(message, type = 'info') {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 p-4 rounded-md text-white z-50 ${
            type === 'error' ? 'bg-red-500' :
            type === 'success' ? 'bg-green-500' : 'bg-blue-500'
        }`;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            document.body.removeChild(toast);
        }, 3000);
    }

    // State Management
    updateState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    render() {
        // Update UI based on state
        this.updateModalVisibility();
        this.updateDescriptionField();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new DashboardController();

    // Make deleteTask globally accessible
    window.deleteTask = function(taskId) {
        window.dashboardController.deleteTask(taskId);
    };
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardController;
}