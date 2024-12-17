async function generateJavaCode() {
    const promptInput = document.getElementById('prompt-input');
    const codeSection = document.querySelector('.code-section');
    const outputSection = document.querySelector('.output-section');
    const testSection = document.querySelector('.test-section');
    const generatedCode = document.getElementById('generated-code');
    const codeEditor = document.getElementById('code-editor');
    const button = document.querySelector('.prompt-input button');
    
    try {
        button.disabled = true;
        button.classList.add('loading');
        
        const response = await fetch('/generate_java', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: promptInput.value
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate Java code');
        }
        
        // Show generated code
        generatedCode.textContent = data.code;
        codeEditor.value = data.code;
        codeSection.style.display = 'block';
        
        // Show test cases if available
        if (data.tests) {
            testSection.style.display = 'block';
            document.getElementById('test-results').innerHTML = formatTests(data.tests);
        }
        
        // Highlight syntax
        if (window.hljs) {
            hljs.highlightElement(generatedCode);
        }
    } catch (error) {
        showError(error.message);
    } finally {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

async function runCode() {
    const codeEditor = document.getElementById('code-editor');
    const codeDisplay = document.querySelector('.code-display');
    const outputSection = document.querySelector('.output-section');
    const outputElement = document.getElementById('code-output');
    const button = document.querySelector('.code-actions button:last-child');
    
    const code = codeDisplay.style.display === 'none' ? 
        codeEditor.value : 
        document.getElementById('generated-code').textContent;
    
    try {
        button.disabled = true;
        button.classList.add('loading');
        outputSection.style.display = 'block';
        outputElement.innerHTML = '<div class="loading">Running code...</div>';
        
        const response = await fetch('/run_java', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to run Java code');
        }
        
        outputElement.innerHTML = `<pre class="success">${formatOutput(data.result || '')}</pre>`;
    } catch (error) {
        outputElement.innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
    } finally {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

function editCode() {
    const codeDisplay = document.querySelector('.code-display');
    const codeEditor = document.querySelector('.code-editor');
    const editButton = document.querySelector('.code-actions button:first-child');
    
    if (codeDisplay.style.display !== 'none') {
        // Switch to editor
        codeDisplay.style.display = 'none';
        codeEditor.style.display = 'block';
        editButton.querySelector('.icon').textContent = '✓';
    } else {
        // Switch to display
        const code = document.getElementById('code-editor').value;
        document.getElementById('generated-code').textContent = code;
        codeDisplay.style.display = 'block';
        codeEditor.style.display = 'none';
        editButton.querySelector('.icon').textContent = '✎';
        
        // Highlight syntax
        if (window.hljs) {
            hljs.highlightElement(document.getElementById('generated-code'));
        }
    }
}

function formatOutput(output) {
    return output
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\n/g, '<br>')
        .replace(/ /g, '&nbsp;');
}

function formatTests(tests) {
    return tests.map(test => `
        <div class="test-case ${test.passed ? 'passed' : 'failed'}">
            <div class="test-header">
                <span class="test-name">${test.name}</span>
                <span class="test-status">${test.passed ? '✓' : '✗'}</span>
            </div>
            ${test.message ? `<div class="test-message">${test.message}</div>` : ''}
        </div>
    `).join('');
}

function showError(message) {
    const outputSection = document.querySelector('.output-section');
    const outputElement = document.getElementById('code-output');
    
    outputSection.style.display = 'block';
    outputElement.innerHTML = `<pre class="error">Error: ${message}</pre>`;
}
