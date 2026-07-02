<p align="center">
  <img src="images/banner.png" width="100%">
</p>


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

![Google ADK](https://img.shields.io/badge/Google-ADK-blue?style=for-the-badge&logo=google)

![MCP](https://img.shields.io/badge/MCP-Enabled-success?style=for-the-badge)

# 🎓 StudyPilot AI – Intelligent Multi-Agent Learning Concierge

<p align="center">
  <b>An AI-powered multi-agent learning assistant built with Google ADK concepts, Model Context Protocol (MCP), FastAPI, and a modern dashboard.</b>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Google ADK" src="https://img.shields.io/badge/Google-ADK-blue?style=for-the-badge&logo=google">
  <img alt="MCP" src="https://img.shields.io/badge/MCP-Enabled-success?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</p>

---

# 📖 Overview

StudyPilot AI is a full-stack, multi-agent AI learning platform designed to help students plan, learn, practice, revise, and track their academic progress through intelligent agent collaboration.

The project demonstrates modern AI application architecture by combining **Google Agent Development Kit (ADK) concepts**, **Model Context Protocol (MCP)** integration, **FastAPI**, secure backend services, and a clean glassmorphism dashboard.

Instead of relying on a single AI assistant, StudyPilot AI coordinates multiple specialized agents that work together to deliver personalized educational assistance.

---
<img width="1920" height="911" alt="image" src="https://github.com/user-attachments/assets/41f74b28-2388-402b-b311-e3631b1c12b7" />

# ✨ Key Features

## 🤖 Multi-Agent AI System

StudyPilot AI consists of specialized AI agents coordinated by a central orchestration layer.

* 🎯 Coordinator Agent
* 📅 Study Planner Agent
* 📝 Quiz Generator Agent
* 📚 Notes Analyzer Agent
* 📈 Progress Tracker Agent

Each agent has a dedicated responsibility while the Coordinator intelligently routes user requests to the appropriate specialist.

---

## 🧠 Google ADK Inspired Architecture

The project follows Google's Agent Development Kit (ADK) concepts including:

* Agent abstraction
* Session state management
* Sequential workflows
* Agent coordination
* Modular architecture

The implementation mirrors Google's multi-agent design principles while remaining fully deployable locally.

---

## 🔌 Model Context Protocol (MCP)

StudyPilot AI includes a built-in MCP server that exposes agent capabilities as reusable tools.

Available tools include:

* Generate Study Plans
* Generate Quizzes
* Analyze Notes
* Retrieve Learning Progress

These tools can be accessed from MCP-compatible clients.

---

## 📚 Personalized Learning

Students can generate:

* Daily study schedules
* Weekly learning plans
* Monthly roadmaps
* Coding exercises
* Revision schedules
* Mini-projects
* Interview preparation plans

Plans adapt according to:

* Subject
* Skill Level
* Daily Study Hours
* Study Duration

---

## 📝 Intelligent Quiz Generator

Generate quizzes containing:

* Multiple Choice Questions
* Short Answer Questions
* Coding Problems
* Difficulty Levels
* Answer Explanations

Designed for continuous learning and self-assessment.

---

## 📖 Notes Assistant

Upload study material and automatically:

* Generate summaries
* Extract key concepts
* Create revision notes
* Produce practice questions
* Explain difficult topics

---

## 📊 Progress Tracking

Track your learning journey through:

* Experience Points (XP)
* Level System
* Quiz Performance
* Weak Topic Detection
* Personalized Recommendations

---

## 🔒 Security Features

StudyPilot AI follows secure development practices.

Features include:

* Input validation
* Safe execution
* Prompt sanitization
* Path traversal protection
* Secure file handling
* Upload sandboxing
* Error handling
* Runtime validation

---

# 🏗 Technology Stack

### Backend

* Python
* FastAPI
* Google ADK Concepts
* Model Context Protocol (MCP)

### Frontend

* HTML5
* CSS3
* JavaScript

### Database

* JSON Storage

### AI

* Multi-Agent Architecture
* Optional Gemini API Integration
* Offline Fallback Engine

---

# 📂 Project Structure

```text
StudyPilot-AI/

│── backend/
│   ├── agents/
│   ├── mcp/
│   ├── utils/
│   ├── app.py
│   └── requirements.txt
│
│── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
│── data/
│   ├── db/
│   └── uploads/
│
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/StudyPilot-AI.git

cd StudyPilot-AI
```

---

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## Run Application

```bash
python -m backend.app
```

Application runs at

```
http://127.0.0.1:8000
```

---

# 💻 Dashboard Modules

### 🤖 Chat Assistant

Communicates with the Coordinator Agent to intelligently route requests.

---

### 📅 Study Planner

Generates personalized learning roadmaps.

---

### 📝 Quiz Generator

Creates adaptive quizzes with explanations.

---

### 📚 Notes Analyzer

Processes uploaded study notes and produces summaries.

---

### 📈 Progress Dashboard

Displays:

* XP
* Levels
* Quiz History
* Weak Topics
* Recommendations

---

# 🔌 MCP Integration

Run the MCP server

```bash
python -m backend.mcp.server
```

For debugging:

```bash
mcp dev backend/mcp/server.py
```

---

# 🔄 Multi-Agent Workflow

```text
                 User
                   │
                   ▼
          Coordinator Agent
      ┌─────────┼─────────┐
      ▼         ▼         ▼
 Planner     Quiz      Notes
      │         │         │
      └──────┬──┴─────────┘
             ▼
      Progress Tracker
             │
             ▼
         Final Response
```

---

# 🛡 Security Architecture

StudyPilot AI incorporates multiple security mechanisms.

* Input Validation
* Prompt Sanitization
* Secure File Upload
* Safe Execution
* Error Redaction
* Upload Sandboxing
* Path Traversal Protection

These safeguards ensure reliable and secure execution.

---

# 🌟 Highlights

✅ Google ADK Inspired Multi-Agent System

✅ Model Context Protocol (MCP)

✅ FastAPI Backend

✅ Modular Agent Architecture

✅ Secure File Processing

✅ Intelligent Study Planning

✅ Adaptive Quiz Generation

✅ Progress Analytics

✅ Modern Glassmorphism Dashboard

---

# 📌 Future Improvements

* User Authentication
* Cloud Database Integration
* Voice Assistant
* Calendar Synchronization
* Mobile Application
* AI Flashcards
* Spaced Repetition Engine
* Team Study Rooms

---

# 👨‍💻 Author

**Ali Muhammad**

Software Engineering Student

AI Automation & Multi-Agent Systems Enthusiast

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps others discover the project and supports future development.
