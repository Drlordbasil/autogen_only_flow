document.addEventListener('DOMContentLoaded', () => {
    loadWorkflows();
    setupAnimations();
    setupIntersectionObserver();
});

class CodeExecutor {
    constructor() {
        this.status = 'idle';
        this.output = '';
        this.error = null;
        this.executionId = null;
    }

    async execute(code, language, options = {}) {
        try {
            this.status = 'running';
            this.updateUI();

            const response = await fetch('/execute_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code,
                    language,
                    ...options
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to execute code');
            }

            this.executionId = data.execution_id;
            await this.pollExecutionStatus();

            return {
                success: !data.error,
                result: data.result,
                error: data.error
            };

        } catch (error) {
            this.status = 'error';
            this.error = error.message;
            this.updateUI();
            throw error;
        }
    }

    async pollExecutionStatus() {
        const statusElement = document.getElementById('execution-status');
        statusElement.classList.add('loading');

        while (this.status === 'running') {
            const response = await fetch(`/execution_status/${this.executionId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                this.status = data.error ? 'error' : 'success';
                this.output = data.result;
                this.error = data.error;
                break;
            } else if (data.status === 'failed') {
                this.status = 'error';
                this.error = data.error;
                break;
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        statusElement.classList.remove('loading');
        this.updateUI();
    }

    updateUI() {
        const statusElement = document.getElementById('execution-status');
        const resultElement = document.getElementById('execution-result');
        const errorElement = document.getElementById('error-details');

        if (this.status === 'running') {
            statusElement.innerHTML = `
                Running
                <div class="loading-spinner"></div>
            `;
        } else {
            statusElement.textContent = this.getStatusText();
        }

        statusElement.className = `status ${this.status}`;

        if (this.output) {
            resultElement.innerHTML = formatOutput(this.output);
            fadeIn(resultElement);
        }

        if (this.error) {
            errorElement.textContent = this.error;
            fadeIn(errorElement);
        } else {
            fadeOut(errorElement);
        }
    }

    getStatusText() {
        const statusTexts = {
            idle: 'Ready',
            running: 'Executing...',
            success: 'Completed Successfully',
            error: 'Execution Failed'
        };
        return statusTexts[this.status] || this.status;
    }
}

class AutoGenAgent {
    constructor(name, role) {
        this.name = name;
        this.role = role;
        this.messages = [];
    }

    async sendMessage(message) {
        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sender: this.name,
                    role: this.role,
                    message
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            this.messages.push({
                role: this.role,
                content: message,
                timestamp: new Date()
            });

            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }
}

class WorkflowManager {
    constructor() {
        this.workflows = new Map();
        this.activeWorkflow = null;
    }

    async loadWorkflows() {
        try {
            const response = await fetch('/list_workflows');
            const data = await response.json();
            
            this.workflows.clear();
            data.forEach(workflow => {
                this.workflows.set(workflow.id, workflow);
            });

            this.updateWorkflowList();
        } catch (error) {
            console.error('Error loading workflows:', error);
            showError('Failed to load workflows');
        }
    }

    updateWorkflowList() {
        const workflowList = document.getElementById('workflow-list');
        workflowList.innerHTML = '';

        this.workflows.forEach((workflow, id) => {
            const workflowItem = document.createElement('div');
            workflowItem.className = 'workflow-item slide-in';
            workflowItem.innerHTML = `
                <h3>${workflow.name}</h3>
                <p>${workflow.description || 'No description available'}</p>
                <button onclick="workflowManager.executeWorkflow('${id}')" 
                        class="tooltip" 
                        data-tooltip="Execute this workflow">
                    Run Workflow
                </button>
            `;
            workflowList.appendChild(workflowItem);
        });
    }

    async executeWorkflow(workflowId) {
        try {
            const workflow = this.workflows.get(workflowId);
            if (!workflow) {
                throw new Error('Workflow not found');
            }

            this.activeWorkflow = workflowId;
            const statusElement = document.getElementById('workflow-status');
            statusElement.className = 'status running';
            statusElement.textContent = 'Executing workflow...';

            const response = await fetch(`/execute_workflow/${workflowId}`, {
                method: 'POST'
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to execute workflow');
            }

            statusElement.className = 'status success';
            statusElement.textContent = 'Workflow completed successfully';

            const outputElement = document.getElementById('workflow-output');
            outputElement.innerHTML = formatOutput(data.result);
            fadeIn(outputElement);

        } catch (error) {
            console.error('Error executing workflow:', error);
            const statusElement = document.getElementById('workflow-status');
            statusElement.className = 'status error';
            statusElement.textContent = `Workflow failed: ${error.message}`;
        }
    }
}

// Initialize global instances
const codeExecutor = new CodeExecutor();
const assistantAgent = new AutoGenAgent('assistant', 'assistant');
const userAgent = new AutoGenAgent('user', 'user');
const workflowManager = new WorkflowManager();

async function runCode(code, language) {
    try {
        const result = await codeExecutor.execute(code, language);
        if (result.success) {
            displayResult(result.result);
        } else {
            displayError(result.error);
        }
    } catch (error) {
        displayError(error.message);
    }
}

function displayResult(result) {
    const outputElement = document.getElementById(`${language}-output`);
    outputElement.innerHTML = formatOutput(result);
    fadeIn(outputElement);
}

function displayError(error) {
    const errorElement = document.getElementById('error-details');
    errorElement.textContent = error;
    fadeIn(errorElement);
}

function formatOutput(output) {
    if (!output) return '';
    
    // Escape HTML to prevent XSS
    const escaped = output.replace(/[&<>"']/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[char]));

    // Add syntax highlighting for code blocks
    return escaped.replace(/```(\w+)?\n([\s\S]+?)\n```/g, (_, lang, code) => `
        <div class="code-block ${lang || ''}">${code}</div>
    `);
}

function setupAnimations() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', e => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            button.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    const sections = document.querySelectorAll('.tool-section');
    sections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.1}s`;
    });
}

function fadeIn(element) {
    element.style.display = 'block';
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';
    
    requestAnimationFrame(() => {
        element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    });
}

function fadeOut(element) {
    element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, 300);
}

function setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.tool-section').forEach(section => {
        observer.observe(section);
    });
}

async function updateCode() {
    const filePath = document.getElementById('file-path').value.trim();
    const code = document.getElementById('update-code').value.trim();
    const outputElement = document.getElementById('update-output');

    if (!filePath || !code) {
        displayError('Please provide both file path and code');
        return;
    }

    try {
        const response = await fetch('/update_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_path: filePath, code })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to update code');
        }

        outputElement.innerHTML = `
            <div class="success-message">
                Code updated successfully!
                <button onclick="this.parentElement.remove()" class="close-button">×</button>
            </div>
        `;
        fadeIn(outputElement);

    } catch (error) {
        displayError(error.message);
    }
}

// Load workflows on startup
loadWorkflows();

async function runPythonTool() {
    const codeInput = document.getElementById('python-code');
    const outputElement = document.getElementById('python-output');
    const button = document.querySelector('#python-tools button');
    
    try {
        button.disabled = true;
        button.classList.add('loading');
        outputElement.innerHTML = '<div class="loading">Executing code...</div>';
        
        const response = await fetch('/run_python_tool', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: codeInput.value,
                language: 'python',
                options: {}
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to execute Python code');
        }
        
        outputElement.innerHTML = `<pre class="success">${formatOutput(data.result || '')}</pre>`;
    } catch (error) {
        outputElement.innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
    } finally {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

async function runJavaTool() {
    const codeInput = document.getElementById('java-code');
    const outputElement = document.getElementById('java-output');
    const button = document.querySelector('#java-tools button');
    
    try {
        button.disabled = true;
        button.classList.add('loading');
        outputElement.innerHTML = '<div class="loading">Executing code...</div>';
        
        const response = await fetch('/run_java_tool', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: codeInput.value,
                language: 'java',
                options: {}
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to execute Java code');
        }
        
        outputElement.innerHTML = `<pre class="success">${formatOutput(data.result || '')}</pre>`;
    } catch (error) {
        outputElement.innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
    } finally {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

// Codebase Analysis Functions
async function analyzeCodebase() {
    const path = document.getElementById('codebase-path').value;
    const resultContainer = document.getElementById('analysis-result');
    
    try {
        resultContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        const response = await fetch('/analyze_codebase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Analysis failed');
        }
        
        resultContainer.innerHTML = formatOutput(data.result);
    } catch (error) {
        resultContainer.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

async function solveProblem() {
    const description = document.getElementById('problem-description').value;
    const resultContainer = document.getElementById('solution-result');
    
    try {
        resultContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        const response = await fetch('/solve_problem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ problem_description: description })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Problem solving failed');
        }
        
        resultContainer.innerHTML = formatOutput(data.result);
    } catch (error) {
        resultContainer.innerHTML = `<div class="error">${error.message}</div>`;
    }
}

async function improveTests() {
    const description = document.getElementById('feature-description').value;
    const resultContainer = document.getElementById('test-result');
    
    try {
        resultContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        const response = await fetch('/improve_tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ feature_description: description })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Test improvement failed');
        }
        
        resultContainer.innerHTML = formatOutput(data.result);
    } catch (error) {
        resultContainer.innerHTML = `<div class="error">${error.message}</div>`;
    }
}
