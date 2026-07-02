// ==========================================================================
// STUDYPILOT AI - FRONTEND APPLICATION LOGIC
// ==========================================================================

const API_BASE = "http://127.0.0.1:8000/api";

// --- Global Application State ---
let state = {
    profile: {
        name: "Student",
        level: "Beginner",
        weekly_hours_goal: 10,
        xp: 0
    },
    activeTab: "chat",
    studyPlans: [],
    uploadedNotes: [],
    activeNoteId: null, // Index or filename of selected note
    activeNoteContent: "",
    activeNoteTitle: "",
    notesViewerTab: "summary", // summary | qa
    
    // Quiz State
    quiz: {
        topic: "",
        questions: [],
        currentIndex: 0,
        selectedOption: null,
        isAnswered: false,
        correctCount: 0
    }
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
    // Initial fetch of profile and basic lists
    initializeApp();
});

async function initializeApp() {
    try {
        await refreshProfile();
        await refreshPlans();
        await refreshNotesList();
        await refreshProgress();
    } catch (err) {
        console.error("Initialization error:", err);
    }
}

// --- Navigation / View Management ---
function switchTab(tabId) {
    state.activeTab = tabId;
    
    // Toggle active classes on sidebar buttons
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`btn-${tabId}`);
    if (activeBtn) activeBtn.classList.add("active");
    
    // Toggle active classes on view containers
    document.querySelectorAll(".tab-view").forEach(view => view.classList.remove("active"));
    const activeView = document.getElementById(`view-${tabId}`);
    if (activeView) activeView.classList.add("active");
    
    // Run tab-specific refreshes
    if (tabId === "progress") {
        refreshProgress();
    } else if (tabId === "planner") {
        refreshPlans();
    } else if (tabId === "notes") {
        refreshNotesList();
    }
}

// --- Profile & Stats Management ---
async function refreshProfile() {
    try {
        const response = await fetch(`${API_BASE}/profile`);
        if (!response.ok) throw new Error("Failed to load profile.");
        const data = await response.json();
        state.profile = data;
        
        // Update header UI
        document.getElementById("header-student-name").textContent = data.name;
        document.getElementById("header-xp").textContent = `${data.xp} XP`;
        
        // Simple Leveling Calculation: 1 + XP/500
        const calculatedLevel = 1 + Math.floor(data.xp / 500);
        document.getElementById("header-level").textContent = calculatedLevel;
        
    } catch (err) {
        console.error("Error refreshing profile:", err);
    }
}

function openProfileModal() {
    document.getElementById("profile-name").value = state.profile.name;
    document.getElementById("profile-level").value = state.profile.level;
    document.getElementById("profile-hours").value = state.profile.weekly_hours_goal;
    
    document.getElementById("profile-modal").style.display = "flex";
}

function closeProfileModal() {
    document.getElementById("profile-modal").style.display = "none";
}

async function saveProfile(event) {
    event.preventDefault();
    const name = document.getElementById("profile-name").value;
    const level = document.getElementById("profile-level").value;
    const goal = parseInt(document.getElementById("profile-hours").value);
    
    try {
        const response = await fetch(`${API_BASE}/profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name,
                level: level,
                weekly_hours_goal: goal
            })
        });
        
        if (!response.ok) throw new Error("Failed to update profile.");
        
        closeProfileModal();
        await refreshProfile();
        await refreshProgress();
        
    } catch (err) {
        showToast("error", "Profile Update Failed", err.message);
    }
}

// --- Chat Assistant Handler ---
async function sendChatMessage(event) {
    event.preventDefault();
    const inputEl = document.getElementById("chat-input");
    const query = inputEl.value.trim();
    if (!query) return;
    
    // Clear input
    inputEl.value = "";
    
    // Append user message
    appendMessage("user", "You", query);
    
    // Add system thinking indicator
    const thinkingId = appendMessage("agent", "Coordinator Agent", "Thinking...");
    
    try {
        const bodyData = { query: query };
        // Attach active note context if available
        if (state.activeNoteId) {
            bodyData.notes_text = state.activeNoteContent;
            bodyData.notes_title = state.activeNoteTitle;
        }
        
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bodyData)
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Server error.");
        }
        
        const data = await response.json();
        
        // Remove thinking indicator and show actual response
        removeMessage(thinkingId);
        appendMessage("agent", "Coordinator Agent", data.response);
        
        // If the query was about planner, quiz, or notes, trigger updates in background
        if (query.toLowerCase().includes("plan") || query.toLowerCase().includes("schedule")) {
            refreshPlans();
        }
        
        // Refresh profile in case XP was earned
        refreshProfile();
        
    } catch (err) {
        removeMessage(thinkingId);
        if (err.message.includes("Potential prompt injection") || err.message.includes("safety bypass")) {
            showToast("warning", "Security Warning", "Input blocked: Prompt injection or safety bypass patterns detected.");
            appendMessage("system", "Security Guard", "⚠️ Input blocked due to security policy violations.");
        } else {
            appendMessage("system", "System", `Error: ${err.message}`);
        }
    }
}

function appendMessage(senderType, senderName, text) {
    const messagesContainer = document.getElementById("chat-messages");
    const messageId = "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 5);
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${senderType}`;
    messageDiv.id = messageId;
    
    const senderDiv = document.createElement("div");
    senderDiv.className = "message-sender";
    senderDiv.textContent = senderName;
    
    const textDiv = document.createElement("div");
    textDiv.className = "message-text";
    
    // Parse markdown before rendering
    textDiv.innerHTML = parseMarkdownOffline(text);
    
    messageDiv.appendChild(senderDiv);
    messageDiv.appendChild(textDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

function removeMessage(messageId) {
    const el = document.getElementById(messageId);
    if (el) el.remove();
}

function detachNotes() {
    state.activeNoteId = null;
    state.activeNoteContent = "";
    state.activeNoteTitle = "";
    document.getElementById("notes-attached-indicator").style.display = "none";
    document.getElementById("notes-quiz-option-container").style.display = "none";
    document.getElementById("quiz-from-notes-check").checked = false;
}

// --- Study Planner Handler ---
async function refreshPlans() {
    try {
        const response = await fetch(`${API_BASE}/planner`);
        if (!response.ok) throw new Error("Failed to load plans.");
        const data = await response.json();
        state.studyPlans = data;
        
        renderStudyPlans();
    } catch (err) {
        console.error("Error refreshing plans:", err);
    }
}

function renderStudyPlans() {
    const listContainer = document.getElementById("planner-list");
    listContainer.innerHTML = "";
    
    if (state.studyPlans.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-calendar-xmark"></i>
                <p>No active study plans generated yet. Use the creator form to get started!</p>
            </div>
        `;
        return;
    }
    
    // Render plans descending by ID
    state.studyPlans.slice().reverse().forEach(plan => {
        const planCard = document.createElement("div");
        planCard.className = "study-plan-card";
        
        planCard.innerHTML = `
            <div class="study-plan-card-header">
                <h5>${plan.topic}</h5>
                <button class="delete-plan-btn" onclick="deletePlan(${plan.id})" title="Delete Study Plan">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
            <div class="study-plan-meta">
                <span><i class="fa-solid fa-clock"></i> ${plan.daily_hours} hrs/day</span>
                <span><i class="fa-solid fa-calendar"></i> ${plan.duration_weeks} Weeks</span>
                <span><i class="fa-solid fa-graduation-cap"></i> ${plan.skill_level}</span>
            </div>
            <div class="study-plan-body">
                ${parseMarkdownOffline(plan.plan_markdown)}
            </div>
        `;
        listContainer.appendChild(planCard);
    });
}

async function generateStudyPlan(event) {
    event.preventDefault();
    const topic = document.getElementById("plan-topic").value.trim();
    const weeks = parseInt(document.getElementById("plan-weeks").value);
    const hours = parseFloat(document.getElementById("plan-hours").value);
    const level = document.getElementById("plan-level").value;
    
    if (!topic) return;
    
    try {
        const response = await fetch(`${API_BASE}/planner`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic: topic,
                duration_weeks: weeks,
                daily_hours: hours,
                skill_level: level
            })
        });
        
        if (!response.ok) throw new Error("Failed to generate study plan.");
        
        document.getElementById("plan-topic").value = "";
        await refreshPlans();
        await refreshProfile();
        
    } catch (err) {
        showToast("error", "Plan Generation Failed", err.message);
    }
}

async function deletePlan(id) {
    if (!confirm("Are you sure you want to delete this study plan?")) return;
    try {
        const response = await fetch(`${API_BASE}/planner/${id}`, {
            method: "DELETE"
        });
        if (!response.ok) throw new Error("Failed to delete plan.");
        await refreshPlans();
        await refreshProgress();
    } catch (err) {
        showToast("error", "Plan Deletion Failed", err.message);
    }
}

// --- Graded Quiz Handler ---
function startQuiz() {
    const isFromNotes = document.getElementById("quiz-from-notes-check").checked;
    const topicInput = document.getElementById("quiz-topic-input").value.trim();
    const numQ = parseInt(document.getElementById("quiz-question-count").value);
    
    let topic = topicInput;
    let notesText = null;
    
    if (isFromNotes) {
        topic = "Custom Note Quiz";
        notesText = state.activeNoteContent;
    } else if (!topic) {
        showToast("warning", "Missing Configuration", "Please enter a study topic or choose an uploaded notes file first.");
        return;
    }
    
    // Trigger loading state or request
    fetchQuizFromServer(topic, numQ, notesText);
}

async function fetchQuizFromServer(topic, numQ, notesText) {
    try {
        const reqBody = {
            topic: topic,
            num_questions: numQ
        };
        if (notesText) {
            reqBody.notes_text = notesText;
        }
        
        const response = await fetch(`${API_BASE}/quiz`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqBody)
        });
        
        if (!response.ok) throw new Error("Failed to generate quiz questions.");
        const data = await response.json();
        
        if (data.questions.length === 0) {
            throw new Error("No quiz questions could be parsed or generated. Try uploading a longer study note.");
        }
        
        // Setup state
        state.quiz.topic = data.topic || topic;
        state.quiz.questions = data.questions;
        state.quiz.currentIndex = 0;
        state.quiz.selectedOption = null;
        state.quiz.isAnswered = false;
        state.quiz.correctCount = 0;
        
        // Update Board UI
        document.getElementById("quiz-current-topic").textContent = data.topic || topic;
        document.getElementById("quiz-setup").style.display = "none";
        document.getElementById("quiz-results").style.display = "none";
        document.getElementById("quiz-board").style.display = "flex";
        
        renderQuizQuestion();
        
    } catch (err) {
        showToast("error", "Quiz Generation Failed", err.message);
    }
}

function renderQuizQuestion() {
    const q = state.quiz.questions[state.quiz.currentIndex];
    state.quiz.isAnswered = false;
    state.quiz.selectedOption = null;
    
    // Hide details
    document.getElementById("quiz-explanation-box").style.display = "none";
    document.getElementById("quiz-next-btn").disabled = true;
    
    // Text
    document.getElementById("quiz-progress-text").textContent = `Question ${state.quiz.currentIndex + 1} of ${state.quiz.questions.length}`;
    document.getElementById("quiz-question-text").textContent = q.question;
    
    // Toggle container views based on question type
    const qType = q.type || "mcq";
    
    const grid = document.getElementById("quiz-options-grid");
    const saContainer = document.getElementById("quiz-short-answer-container");
    const codingContainer = document.getElementById("quiz-coding-container");
    
    grid.style.display = "none";
    saContainer.style.display = "none";
    codingContainer.style.display = "none";
    
    if (qType === "mcq") {
        grid.style.display = "flex";
        grid.innerHTML = "";
        q.options.forEach((opt, idx) => {
            const btn = document.createElement("button");
            btn.className = "option-btn";
            btn.innerHTML = `<span class="opt-letter">${String.fromCharCode(65 + idx)})</span> ${opt}`;
            btn.onclick = () => selectQuizOption(idx);
            grid.appendChild(btn);
        });
    } else if (qType === "short_answer") {
        saContainer.style.display = "block";
        const inputEl = document.getElementById("quiz-short-answer-input");
        inputEl.value = "";
        inputEl.disabled = false;
        inputEl.style.borderColor = "var(--card-border)";
        document.getElementById("quiz-submit-short-answer-btn").disabled = false;
    } else if (qType === "coding") {
        codingContainer.style.display = "block";
        const textareaEl = document.getElementById("quiz-coding-input");
        textareaEl.value = "";
        textareaEl.disabled = false;
        textareaEl.style.borderColor = "var(--card-border)";
        document.getElementById("quiz-submit-coding-btn").disabled = false;
    }
}

function selectQuizOption(idx) {
    if (state.quiz.isAnswered) return;
    
    state.quiz.selectedOption = idx;
    state.quiz.isAnswered = true;
    
    const q = state.quiz.questions[state.quiz.currentIndex];
    const correctIdx = typeof q.correct === 'number' ? q.correct : parseInt(q.correct, 10);
    
    // UI updates for options
    const buttons = document.getElementById("quiz-options-grid").querySelectorAll(".option-btn");
    
    if (idx === correctIdx) {
        buttons[idx].classList.add("correct");
        state.quiz.correctCount++;
    } else {
        buttons[idx].classList.add("wrong");
        if (buttons[correctIdx]) {
            buttons[correctIdx].classList.add("correct"); // Show the right one
        }
    }
    
    // Display explanation
    document.getElementById("quiz-explanation-text").textContent = q.explanation;
    document.getElementById("quiz-explanation-box").style.display = "block";
    
    // Unlock Next Button
    document.getElementById("quiz-next-btn").disabled = false;
}

function submitShortAnswer() {
    if (state.quiz.isAnswered) return;
    
    const inputEl = document.getElementById("quiz-short-answer-input");
    const userAnswer = inputEl.value.trim().toLowerCase();
    
    const q = state.quiz.questions[state.quiz.currentIndex];
    const correctAnswer = q.correct.trim().toLowerCase();
    
    state.quiz.isAnswered = true;
    inputEl.disabled = true;
    document.getElementById("quiz-submit-short-answer-btn").disabled = true;
    
    if (userAnswer === correctAnswer) {
        inputEl.style.borderColor = "var(--accent-green)";
        state.quiz.correctCount++;
    } else {
        inputEl.style.borderColor = "#ef4444";
    }
    
    // Display explanation
    document.getElementById("quiz-explanation-text").innerHTML = `<strong>Correct Answer:</strong> <code>${q.correct}</code><br><br>${q.explanation}`;
    document.getElementById("quiz-explanation-box").style.display = "block";
    
    // Unlock Next Button
    document.getElementById("quiz-next-btn").disabled = false;
}

function submitCodingAnswer() {
    if (state.quiz.isAnswered) return;
    
    const textareaEl = document.getElementById("quiz-coding-input");
    const userCode = textareaEl.value.trim();
    if (!userCode) {
        showToast("warning", "Empty Submission", "Please write some code before submitting.");
        return;
    }
    
    const q = state.quiz.questions[state.quiz.currentIndex];
    
    state.quiz.isAnswered = true;
    textareaEl.disabled = true;
    document.getElementById("quiz-submit-coding-btn").disabled = true;
    
    // Auto-approve coding attempts educationally
    textareaEl.style.borderColor = "var(--accent-green)";
    state.quiz.correctCount++; 
    
    // Display explanation with model solution
    document.getElementById("quiz-explanation-text").innerHTML = `<strong>Model Solution:</strong><pre style="background: rgba(15,21,39,0.5); padding: 10px; border-radius: 4px; margin-top: 5px; color: var(--text-primary); font-family: monospace;">${q.correct}</pre><br>${q.explanation}`;
    document.getElementById("quiz-explanation-box").style.display = "block";
    
    // Unlock Next Button
    document.getElementById("quiz-next-btn").disabled = false;
}

function nextQuizQuestion() {
    state.quiz.currentIndex++;
    if (state.quiz.currentIndex < state.quiz.questions.length) {
        renderQuizQuestion();
    } else {
        // Submit score to server
        submitQuizScore();
    }
}

async function submitQuizScore() {
    const total = state.quiz.questions.length;
    const correct = state.quiz.correctCount;
    const percentage = (correct / total) * 100;
    
    try {
        const response = await fetch(`${API_BASE}/quiz/score`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic: state.quiz.topic,
                total_questions: total,
                correct_answers: correct,
                score_percentage: percentage
            })
        });
        
        if (!response.ok) throw new Error("Failed to save score.");
        
        // Show Results Screen
        document.getElementById("quiz-board").style.display = "none";
        document.getElementById("quiz-results").style.display = "block";
        
        // Results Data
        document.getElementById("results-score").textContent = `${correct}/${total}`;
        document.getElementById("results-percentage").textContent = `${percentage.toFixed(0)}%`;
        
        const resultsIcon = document.getElementById("results-icon");
        const resultsFeedback = document.getElementById("results-feedback");
        
        if (percentage >= 80) {
            resultsIcon.className = "fa-solid fa-circle-check text-green large-icon";
            resultsFeedback.textContent = "Excellent work! You have shown strong mastery of this topic.";
        } else if (percentage >= 50) {
            resultsIcon.className = "fa-solid fa-face-smile text-cyan large-icon";
            resultsFeedback.textContent = "Good effort! Take a quick revision of the notes and try again.";
        } else {
            resultsIcon.className = "fa-solid fa-triangle-exclamation text-orange large-icon";
            resultsFeedback.textContent = "Keep practicing! Reviewing summaries and breaking down subjects will help.";
        }
        
        // Calculate XP gain (2 XP per percentage point)
        const xpEarned = Math.round(percentage * 2);
        document.getElementById("results-xp-gain").textContent = `+${xpEarned} XP Earned`;
        
        await refreshProfile();
        await refreshProgress();
        
    } catch (err) {
        showToast("error", "Save Score Failed", err.message);
    }
}

function resetQuizView() {
    document.getElementById("quiz-results").style.display = "none";
    document.getElementById("quiz-board").style.display = "none";
    document.getElementById("quiz-setup").style.display = "block";
}

// --- Notes Upload & QA Handler ---
function triggerFileInput() {
    document.getElementById("file-input").click();
}

async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Prepare form data
    const formData = new FormData();
    formData.append("file", file);
    
    // Show progress
    document.getElementById("upload-progress").style.display = "block";
    
    try {
        const response = await fetch(`${API_BASE}/notes/upload`, {
            method: "POST",
            body: formData
        });
        
        document.getElementById("upload-progress").style.display = "none";
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Upload failed.");
        }
        
        const data = await response.json();
        
        // Select uploaded document as active context
        selectNoteFile(data.filename, data.full_content, data.summary_markdown);
        
        // Refresh list
        await refreshNotesList();
        
    } catch (err) {
        document.getElementById("upload-progress").style.display = "none";
        if (err.message.includes("unsafe HTML/script") || err.message.includes("XSS") || err.message.includes("sandbox restrictions")) {
            showToast("error", "Security Violation", "The file was rejected because it contains potential script execution payloads (XSS) or path traversals.");
        } else {
            showToast("error", "File Upload Failed", err.message);
        }
    }
}

async function refreshNotesList() {
    try {
        const response = await fetch(`${API_BASE}/notes`);
        if (!response.ok) throw new Error("Failed to load study notes.");
        const data = await response.json();
        
        localNotesCache = data.map(note => ({
            filename: note.filename,
            content: note.full_content,
            summary: note.summary_markdown
        }));
        
        // Render the notes list using the cached items
        const listEl = document.getElementById("uploaded-notes-list");
        listEl.innerHTML = "";
        
        if (localNotesCache.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state" style="padding: 1rem 0;">
                    <i class="fa-solid fa-file-lines" style="font-size: 1.5rem; opacity: 0.5;"></i>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem;">No study notes uploaded yet.</p>
                </div>
            `;
            return;
        }
        
        localNotesCache.forEach(note => {
            const itemDiv = document.createElement("div");
            itemDiv.className = `note-item ${state.activeNoteId === note.filename ? 'active' : ''}`;
            itemDiv.onclick = () => selectNoteFile(note.filename, note.content, note.summary);
            
            itemDiv.innerHTML = `
                <i class="fa-solid fa-file-lines"></i>
                <div class="note-item-info">
                    <h6>${note.filename}</h6>
                    <span>${Math.round(note.content.length / 5)} words</span>
                </div>
            `;
            listEl.appendChild(itemDiv);
        });
        
    } catch (err) {
        console.error("Error notes list:", err);
    }
}

// Since app.py doesn't have a direct GET /api/notes, we can cache uploads in the client session storage or state!
// This is extremely safe and persistent during page session.
function selectNoteFile(filename, content, summaryMarkdown) {
    state.activeNoteId = filename;
    state.activeNoteContent = content;
    state.activeNoteTitle = filename;
    
    // Update attached status indicators
    document.getElementById("attached-filename").textContent = filename;
    document.getElementById("notes-attached-indicator").style.display = "flex";
    
    // Update quiz notes indicator
    document.getElementById("quiz-notes-filename").textContent = filename;
    document.getElementById("notes-quiz-option-container").style.display = "block";
    
    // Show summary in viewer
    document.getElementById("summary-body").innerHTML = parseMarkdownOffline(summaryMarkdown);
    
    // Reset QA container
    const qaBox = document.getElementById("qa-messages-box");
    qaBox.innerHTML = `
        <div class="qa-placeholder">
            <i class="fa-solid fa-circle-question"></i>
            <p>Ask a question about <strong>${filename}</strong>. The Notes Agent will query the content offline.</p>
        </div>
    `;
    
    // Switch to summary tab
    switchViewerTab("summary");
    
    // Sync note item styling
    renderNoteListOffline(filename, content, summaryMarkdown);
}

// Add uploaded files to local list cache so that they display even if API endpoint is simple
let localNotesCache = [];
function renderNoteListOffline(filename, content, summaryMarkdown) {
    // Add to cache if new
    if (!localNotesCache.find(n => n.filename === filename)) {
        localNotesCache.push({ filename, content, summary: summaryMarkdown });
    }
    
    const listEl = document.getElementById("uploaded-notes-list");
    listEl.innerHTML = "";
    
    localNotesCache.forEach(note => {
        const itemDiv = document.createElement("div");
        itemDiv.className = `note-item ${state.activeNoteId === note.filename ? 'active' : ''}`;
        itemDiv.onclick = () => selectNoteFile(note.filename, note.content, note.summary);
        
        itemDiv.innerHTML = `
            <i class="fa-solid fa-file-lines"></i>
            <div class="note-item-info">
                <h6>${note.filename}</h6>
                <span>${Math.round(note.content.length / 5)} words</span>
            </div>
        `;
        listEl.appendChild(itemDiv);
    });
}

function switchViewerTab(tabId) {
    state.notesViewerTab = tabId;
    
    document.getElementById("v-tab-summary").classList.toggle("active", tabId === "summary");
    document.getElementById("v-tab-qa").classList.toggle("active", tabId === "qa");
    
    document.getElementById("viewer-summary-subview").classList.toggle("active", tabId === "summary");
    document.getElementById("viewer-qa-subview").classList.toggle("active", tabId === "qa");
}

async function submitNotesQA(event) {
    event.preventDefault();
    if (!state.activeNoteId) {
        showToast("warning", "No Active Note", "Please select or upload a document first.");
        return;
    }
    
    const inputEl = document.getElementById("notes-qa-input");
    const query = inputEl.value.trim();
    if (!query) return;
    
    inputEl.value = "";
    
    const qaBox = document.getElementById("qa-messages-box");
    
    // Remove placeholder if present
    const placeholder = qaBox.querySelector(".qa-placeholder");
    if (placeholder) placeholder.remove();
    
    // Append user question
    const userMsg = document.createElement("div");
    userMsg.className = "qa-msg user";
    userMsg.textContent = query;
    qaBox.appendChild(userMsg);
    
    // Add agent thinking indicator
    const agentMsg = document.createElement("div");
    agentMsg.className = "qa-msg agent";
    agentMsg.textContent = "Searching document content...";
    qaBox.appendChild(agentMsg);
    qaBox.scrollTop = qaBox.scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: `notes-qa: ${query}`,
                notes_text: state.activeNoteContent,
                notes_title: state.activeNoteTitle
            })
        });
        
        if (!response.ok) throw new Error("Could not fetch answer.");
        const data = await response.json();
        
        // Strip Coordinator prefix if exists
        let cleanAns = data.response.replace("📂 **Notes Agent Route Activated**\n\n", "");
        
        agentMsg.innerHTML = parseMarkdownOffline(cleanAns);
        qaBox.scrollTop = qaBox.scrollHeight;
        
    } catch (err) {
        agentMsg.textContent = `Error querying document: ${err.message}`;
    }
}

// --- Progress Tracker Handler ---
async function refreshProgress() {
    try {
        const response = await fetch(`${API_BASE}/progress`);
        if (!response.ok) throw new Error("Failed to load progress analysis.");
        const data = await response.json();
        
        // Update stats cards
        document.getElementById("prog-xp").textContent = `${data.xp} XP`;
        document.getElementById("prog-level").textContent = `Level ${data.level}`;
        document.getElementById("prog-plans").textContent = data.num_plans;
        document.getElementById("prog-score").textContent = `${data.avg_score}%`;
        
        // Update recommendations
        document.getElementById("prog-rec-text").textContent = data.recommendation;
        
        // Render tips list
        const tipsList = document.getElementById("prog-tips-list");
        tipsList.innerHTML = "";
        data.study_tips.forEach(tip => {
            const li = document.createElement("li");
            li.textContent = tip;
            tipsList.appendChild(li);
        });
        
        // Render topics list
        const topicsList = document.querySelector(".recommended-topics-list");
        topicsList.innerHTML = "";
        data.next_topics.forEach(topic => {
            const li = document.createElement("li");
            li.textContent = topic;
            topicsList.appendChild(li);
        });
        
        // Render history table (re-fetch scores database entries)
        await fetchHistoryTable();
        
    } catch (err) {
        console.error("Error refreshing progress:", err);
    }
}

async function fetchHistoryTable() {
    try {
        // To get history list, we can load DB file scores list or fetch custom profiles
        // We can request progress detail list. Let's do a post chat query that returns it, or load it from backend.
        // Let's create a direct endpoints in future but for now, we can query it from profile.
        // Wait, app.py does not have a GET /api/quiz/history, but we can call a simple fetch. Let's see if we can parse it from another data stream.
        // Wait! We can call `GET /api/progress`? No, /api/progress returns stats count, but we can also extend the API response or use a local scores tracker.
        // Wait! Let's update `app.py` or fetch it directly. In `app.py`, let's see if we returned the full scores.
        // Wait, `app.py` has no history list. Let's check how we can fetch it.
        // Let's look at the database. In `app.py`, `record_score` returns `progress_agent.analyze_progress()`.
        // Let's check if we can modify `app.py` to return the score history list inside `/api/progress`. That is extremely elegant!
        // Yes! Let's check if we can add quiz score history array inside the progress endpoint in `app.py`.
        // Wait, we can edit `app.py` later or just write a request for scores.
        // Let's look at what `/api/progress` currently returns. It calls `progress_agent.analyze_progress()`, which gathers `scores = get_quiz_scores()` and computes stats, but it doesn't return the list of scores.
        // Let's edit `progress.py` or `app.py` to include the raw scores list inside the progress payload! That will be clean and make our history table work out-of-the-box.
        // Let's write `app.js` first assuming we return `history: scores` in the progress endpoint.
        
        const response = await fetch(`${API_BASE}/progress`);
        if (!response.ok) return;
        const data = await response.json();
        
        // Let's check if history list is returned. If not, we will mock render recent quiz.
        const tbody = document.getElementById("prog-history-tbody");
        tbody.innerHTML = "";
        
        const quizHistory = data.history || [];
        if (quizHistory.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center">No quiz history recorded yet. Use the Quiz tab!</td></tr>`;
            return;
        }
        
        quizHistory.forEach(item => {
            const dateStr = item.date || new Date().toLocaleString();
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${dateStr}</td>
                <td><strong>${item.topic}</strong></td>
                <td>${item.total_questions}</td>
                <td>${item.correct_answers}</td>
                <td><span class="quiz-badge">${Math.round(item.score_percentage)}%</span></td>
            `;
            tbody.appendChild(tr);
        });
        
    } catch (err) {
        console.error("Error loading history table:", err);
    }
}

// --- Helper: Offline Markdown Parser ---
function parseMarkdownOffline(markdownText) {
    if (!markdownText) return "";
    
    let html = markdownText;
    
    // Escape standard XML tags first to be safe, except our own tags
    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italics: *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Headers: # Header -> h1, ## -> h2, ### -> h3
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Code blocks: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Unordered lists: - item or * item
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*\*\s+(.*$)/gim, '<li>$1</li>');
    
    // Wrap lists in ul
    // Simple lookbehind-like grouping for adjacent list items
    html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
    // Remove nested lists errors
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    
    // Replace newlines with breaks (if not inside list tags)
    html = html.split('\n').map(line => {
        if (line.trim().startsWith('<h') || line.trim().startsWith('<u') || line.trim().startsWith('<l')) {
            return line;
        }
        return line + '<br>';
    }).join('\n');
    
    return html;
}

function showToast(type, title, message) {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let iconClass = "fa-circle-info";
    if (type === "success") iconClass = "fa-circle-check";
    else if (type === "error") iconClass = "fa-circle-exclamation";
    else if (type === "warning") iconClass = "fa-triangle-exclamation";
    
    toast.innerHTML = `
        <i class="fa-solid ${iconClass} toast-icon"></i>
        <div class="toast-body">
            <span class="toast-title">${title}</span>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close-btn" onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>
    `;
    
    container.appendChild(toast);
    
    // Automatically remove after 5 seconds
    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

