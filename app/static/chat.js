const STORAGE_KEY = "ai-workforce-chat-history";
const USER_KEY = "ai-workforce-user-id";

const agentConfig = {
    support: { label: "Support", className: "support" },
    sales: { label: "Sales", className: "sales" },
    ops: { label: "Ops", className: "ops" },
};

const starterPrompts = [
    "I need help with a refund on my order.",
    "Can you explain pricing for a growing team?",
    "Please update our onboarding workflow and CRM status.",
];

const state = {
    isLoading: false,
    userId: getOrCreateUserId(),
    history: loadHistory(),
};

const messagesContainer = document.getElementById("messages");
const messagesWrapper = document.getElementById("messages-wrapper");
const messageInput = document.getElementById("message-input");
const chatForm = document.getElementById("chat-form");
const sendButton = document.getElementById("send-btn");
const clearButton = document.getElementById("clear-chat");
const promptButtons = document.querySelectorAll("[data-prompt]");
const userBadge = document.getElementById("user-badge");
const conversationCount = document.getElementById("conversation-count");

document.addEventListener("DOMContentLoaded", () => {
    userBadge.textContent = String(state.userId);
    renderConversation();
    bindEvents();
    autoResizeInput();
    messageInput.focus();
});

function bindEvents() {
    chatForm.addEventListener("submit", sendMessage);
    clearButton.addEventListener("click", clearConversation);
    messageInput.addEventListener("input", autoResizeInput);
    promptButtons.forEach((button) => {
        button.addEventListener("click", () => {
            messageInput.value = button.dataset.prompt || "";
            autoResizeInput();
            messageInput.focus();
        });
    });
    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(event);
        }
    });
}

async function sendMessage(event) {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (!message || state.isLoading) {
        return;
    }

    state.isLoading = true;
    setComposerState(true);

    const userMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
    };
    state.history.push(userMessage);
    persistHistory();
    renderConversation();

    messageInput.value = "";
    autoResizeInput();
    showTyping();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                user_id: state.userId,
                history: state.history,
            }),
        });

        if (!response.ok) {
            throw new Error(`Request failed with ${response.status}`);
        }

        const payload = await response.json();
        renderAIMessage(payload);
    } catch (error) {
        removeTyping();
        state.history.push({
            role: "assistant",
            content: `The chat service hit an error: ${error.message}`,
            agent_type: "support",
            confidence: 0,
            timestamp: new Date().toISOString(),
        });
        persistHistory();
        renderConversation();
    } finally {
        state.isLoading = false;
        setComposerState(false);
        messageInput.focus();
    }
}

function renderAIMessage(payload) {
    removeTyping();
    state.history.push({
        role: "assistant",
        content: payload.response,
        agent_type: payload.agent_type,
        confidence: payload.confidence,
        timestamp: new Date().toISOString(),
    });
    persistHistory();
    renderConversation();
}

function showTyping() {
    removeTyping();
    const node = document.createElement("article");
    node.className = "message assistant typing";
    node.innerHTML = `
        <div class="message-meta">
            <span class="agent-tag support">Routing</span>
            <span class="confidence-text">Thinking through the best lane...</span>
        </div>
        <div class="bubble">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(node);
    scrollToBottom();
}

function removeTyping() {
    const node = messagesContainer.querySelector(".typing");
    if (node) {
        node.remove();
    }
}

function renderConversation() {
    messagesContainer.innerHTML = "";
    updateConversationMeta();

    if (!state.history.length) {
        const starter = document.createElement("section");
        starter.className = "starter-card";
        starter.innerHTML = `
            <p class="eyebrow">Start here</p>
            <h3>Run a real multi-agent thread</h3>
            <p>
                Ask a support question, a buying question, or an internal operations request and keep replying in the same thread.
            </p>
            <div class="starter-prompt-row">
                ${starterPrompts.map((prompt) => `<span class="starter-chip">${escapeHtml(prompt)}</span>`).join("")}
            </div>
        `;
        messagesContainer.appendChild(starter);
        return;
    }

    state.history.forEach((item) => {
        const messageNode = document.createElement("article");
        const isUser = item.role === "user";
        const agent = agentConfig[item.agent_type] || agentConfig.support;
        const timestamp = formatTimestamp(item.timestamp);
        messageNode.className = `message ${isUser ? "user" : "assistant"}`;

        if (isUser) {
            messageNode.innerHTML = `
                <div class="message-meta">
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="bubble">
                    <p>${escapeHtml(item.content)}</p>
                </div>
            `;
        } else {
            const confidence = formatConfidence(item.confidence);
            messageNode.innerHTML = `
                <div class="message-meta">
                    <span class="agent-tag ${agent.className}">${agent.label}</span>
                    <span class="confidence-text">${confidence}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="bubble">
                    <p>${escapeHtml(item.content)}</p>
                </div>
            `;
        }

        messagesContainer.appendChild(messageNode);
    });

    scrollToBottom();
}

function clearConversation() {
    state.history = [];
    persistHistory();
    renderConversation();
    messageInput.focus();
}

function setComposerState(isLoading) {
    sendButton.disabled = isLoading;
    messageInput.disabled = isLoading;
    sendButton.textContent = isLoading ? "Sending..." : "Send";
}

function autoResizeInput() {
    messageInput.style.height = "0px";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 180)}px`;
}

function persistHistory() {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state.history));
}

function loadHistory() {
    try {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        const parsed = stored ? JSON.parse(stored) : [];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function getOrCreateUserId() {
    const existing = window.localStorage.getItem(USER_KEY);
    if (existing) {
        return Number(existing);
    }

    const userId = Math.floor(Date.now() / 1000);
    window.localStorage.setItem(USER_KEY, String(userId));
    return userId;
}

function updateConversationMeta() {
    const messageCount = state.history.length;
    const label = messageCount === 1 ? "message" : "messages";
    conversationCount.textContent = `${messageCount} ${label}`;
}

function formatConfidence(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
        return "Confidence unavailable";
    }

    return `Confidence ${Math.round(value * 100)}%`;
}

function formatTimestamp(value) {
    if (!value) {
        return "just now";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "just now";
    }

    return date.toLocaleTimeString([], {
        hour: "numeric",
        minute: "2-digit",
    });
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
    });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, "<br>");
}
