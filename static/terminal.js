let currentPath = '';
let commandHistory = [];
let historyIndex = -1;
let commandCount = 0;

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('command-input');
    const output = document.getElementById('output');
    const clearBtn = document.getElementById('clearBtn');
    const helpBtn = document.getElementById('helpBtn');
    const statusElement = document.getElementById('status');
    const cwdElement = document.getElementById('cwd');
    const timeElement = document.getElementById('time');
    const commandCountElement = document.getElementById('commandCount');

    // Initialize
    updateCurrentPath();
    updateTime();
    setInterval(updateTime, 1000);

    // Input focus and event handling
    input.focus();
    
    // Keep input focused
    document.addEventListener('click', () => {
        if (!window.getSelection().toString()) {
            input.focus();
        }
    });

    // Command input handling
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const command = input.value.trim();
            if (command) {
                executeCommand(command);
                commandHistory.unshift(command);
                if (commandHistory.length > 50) commandHistory.pop();
                historyIndex = -1;
                input.value = '';
                commandCount++;
                updateCommandCount();
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (historyIndex < commandHistory.length - 1) {
                historyIndex++;
                input.value = commandHistory[historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                historyIndex--;
                input.value = commandHistory[historyIndex];
            } else if (historyIndex === 0) {
                historyIndex = -1;
                input.value = '';
            }
        } else if (e.key === 'Tab') {
            e.preventDefault();
            // Basic autocomplete for common commands
            const commands = ['ls', 'pwd', 'cd', 'mkdir', 'rm', 'cat', 'touch', 'mv', 'echo', 'help', 'clear', 'tree', 'search', 'cpu', 'mem', 'ps', 'sysinfo', 'history'];
            const currentValue = input.value.toLowerCase();
            const matches = commands.filter(cmd => cmd.startsWith(currentValue));
            if (matches.length === 1) {
                input.value = matches[0] + ' ';
            }
        }
    });

    // Button event handlers
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            clearTerminal();
        });
    }

    if (helpBtn) {
        helpBtn.addEventListener('click', () => {
            executeCommand('help');
        });
    }

    // Command chips functionality
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', function() {
            const command = this.getAttribute('data-cmd');
            input.value = command;
            executeCommand(command);
            commandHistory.unshift(command);
            if (commandHistory.length > 50) commandHistory.pop();
            historyIndex = -1;
            input.value = '';
            commandCount++;
            updateCommandCount();
        });
    });

    // Functions
    function executeCommand(command) {
        // Add command to output
        addToOutput(`<div class="command-line">
            <span class="command-prompt">$</span>
            <span class="command-text">${escapeHtml(command)}</span>
        </div>`);

        // Show loading state
        const container = document.querySelector('.terminal-input-container');
        if (container) container.classList.add('executing');
        if (statusElement) statusElement.textContent = 'Executing...';

        // Send command to server
        fetch('/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading state
            if (container) container.classList.remove('executing');
            if (statusElement) statusElement.textContent = 'Ready';

            // Handle clear command
            if (command.trim() === 'clear') {
                clearTerminal();
                return;
            }

            // Add output
            if (data.output) {
                const outputClass = data.output.includes('Error:') || data.output.includes('❌') ? 'error-output' :
                                  data.output.includes('✅') || data.output.includes('SUCCESS') ? 'success-output' :
                                  data.output.includes('INFO') || data.output.includes('🔥') ? 'info-output' : '';
                addToOutput(`<div class="command-output ${outputClass}">${escapeHtml(data.output)}</div>`);
            }

            // Update path if directory changed
            updateCurrentPath();
            
            // Scroll to bottom
            output.scrollTop = output.scrollHeight;
        })
        .catch(error => {
            if (container) container.classList.remove('executing');
            if (statusElement) statusElement.textContent = 'Error';
            addToOutput(`<div class="command-output error-output">Network error: ${error.message}</div>`);
        });
    }

    function addToOutput(html) {
        output.insertAdjacentHTML('beforeend', html);
        output.scrollTop = output.scrollHeight;
    }

    function clearTerminal() {
        output.innerHTML = `
            <div class="welcome-message">
                <pre class="welcome-ascii">
┌─────────────────────────────────────────────────────────────┐
│                    Python Terminal v2.0                     │
│                     Web Interface                           │
│                                                             │
│  Type 'help' to see available commands                      │
│  Use natural language - try "show me all files"             │
│  All commands are logged to .terminal_history               │
└─────────────────────────────────────────────────────────────┘
                </pre>
            </div>
        `;
    }

    function updateCurrentPath() {
        fetch('/cwd')
        .then(response => response.json())
        .then(data => {
            currentPath = data.cwd;
            if (cwdElement) cwdElement.textContent = currentPath;
        })
        .catch(error => {
            if (cwdElement) cwdElement.textContent = 'Error loading path';
        });
    }

    function updateTime() {
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString();
        }
    }

    function updateCommandCount() {
        if (commandCountElement) {
            commandCountElement.textContent = commandCount;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});