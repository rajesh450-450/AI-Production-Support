// =========================================================
// AI PRODUCTION SUPPORT - CHAT UI
//
// 7.10.7 - Conversation List
// 8.1.6  - Observability UI
// 8.1.7  - Markdown Answer Rendering
//
// Responsibilities:
// - Manage current conversation ID
// - Send messages
// - Restore conversation history
// - Load conversation list
// - Select an existing conversation
// - Start a new conversation
// - Switch between Chat and Observability
// - Load execution observability data
// - Render assistant responses in readable Markdown
// =========================================================


// =========================================================
// DOM ELEMENTS
// =========================================================

const newChatButton =
    document.getElementById(
        "new-chat-button"
    );

const sendButton =
    document.getElementById(
        "send-button"
    );

const messageInput =
    document.getElementById(
        "message-input"
    );

const messages =
    document.getElementById(
        "messages"
    );

const conversationList =
    document.getElementById(
        "conversation-list"
    );

const conversationTitle =
    document.getElementById(
        "conversation-title"
    );

const conversationStatus =
    document.getElementById(
        "conversation-status"
    );


// =========================================================
// OBSERVABILITY DOM ELEMENTS
// =========================================================

const observabilityButton =
    document.getElementById(
        "observability-button"
    );

const chatView =
    document.getElementById(
        "chat-view"
    );

const observabilityView =
    document.getElementById(
        "observability-view"
    );


// =========================================================
// CURRENT CONVERSATION
// =========================================================

let currentConversationId =
    localStorage.getItem(
        "conversation_id"
    );


// =========================================================
// CURRENT EXECUTION
//
// Set after /api/v1/chat returns.
//
// This is used by the Observability page.
// =========================================================

let currentExecutionId =
    localStorage.getItem(
        "execution_id"
    );


// =========================================================
// INITIALIZE UI
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        showChatView();

        await loadConversationList();

        if (currentConversationId) {

            await restoreConversation(
                currentConversationId
            );

        }

    }
);


// =========================================================
// VIEW SWITCHING
// =========================================================


// ---------------------------------------------------------
// Show Chat
// ---------------------------------------------------------

function showChatView() {

    if (chatView) {

        chatView.style.display =
            "flex";

    }

    if (observabilityView) {

        observabilityView.style.display =
            "none";

    }

}


// ---------------------------------------------------------
// Show Observability
// ---------------------------------------------------------

function showObservabilityView() {

    if (chatView) {

        chatView.style.display =
            "none";

    }

    if (observabilityView) {

        observabilityView.style.display =
            "block";

    }

    loadObservability();

}


// =========================================================
// LOAD CONVERSATION LIST
// =========================================================

async function loadConversationList() {

    try {

        const response =
            await fetch(
                "/api/v1/chat/conversations"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load conversations."
            );

        }


        const data =
            await response.json();


        renderConversationList(
            data.conversations || []
        );

    }
    catch (error) {

        console.error(
            "Error loading conversations:",
            error
        );

    }

}


// =========================================================
// RENDER CONVERSATION LIST
// =========================================================

function renderConversationList(
    conversations
) {

    if (!conversationList) {

        return;

    }


    conversationList.innerHTML = "";


    if (!conversations.length) {

        const emptyMessage =
            document.createElement(
                "div"
            );

        emptyMessage.className =
            "conversation-empty";

        emptyMessage.textContent =
            "No conversations yet.";

        conversationList.appendChild(
            emptyMessage
        );

        return;

    }


    conversations.forEach(
        (conversation) => {

            const item =
                document.createElement(
                    "button"
                );


            item.className =
                "conversation-item";


            item.dataset.conversationId =
                conversation.conversation_id;


            item.textContent =
                conversation.title ||
                "Untitled Conversation";


            // -------------------------------------------------
            // Highlight current conversation
            // -------------------------------------------------

            if (
                conversation.conversation_id ===
                currentConversationId
            ) {

                item.classList.add(
                    "active"
                );

            }


            // -------------------------------------------------
            // Click conversation
            // -------------------------------------------------

            item.addEventListener(
                "click",
                async () => {

                    showChatView();

                    await selectConversation(
                        conversation.conversation_id,
                        conversation.title ||
                        "Conversation"
                    );

                }
            );


            conversationList.appendChild(
                item
            );

        }
    );

}


// =========================================================
// SELECT CONVERSATION
// =========================================================

async function selectConversation(
    conversationId,
    title
) {

    currentConversationId =
        conversationId;


    localStorage.setItem(
        "conversation_id",
        conversationId
    );


    if (conversationTitle) {

        conversationTitle.textContent =
            title;

    }


    if (conversationStatus) {

        conversationStatus.textContent =
            "Loading...";

    }


    updateActiveConversation();


    await restoreConversation(
        conversationId
    );

}


// =========================================================
// UPDATE ACTIVE CONVERSATION
// =========================================================

function updateActiveConversation() {

    const items =
        document.querySelectorAll(
            ".conversation-item"
        );


    items.forEach(
        (item) => {

            if (
                item.dataset.conversationId ===
                currentConversationId
            ) {

                item.classList.add(
                    "active"
                );

            }
            else {

                item.classList.remove(
                    "active"
                );

            }

        }
    );

}


// =========================================================
// RESTORE CONVERSATION
// =========================================================

async function restoreConversation(
    conversationId
) {

    try {

        if (conversationStatus) {

            conversationStatus.textContent =
                "Loading...";

        }


        const response =
            await fetch(
                `/api/v1/chat/${conversationId}/history`
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load conversation history."
            );

        }


        const data =
            await response.json();


        renderHistory(
            data.messages || []
        );


        if (conversationStatus) {

            conversationStatus.textContent =
                "Ready";

        }


        updateActiveConversation();

    }
    catch (error) {

        console.error(
            "Error restoring conversation:",
            error
        );


        if (conversationStatus) {

            conversationStatus.textContent =
                "Unable to load conversation.";

        }

    }

}


// =========================================================
// RENDER HISTORY
// =========================================================

function renderHistory(
    history
) {

    if (!messages) {

        return;

    }


    messages.innerHTML = "";


    if (!history.length) {

        showEmptyState();

        return;

    }


    history.forEach(
        (message) => {

            addMessage(
                message.role,
                message.text
            );

        }
    );

}


// =========================================================
// SHOW EMPTY STATE
// =========================================================

function showEmptyState() {

    if (!messages) {

        return;

    }


    const emptyState =
        document.createElement(
            "div"
        );


    emptyState.id =
        "empty-state";


    emptyState.className =
        "empty-state";


    emptyState.innerHTML = `
        <div class="empty-icon">
            ✦
        </div>

        <h2>
            Your support assistant is ready
        </h2>

        <p>
            Ask a production support question
            to begin an investigation.
        </p>
    `;


    messages.appendChild(
        emptyState
    );

}


// =========================================================
// ADD MESSAGE
// =========================================================

function addMessage(
    role,
    text
) {

    if (!messages) {

        return;

    }


    const message =
        document.createElement(
            "div"
        );


    // -----------------------------------------------------
    // Message container
    // -----------------------------------------------------

    if (role === "user") {

        message.className =
            "message user-message";

    }
    else {

        message.className =
            "message assistant-message";

    }


    // -----------------------------------------------------
    // Role label
    // -----------------------------------------------------

    const roleLabel =
        document.createElement(
            "div"
        );


    roleLabel.className =
        "message-role";


    roleLabel.textContent =
        role === "user"
            ? "User"
            : "Assistant";


    // -----------------------------------------------------
    // Message content
    //
    // IMPORTANT:
    //
    // User messages remain plain text.
    //
    // Assistant messages are rendered as Markdown so
    // headings, bullets, bold text, numbered lists, etc.
    // are readable in the UI.
    // -----------------------------------------------------

    const messageText =
        document.createElement(
            "div"
        );


    messageText.className =
        "message-text";


    if (role === "assistant") {

        messageText.innerHTML =
            renderMarkdown(
                text
            );

    }
    else {

        messageText.textContent =
            text;

    }


    // -----------------------------------------------------
    // Build message
    // -----------------------------------------------------

    message.appendChild(
        roleLabel
    );


    message.appendChild(
        messageText
    );


    // -----------------------------------------------------
    // Add to chat
    // -----------------------------------------------------

    messages.appendChild(
        message
    );


    // -----------------------------------------------------
    // Scroll to latest message
    // -----------------------------------------------------

    messages.scrollTop =
        messages.scrollHeight;

}


// =========================================================
// MARKDOWN RENDERER
//
// Lightweight renderer.
//
// Supported:
// - # Heading
// - ## Heading
// - ### Heading
// - **bold**
// - *italic*
// - `inline code`
// - ```code blocks```
// - bullet lists
// - numbered lists
// - blockquotes
// - horizontal rules
// - paragraphs
// - line breaks
//
// HTML from the model is escaped first, so raw HTML returned
// by the model is not executed in the browser.
// =========================================================

function renderMarkdown(
    markdown
) {

    if (
        markdown === null ||
        markdown === undefined
    ) {

        return "";

    }


    let text =
        String(markdown);


    // -----------------------------------------------------
    // Normalize line endings
    // -----------------------------------------------------

    text =
        text.replace(
            /\r\n/g,
            "\n"
        );


    text =
        text.replace(
            /\r/g,
            "\n"
        );


    // -----------------------------------------------------
    // Escape HTML first
    //
    // This prevents assistant-generated HTML/JavaScript
    // from being inserted into the page.
    // -----------------------------------------------------

    text =
        escapeHtml(
            text
        );


    // -----------------------------------------------------
    // Extract fenced code blocks temporarily
    // -----------------------------------------------------

    const codeBlocks = [];


    text =
        text.replace(
            /```([a-zA-Z0-9_+-]*)\n([\s\S]*?)```/g,
            (
                match,
                language,
                code
            ) => {

                const index =
                    codeBlocks.length;


                codeBlocks.push(
                    {
                        language:
                            language || "",
                        code:
                            code
                                .replace(
                                    /\n$/,
                                    ""
                                )
                    }
                );


                return `@@CODE_BLOCK_${index}@@`;

            }
        );


    // -----------------------------------------------------
    // Extract inline code temporarily
    // -----------------------------------------------------

    const inlineCodeBlocks = [];


    text =
        text.replace(
            /`([^`\n]+)`/g,
            (
                match,
                code
            ) => {

                const index =
                    inlineCodeBlocks.length;


                inlineCodeBlocks.push(
                    code
                );


                return `@@INLINE_CODE_${index}@@`;

            }
        );


    // -----------------------------------------------------
    // Escape Markdown special HTML characters already done.
    //
    // Convert headings.
    // -----------------------------------------------------

    text =
        text.replace(
            /^### (.+)$/gm,
            "<h4>$1</h4>"
        );


    text =
        text.replace(
            /^## (.+)$/gm,
            "<h3>$1</h3>"
        );


    text =
        text.replace(
            /^# (.+)$/gm,
            "<h2>$1</h2>"
        );


    // -----------------------------------------------------
    // Horizontal rule
    // -----------------------------------------------------

    text =
        text.replace(
            /^(\*\*\*|---|___)$/gm,
            "<hr>"
        );


    // -----------------------------------------------------
    // Blockquote
    // -----------------------------------------------------

    text =
        text.replace(
            /^> (.+)$/gm,
            "<blockquote>$1</blockquote>"
        );


    // -----------------------------------------------------
    // Bold
    // -----------------------------------------------------

    text =
        text.replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        );


    text =
        text.replace(
            /__(.+?)__/g,
            "<strong>$1</strong>"
        );


    // -----------------------------------------------------
    // Italic
    // -----------------------------------------------------

    text =
        text.replace(
            /(^|[^*])\*([^*\n]+)\*(?!\*)/g,
            "$1<em>$2</em>"
        );


    text =
        text.replace(
            /(^|[^_])_([^_\n]+)_(?!_)/g,
            "$1<em>$2</em>"
        );


    // -----------------------------------------------------
    // Unordered lists
    // -----------------------------------------------------

    text =
        text.replace(
            /(?:^|\n)((?:[-*+] .+(?:\n|$))+)/g,
            (
                match,
                list
            ) => {

                const items =
                    list
                        .trim()
                        .split("\n")
                        .map(
                            (line) =>
                                line.replace(
                                    /^[-*+] (.+)$/,
                                    "<li>$1</li>"
                                )
                        )
                        .join("");


                return `\n<ul>${items}</ul>\n`;

            }
        );


    // -----------------------------------------------------
    // Ordered lists
    // -----------------------------------------------------

    text =
        text.replace(
            /(?:^|\n)((?:\d+\. .+(?:\n|$))+)/g,
            (
                match,
                list
            ) => {

                const items =
                    list
                        .trim()
                        .split("\n")
                        .map(
                            (line) =>
                                line.replace(
                                    /^\d+\. (.+)$/,
                                    "<li>$1</li>"
                                )
                        )
                        .join("");


                return `\n<ol>${items}</ol>\n`;

            }
        );


    // -----------------------------------------------------
    // Restore inline code
    // -----------------------------------------------------

    inlineCodeBlocks.forEach(
        (
            code,
            index
        ) => {

            text =
                text.replace(
                    `@@INLINE_CODE_${index}@@`,
                    `<code>${code}</code>`
                );

        }
    );


    // -----------------------------------------------------
    // Restore fenced code blocks
    // -----------------------------------------------------

    codeBlocks.forEach(
        (
            block,
            index
        ) => {

            const languageClass =
                block.language
                    ? ` class="language-${escapeHtml(
                        block.language
                    )}"`
                    : "";


            text =
                text.replace(
                    `@@CODE_BLOCK_${index}@@`,
                    `<pre><code${languageClass}>${block.code}</code></pre>`
                );

        }
    );


    // -----------------------------------------------------
    // Convert remaining line breaks
    //
    // Do not add <br> inside structural HTML elements.
    // -----------------------------------------------------

    text =
        text.replace(
            /\n{2,}/g,
            "</p><p>"
        );


    text =
        text.replace(
            /\n/g,
            "<br>"
        );


    // -----------------------------------------------------
    // Avoid wrapping block-level HTML awkwardly.
    // -----------------------------------------------------

    text =
        text.replace(
            /<p><h([234])>/g,
            "<h$1>"
        );


    text =
        text.replace(
            /<\/h([234])><\/p>/g,
            "</h$1>"
        );


    text =
        text.replace(
            /<p><hr><\/p>/g,
            "<hr>"
        );


    text =
        text.replace(
            /<p><ul>/g,
            "<ul>"
        );


    text =
        text.replace(
            /<\/ul><\/p>/g,
            "</ul>"
        );


    text =
        text.replace(
            /<p><ol>/g,
            "<ol>"
        );


    text =
        text.replace(
            /<\/ol><\/p>/g,
            "</ol>"
        );


    text =
        text.replace(
            /<p><blockquote>/g,
            "<blockquote>"
        );


    text =
        text.replace(
            /<\/blockquote><\/p>/g,
            "</blockquote>"
        );


    // -----------------------------------------------------
    // Wrap normal content in paragraph
    // -----------------------------------------------------

    if (
        !text.startsWith("<") &&
        text.trim() !== ""
    ) {

        text =
            `<p>${text}</p>`;

    }


    return text;

}


// =========================================================
// NEW CHAT
// =========================================================

if (newChatButton) {

    newChatButton.addEventListener(
        "click",
        () => {

            // -------------------------------------------------
            // Return to Chat view
            // -------------------------------------------------

            showChatView();


            // -------------------------------------------------
            // Remove current conversation
            // -------------------------------------------------

            currentConversationId =
                null;


            localStorage.removeItem(
                "conversation_id"
            );


            // -------------------------------------------------
            // Remove current execution
            // -------------------------------------------------

            currentExecutionId =
                null;


            localStorage.removeItem(
                "execution_id"
            );


            // -------------------------------------------------
            // Reset header
            // -------------------------------------------------

            if (conversationTitle) {

                conversationTitle.textContent =
                    "New Conversation";

            }


            if (conversationStatus) {

                conversationStatus.textContent =
                    "Ready";

            }


            // -------------------------------------------------
            // Clear messages
            // -------------------------------------------------

            if (messages) {

                messages.innerHTML = "";

            }


            showEmptyState();


            // -------------------------------------------------
            // Remove active conversation
            // -------------------------------------------------

            updateActiveConversation();


            // -------------------------------------------------
            // Focus input
            // -------------------------------------------------

            if (messageInput) {

                messageInput.focus();

            }

        }
    );

}


// =========================================================
// SEND MESSAGE
// =========================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        async () => {

            const message =
                messageInput
                    ? messageInput.value.trim()
                    : "";


            if (!message) {

                return;

            }


            // -------------------------------------------------
            // Display user message immediately
            // -------------------------------------------------

            addMessage(
                "user",
                message
            );


            // -------------------------------------------------
            // Clear input
            // -------------------------------------------------

            if (messageInput) {

                messageInput.value = "";

            }


            // -------------------------------------------------
            // Update status
            // -------------------------------------------------

            if (conversationStatus) {

                conversationStatus.textContent =
                    "Investigating...";

            }


            sendButton.disabled =
                true;


            try {

                const response =
                    await fetch(
                        "/api/v1/chat",
                        {
                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    {
                                        message:
                                            message,

                                        conversation_id:
                                            currentConversationId
                                    }
                                )
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "Chat request failed."
                    );

                }


                const data =
                    await response.json();


                // -------------------------------------------------
                // Conversation ID
                // -------------------------------------------------

                currentConversationId =
                    data.conversation_id;


                if (currentConversationId) {

                    localStorage.setItem(
                        "conversation_id",
                        currentConversationId
                    );

                }


                // -------------------------------------------------
                // Execution ID
                //
                // Required by Observability.
                // -------------------------------------------------

                if (data.execution_id) {

                    currentExecutionId =
                        data.execution_id;


                    localStorage.setItem(
                        "execution_id",
                        currentExecutionId
                    );

                }


                // -------------------------------------------------
                // Display assistant response
                // -------------------------------------------------

                addMessage(
                    "assistant",
                    data.answer ||
                    "No answer was returned."
                );


                // -------------------------------------------------
                // Conversation title
                // -------------------------------------------------

                if (conversationTitle) {

                    conversationTitle.textContent =
                        message;

                }


                if (conversationStatus) {

                    conversationStatus.textContent =
                        "Ready";

                }


                // -------------------------------------------------
                // Refresh sidebar
                // -------------------------------------------------

                await loadConversationList();


                updateActiveConversation();

            }
            catch (error) {

                console.error(
                    "Error sending message:",
                    error
                );


                addMessage(
                    "assistant",
                    "Sorry, an error occurred while processing your request."
                );


                if (conversationStatus) {

                    conversationStatus.textContent =
                        "Error";

                }

            }
            finally {

                sendButton.disabled =
                    false;


                if (messageInput) {

                    messageInput.focus();

                }

            }

        }
    );

}


// =========================================================
// ENTER KEY
// =========================================================

if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                if (sendButton) {

                    sendButton.click();

                }

            }

        }
    );

}


// =========================================================
// OBSERVABILITY BUTTON
// =========================================================

if (observabilityButton) {

    observabilityButton.addEventListener(
        "click",
        () => {

            showObservabilityView();

        }
    );

}


// =========================================================
// LOAD OBSERVABILITY
// =========================================================

async function loadObservability() {

    const timeline =
        document.getElementById(
            "observability-timeline"
        );


    // ---------------------------------------------------------
    // No execution available
    // ---------------------------------------------------------

    if (!currentExecutionId) {

        showNoExecution();

        return;

    }


    try {

        if (timeline) {

            timeline.innerHTML = `
                <div class="timeline-empty">
                    Loading observability data...
                </div>
            `;

        }


        const response =
            await fetch(
                `/api/v1/observability/${currentExecutionId}`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load observability data."
            );

        }


        const data =
            await response.json();


        renderObservability(
            data
        );

    }
    catch (error) {

        console.error(
            "Observability error:",
            error
        );


        showObservabilityError();

    }

}


// =========================================================
// RENDER OBSERVABILITY
// =========================================================

function renderObservability(
    data
) {

    const metrics =
        data.metrics || {};


    // ---------------------------------------------------------
    // Metrics
    // ---------------------------------------------------------

    setText(
        "obs-status",
        data.status || "—"
    );


    setText(
        "obs-duration",
        formatDuration(
            metrics.duration_ms
        )
    );


    setText(
        "obs-llm-calls",
        metrics.llm_calls ?? 0
    );


    setText(
        "obs-tool-calls",
        metrics.tool_calls ?? 0
    );


    setText(
        "obs-retries",
        metrics.retries ?? 0
    );


    // ---------------------------------------------------------
    // Execution information
    // ---------------------------------------------------------

    setText(
        "obs-execution-id",
        data.id || "—"
    );


    setText(
        "obs-conversation-id",
        data.conversation_id ||
        currentConversationId ||
        "—"
    );


    // ---------------------------------------------------------
    // Timestamps
    // ---------------------------------------------------------

    setText(
        "obs-started",
        formatTimestamp(
            data.started_at
        )
    );


    setText(
        "obs-completed",
        formatTimestamp(
            data.completed_at
        )
    );


    // ---------------------------------------------------------
    // Timeline
    // ---------------------------------------------------------

    renderTimeline(
        data.events || []
    );

}


// =========================================================
// SET TEXT SAFELY
// =========================================================

function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (element) {

        element.textContent =
            value;

    }

}


// =========================================================
// FORMAT DURATION
// =========================================================

function formatDuration(
    milliseconds
) {

    if (
        milliseconds === null ||
        milliseconds === undefined
    ) {

        return "—";

    }


    if (
        milliseconds < 1000
    ) {

        return `${Math.round(
            milliseconds
        )} ms`;

    }


    return `${(
        milliseconds / 1000
    ).toFixed(1)} sec`;

}


// =========================================================
// FORMAT TIMESTAMP
// =========================================================

function formatTimestamp(
    timestamp
) {

    if (!timestamp) {

        return "—";

    }


    const date =
        new Date(
            timestamp
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "—";

    }


    return date.toLocaleString();

}


// =========================================================
// RENDER OBSERVABILITY TIMELINE
// =========================================================

function renderTimeline(
    events
) {

    const container =
        document.getElementById(
            "observability-timeline"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (!events.length) {

        container.innerHTML = `
            <div class="timeline-empty">
                No events available.
            </div>
        `;

        return;

    }


    events.forEach(
        (event) => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "timeline-event";


            const icon =
                event.level === "ERROR"
                    ? "✕"
                    : "✓";


            item.innerHTML = `
                <div class="timeline-icon">
                    ${icon}
                </div>

                <div class="timeline-content">

                    <div class="timeline-component">
                        ${escapeHtml(
                            event.component
                        )}
                    </div>

                    <div class="timeline-message">
                        ${escapeHtml(
                            event.message
                        )}
                    </div>

                    <div class="timeline-time">
                        ${formatTimestamp(
                            event.timestamp
                        )}
                    </div>

                </div>
            `;


            container.appendChild(
                item
            );

        }
    );

}


// =========================================================
// HTML SAFETY
// =========================================================

function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;

}


// =========================================================
// NO EXECUTION STATE
// =========================================================

function showNoExecution() {

    setText(
        "obs-status",
        "No execution"
    );


    setText(
        "obs-duration",
        "—"
    );


    setText(
        "obs-llm-calls",
        "—"
    );


    setText(
        "obs-tool-calls",
        "—"
    );


    setText(
        "obs-retries",
        "—"
    );


    setText(
        "obs-execution-id",
        "—"
    );


    setText(
        "obs-conversation-id",
        currentConversationId || "—"
    );


    setText(
        "obs-started",
        "—"
    );


    setText(
        "obs-completed",
        "—"
    );


    const timeline =
        document.getElementById(
            "observability-timeline"
        );


    if (timeline) {

        timeline.innerHTML = `
            <div class="timeline-empty">
                Send a support question first
                to view execution details.
            </div>
        `;

    }

}


// =========================================================
// OBSERVABILITY ERROR
// =========================================================

function showObservabilityError() {

    const timeline =
        document.getElementById(
            "observability-timeline"
        );


    if (timeline) {

        timeline.innerHTML = `
            <div class="timeline-empty">
                Unable to load observability data.
            </div>
        `;

    }

}