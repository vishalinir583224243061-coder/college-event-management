/**
 * AI Assistant Chat & Multi-Tool Engine
 * Connects frontend UI to Gemini-powered AI backend endpoints.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Chat form
    const chatForm = document.getElementById('aiChatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', handleAiChatSubmit);
    }

    // Generator forms
    setupGenerator('ideasForm', '/api/ai/ideas', 'ideasResultBox', 'ideasSubmitBtn');
    setupGenerator('descForm', '/api/ai/description', 'descResultBox', 'descSubmitBtn');
    setupGenerator('scheduleForm', '/api/ai/schedule', 'scheduleResultBox', 'scheduleSubmitBtn');
    setupGenerator('reminderForm', '/api/ai/reminder', 'reminderResultBox', 'reminderSubmitBtn');
    setupGenerator('reportForm', '/api/ai/report', 'reportResultBox', 'reportSubmitBtn');
    setupGenerator('feedbackForm', '/api/ai/feedback-summary', 'feedbackResultBox', 'feedbackSubmitBtn');
});

// Simple Markdown parser for AI responses
function parseMarkdown(text) {
    if (!text) return '';
    let html = text
        // Escape HTML
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Headers
        .replace(/^### (.*$)/gim, '<h5 class="fw-bold text-primary mt-3 mb-2">$1</h5>')
        .replace(/^## (.*$)/gim, '<h4 class="fw-bold mt-3 mb-2">$1</h4>')
        .replace(/^# (.*$)/gim, '<h3 class="fw-bold mt-3 mb-2">$1</h3>')
        // Bold and italic
        .replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        // Code blocks
        .replace(/```([a-z]*)\n([\s\S]*?)```/gim, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        // Blockquotes
        .replace(/^\> (.*$)/gim, '<blockquote class="border-start border-4 border-primary ps-3 my-2 text-muted">$1</blockquote>')
        // Bullet lists
        .replace(/^\* (.*$)/gim, '<li class="ms-3 mb-1">$1</li>')
        .replace(/^- (.*$)/gim, '<li class="ms-3 mb-1">$1</li>')
        // Newlines to line breaks (outside tables and pre)
        .replace(/\n\n/g, '<br><br>');

    // Basic markdown table parser
    if (html.includes('|')) {
        const lines = html.split('\n');
        let inTable = false;
        let tableHtml = '<div class="table-responsive my-2"><table class="table table-bordered table-sm">';
        let newLines = [];

        for (let line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                if (!inTable) {
                    inTable = true;
                    tableHtml = '<div class="table-responsive my-2"><table class="table table-bordered table-sm">';
                }
                if (trimmed.includes('---')) {
                    continue; // Skip markdown separator row
                }
                const cells = trimmed.split('|').slice(1, -1);
                tableHtml += '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
            } else {
                if (inTable) {
                    tableHtml += '</table></div>';
                    newLines.push(tableHtml);
                    inTable = false;
                }
                newLines.push(line);
            }
        }
        if (inTable) {
            tableHtml += '</table></div>';
            newLines.push(tableHtml);
        }
        html = newLines.join('\n');
    }

    return html;
}

// Handle Chat Message Submission
async function handleAiChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    appendChatMessage('user', message);

    // Add typing indicator
    const typingId = appendTypingIndicator();

    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await res.json();
        removeTypingIndicator(typingId);

        if (res.ok && data.success) {
            appendChatMessage('assistant', data.reply);
        } else {
            appendChatMessage('assistant', '⚠️ ' + (data.message || 'Apologies, I encountered an issue processing your request. Please try again!'));
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        appendChatMessage('assistant', '⚠️ Connection failed. Please verify your network.');
    }
}

function appendChatMessage(sender, text) {
    const container = document.getElementById('aiMessagesContainer');
    if (!container) return;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender} animate-fade-in`;

    if (sender === 'assistant') {
        bubble.innerHTML = `
            <div class="d-flex align-items-center gap-2 mb-1">
                <span class="badge bg-gradient-primary" style="font-size: 0.72rem;">🤖 CampusSphere AI</span>
                <button class="btn btn-sm btn-link p-0 text-muted ms-auto" onclick="copyMessageText(this)" title="Copy Response">
                    <i class="far fa-copy"></i>
                </button>
            </div>
            <div class="chat-content">${parseMarkdown(text)}</div>
        `;
    } else {
        bubble.innerHTML = `
            <div class="text-white-50 small mb-1">You</div>
            <div>${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        `;
    }

    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById('aiMessagesContainer');
    if (!container) return null;

    const id = 'typing_' + Date.now();
    const typingBubble = document.createElement('div');
    typingBubble.id = id;
    typingBubble.className = 'chat-bubble assistant animate-fade-in';
    typingBubble.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <span class="small text-muted">AI is crafting response</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    container.appendChild(typingBubble);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function sendPresetQuery(query) {
    const input = document.getElementById('aiChatInput');
    if (input) {
        input.value = query;
        const form = document.getElementById('aiChatForm');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
}

function copyMessageText(btn) {
    const bubble = btn.closest('.chat-bubble');
    const content = bubble.querySelector('.chat-content');
    if (content) {
        navigator.clipboard.writeText(content.innerText).then(() => {
            showToast('📋 Copied AI response to clipboard!', 'info');
        });
    }
}

// Generic AI Generator Form Runner
function setupGenerator(formId, apiEndpoint, resultBoxId, submitBtnId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById(submitBtnId);
        const resultBox = document.getElementById(resultBoxId);
        
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Generating with AI...';

        // Extract form data into object
        const formData = new FormData(form);
        const payload = {};
        formData.forEach((value, key) => { payload[key] = value; });

        try {
            const res = await fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
                        <span class="badge bg-gradient-primary px-3 py-2"><i class="fas fa-sparkles me-1"></i> AI Generated Result</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="copyResultBox('${resultBoxId}')">
                            <i class="far fa-copy me-1"></i> Copy to Clipboard
                        </button>
                    </div>
                    <div class="result-markdown-content">${parseMarkdown(data.result)}</div>
                `;
                resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                showToast('✨ AI generation complete!', 'success');
            } else {
                showToast(data.message || 'Generation failed', 'danger');
            }
        } catch (err) {
            showToast('Network error during AI generation', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

function copyResultBox(boxId) {
    const box = document.getElementById(boxId);
    if (!box) return;
    const contentEl = box.querySelector('.result-markdown-content');
    if (contentEl) {
        navigator.clipboard.writeText(contentEl.innerText).then(() => {
            showToast('📋 Copied to clipboard!', 'info');
        });
    }
}
