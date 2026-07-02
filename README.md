<div align="center">

<!-- ═══════════════════════════════════════════════════════════ -->
<!--                     <img width="1024" height="1536" alt="ChatGPT Image Jul 3, 2026, 02_38_21 AM" src="https://github.com/user-attachments/assets/87c87101-df19-447b-ad98-562ec6394e41" />
                             -->
<!-- ═══════════════════════════════════════════════════════════ -->

<svg width="900" height="220" viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0c29"/>
      <stop offset="50%" style="stop-color:#302b63"/>
      <stop offset="100%" style="stop-color:#24243e"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#a78bfa"/>
      <stop offset="100%" style="stop-color:#38bdf8"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="900" height="220" fill="url(#bg)" rx="16"/>

  <!-- Decorative grid lines -->
  <g stroke="#ffffff08" stroke-width="1">
    <line x1="0" y1="55" x2="900" y2="55"/>
    <line x1="0" y1="110" x2="900" y2="110"/>
    <line x1="0" y1="165" x2="900" y2="165"/>
    <line x1="225" y1="0" x2="225" y2="220"/>
    <line x1="450" y1="0" x2="450" y2="220"/>
    <line x1="675" y1="0" x2="675" y2="220"/>
  </g>

  <!-- Glowing orb left -->
  <circle cx="80" cy="110" r="70" fill="#a78bfa18"/>
  <circle cx="80" cy="110" r="40" fill="#a78bfa10"/>

  <!-- Glowing orb right -->
  <circle cx="820" cy="110" r="70" fill="#38bdf818"/>
  <circle cx="820" cy="110" r="40" fill="#38bdf810"/>

  <!-- Accent top line -->
  <rect x="340" y="0" width="220" height="3" fill="url(#accent)" rx="2"/>

  <!-- Main Title -->
  <text x="450" y="88" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-weight="800" font-size="46" fill="url(#accent)" filter="url(#glow)" letter-spacing="-1">StudyPilot AI</text>

  <!-- Subtitle -->
  <text x="450" y="120" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-weight="400" font-size="15" fill="#cbd5e1" letter-spacing="2">INTELLIGENT MULTI-AGENT LEARNING CONCIERGE</text>

  <!-- Divider line -->
  <line x1="330" y1="134" x2="570" y2="134" stroke="#ffffff20" stroke-width="1"/>

  <!-- Bottom tagline -->
  <text x="450" y="160" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#94a3b8">Google ADK  ·  MCP  ·  FastAPI  ·  Multi-Agent AI</text>

  <!-- Version pill -->
  <rect x="395" y="175" width="110" height="24" rx="12" fill="#a78bfa22" stroke="#a78bfa55" stroke-width="1"/>
  <text x="450" y="191" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#c4b5fd">v1.0 · MIT License</text>
</svg>

<br/>

<!-- Badges -->
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google-ADK_Concepts-4285F4?style=for-the-badge&logo=google&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Enabled-7C3AED?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

</div>

---

## 📖 Overview

**StudyPilot AI** is a full-stack, multi-agent AI learning platform that helps students **plan, learn, practice, revise, and track** academic progress through intelligent agent collaboration.

The project showcases modern AI application architecture by combining **Google Agent Development Kit (ADK) concepts**, **Model Context Protocol (MCP)** integration, **FastAPI**, secure backend services, and a clean glassmorphism dashboard — instead of relying on a single AI assistant, multiple specialized agents coordinate to deliver a personalized educational experience.

> 💡 **Built for learners, by a learner.** This project demonstrates real-world multi-agent AI design patterns applicable to production systems.

---

## 🖥️ Dashboard Preview

<div align="center">
<img width="1920" height="911" alt="StudyPilot AI Dashboard" src="https://github.com/user-attachments/assets/41f74b28-2388-402b-b311-e3631b1c12b7"/>
<br/>
<sub><i>Glassmorphism dashboard with real-time agent coordination</i></sub>
</div>

---

## ✨ Key Features

<div align="center">

| Feature | Description |
|---|---|
| 🤖 Multi-Agent System | 5 specialized AI agents coordinated by an orchestrator |
| 🧠 Google ADK Architecture | Agent abstraction, session state, sequential workflows |
| 🔌 MCP Integration | Reusable tools exposed via Model Context Protocol |
| 📅 Study Planner | Daily, weekly & monthly personalized learning roadmaps |
| 📝 Quiz Generator | MCQs, coding problems, short answers with explanations |
| 📚 Notes Analyzer | Auto-summary, key concepts, practice questions from uploads |
| 📈 Progress Tracking | XP system, levels, weak topic detection, recommendations |
| 🔒 Security-First | Input validation, prompt sanitization, upload sandboxing |

</div>

---

## 🤖 Multi-Agent System

StudyPilot AI coordinates **5 specialized AI agents** through a central orchestration layer:

```
                          ┌─────────────────────────┐
                          │      User Request        │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   🎯 Coordinator Agent   │  ← Routes intelligently
                          └──┬─────────┬────────┬───┘
                             │         │        │
               ┌─────────────▼─┐  ┌────▼────┐ ┌▼──────────────┐
               │ 📅 Study      │  │ 📝 Quiz │ │ 📚 Notes      │
               │ Planner Agent │  │ Generator│ │ Analyzer Agent│
               └──────┬────────┘  └────┬────┘ └──────┬────────┘
                      │                │              │
                      └────────────────┼──────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │  📈 Progress Tracker     │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │      Final Response      │
                          └─────────────────────────┘
```

### Agent Responsibilities

| Agent | Role |
|---|---|
| 🎯 **Coordinator** | Parses intent, routes to the right specialist |
| 📅 **Study Planner** | Generates adaptive learning schedules |
| 📝 **Quiz Generator** | Creates topic-specific assessments |
| 📚 **Notes Analyzer** | Processes and extracts insights from uploads |
| 📈 **Progress Tracker** | Monitors XP, weak areas, and recommendations |

---

## 🧠 Google ADK Inspired Architecture

The project follows Google ADK design principles:

- **Agent Abstraction** — each agent is a self-contained module with a defined role
- **Session State Management** — persistent context across conversation turns
- **Sequential Workflows** — chained agent execution when needed
- **Agent Coordination** — intelligent routing without hardcoded rules
- **Modular Architecture** — plug-and-play agents without breaking the system

> The implementation mirrors ADK design patterns while remaining fully deployable locally — no cloud dependency required.

---

## 🔌 Model Context Protocol (MCP)

StudyPilot AI includes a **built-in MCP server** that exposes agent capabilities as reusable tools, making them accessible from any MCP-compatible client.

### Available MCP Tools

```python
generate_study_plan(subject, level, hours_per_day, duration)
generate_quiz(topic, difficulty, question_count, question_type)
analyze_notes(content, output_type)  # summary | concepts | questions
get_learning_progress(user_id)
```

Run the MCP server:

```bash
python -m backend.mcp.server

# For debugging with MCP Inspector:
mcp dev backend/mcp/server.py
```

---

## 📚 Personalized Learning Plans

The Study Planner generates roadmaps adapted to:

- **Subject** — Python, DSA, ML, Web Dev, etc.
- **Skill Level** — Beginner / Intermediate / Advanced
- **Daily Hours** — how much time you can commit
- **Duration** — weeks or months timeline

### Plan Types Available

- `daily` — hour-by-hour schedule
- `weekly` — topic breakdown per day
- `monthly` — milestone-based roadmap
- `interview_prep` — targeted revision sprints
- `mini_project` — guided hands-on challenges
- `revision` — spaced repetition style review

---

## 📝 Intelligent Quiz Generator

Generate assessments with full control:

| Option | Choices |
|---|---|
| **Type** | Multiple Choice, Short Answer, Coding Problems |
| **Difficulty** | Easy / Medium / Hard |
| **Count** | 1–20 questions |
| **Extras** | Answer explanations, hints |

---

## 📖 Notes Analyzer

Upload any study material and get:

- **Summary** — condensed core ideas
- **Key Concepts** — extracted terms and definitions
- **Revision Notes** — structured bullet-point notes
- **Practice Questions** — auto-generated from content
- **Topic Explanations** — plain-English breakdowns

---

## 📊 Progress Tracking System

| Metric | Description |
|---|---|
| ⚡ **XP Points** | Earned through quizzes and completions |
| 🎮 **Level System** | Leveled progression tied to XP milestones |
| 📉 **Weak Topics** | Auto-detected from quiz performance |
| 🏆 **Quiz History** | Full session log with scores |
| 🔁 **Recommendations** | Next-step suggestions based on progress |

---

## 🛡️ Security Architecture

StudyPilot AI follows secure development practices throughout:

```
┌─────────────────────────────────────────┐
│           Security Layers               │
├─────────────────────────────────────────┤
│ ✅ Input Validation      (all endpoints) │
│ ✅ Prompt Sanitization   (LLM safety)    │
│ ✅ Secure File Upload    (type checking) │
│ ✅ Upload Sandboxing     (isolated dir)  │
│ ✅ Path Traversal Guard  (no escapes)    │
│ ✅ Error Redaction       (no leaks)      │
│ ✅ Safe Execution        (no eval/exec)  │
│ ✅ Runtime Validation    (schema checks) │
└─────────────────────────────────────────┘
```

---

## 🏗️ Technology Stack

### Backend
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)

### AI & Agents
![Google ADK](https://img.shields.io/badge/Google_ADK_Concepts-4285F4?style=flat-square&logo=google&logoColor=white)
![MCP](https://img.shields.io/badge/MCP_Protocol-7C3AED?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini_API-Optional-F59E0B?style=flat-square&logo=google&logoColor=white)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3_(Glassmorphism)-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

### Storage
![JSON](https://img.shields.io/badge/JSON_Storage-000000?style=flat-square&logo=json&logoColor=white)

---

## 📂 Project Structure

```
StudyPilot-AI/
│
├── backend/
│   ├── agents/
│   │   ├── coordinator.py      ← Routes user intent
│   │   ├── study_planner.py    ← Generates learning plans
│   │   ├── quiz_generator.py   ← Creates assessments
│   │   ├── notes_analyzer.py   ← Processes uploaded material
│   │   └── progress_tracker.py ← Tracks XP and weak topics
│   │
│   ├── mcp/
│   │   └── server.py           ← MCP tool server
│   │
│   ├── utils/
│   │   └── security.py         ← Validation & sanitization
│   │
│   ├── app.py                  ← FastAPI entry point
│   └── requirements.txt
│
├── frontend/
│   ├── index.html              ← Glassmorphism dashboard
│   ├── style.css
│   └── app.js
│
├── data/
│   ├── db/                     ← JSON user data
│   └── uploads/                ← Sandboxed file storage
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/StudyPilot-AI.git
cd StudyPilot-AI
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. (Optional) Configure Gemini API

```bash
# Create a .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```
> Without a key, StudyPilot AI runs using its built-in offline fallback engine.

### 4. Run the Application

```bash
python -m backend.app
```

Open your browser at → **`http://127.0.0.1:8000`**

---

## 💻 Dashboard Modules

### 🤖 Chat Assistant
Communicates with the Coordinator Agent to intelligently route your request to the right specialist — no manual selection needed.

### 📅 Study Planner
Input your subject, level, and available time to generate a fully personalized learning roadmap.

### 📝 Quiz Generator
Select topic, difficulty, and question type to get an instant quiz with answer explanations.

### 📚 Notes Analyzer
Paste or upload your study notes to receive a summary, key concepts, and practice questions in seconds.

### 📈 Progress Dashboard
See your XP, current level, quiz history, weak topics, and next recommended steps — all in one view.

---

## 🔮 Future Improvements

- [ ] User Authentication & Profiles
- [ ] Cloud Database Integration
- [ ] Voice Assistant Interface
- [ ] Google Calendar Sync
- [ ] Mobile Application
- [ ] AI Flashcard Generator
- [ ] Spaced Repetition Engine
- [ ] Team Study Rooms / Collaboration
- [ ] Offline Mode (local LLM support)

---

## 👨‍💻 Author

<div align="center">

**Ali Muhammad**

*Software Engineering Student · AI Automation & Multi-Agent Systems Enthusiast*

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/YOUR_USERNAME)

</div>

---

<div align="center">

### ⭐ If this project helped you or impressed you — drop a star!

*It helps others discover the project and motivates future development.*

---

<sub>Built with 🤖 Google ADK concepts · 🔌 MCP · ⚡ FastAPI · Made by Ali Muhammad</sub>

</div>
