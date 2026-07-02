import os
from fastmcp import FastMCP
from ..agents.planner import StudyPlannerAgent
from ..agents.quiz import QuizAgent
from ..agents.notes import NotesAgent
from ..agents.progress import ProgressAgent
from ..utils.security import (
    validate_uploaded_file, 
    UPLOAD_DIR, 
    sanitize_input_text,
    validate_topic,
    sanitize_api_error,
    is_safe_path
)
from ..utils.db import add_study_plan, add_uploaded_note

# Initialize FastMCP Server named StudyPilot
mcp = FastMCP("StudyPilot")

# Instantiate agents
planner_agent = StudyPlannerAgent()
quiz_agent = QuizAgent()
notes_agent = NotesAgent()
progress_agent = ProgressAgent()

@mcp.tool()
def generate_study_schedule(topic: str, duration_weeks: int = 4, daily_hours: float = 2.0, skill_level: str = "Beginner") -> str:
    """
    Generates a personalized study schedule/plan.
    
    Args:
        topic: The subject or topic of study (e.g. Python, Calculus).
        duration_weeks: The length of the study plan in weeks (1 to 12).
        daily_hours: Number of hours to dedicate daily (0.5 to 8.0).
        skill_level: Current experience level (Beginner, Intermediate, Advanced).
    """
    try:
        # Validate inputs
        is_valid_topic, err_topic = validate_topic(topic)
        if not is_valid_topic:
            return f"Validation Error: {err_topic}"
            
        topic_san = sanitize_input_text(topic)
        level_san = sanitize_input_text(skill_level)
        
        if level_san not in ["Beginner", "Intermediate", "Advanced"]:
            return "Validation Error: Skill level must be one of 'Beginner', 'Intermediate', or 'Advanced'."
            
        if not (1 <= duration_weeks <= 12):
            return "Validation Error: Duration must be between 1 and 12 weeks."
            
        if not (0.5 <= daily_hours <= 8.0):
            return "Validation Error: Daily study hours must be between 0.5 and 8.0."
            
        plan_md = planner_agent.generate_plan(topic_san, duration_weeks, daily_hours, level_san)
        
        # Save plan to db
        add_study_plan({
            "topic": topic_san,
            "duration_weeks": duration_weeks,
            "daily_hours": daily_hours,
            "skill_level": level_san,
            "plan_markdown": plan_md
        })
        
        return plan_md
    except Exception as e:
        error_clean = sanitize_api_error(str(e))
        return f"Execution Error: An error occurred while generating study schedule: {error_clean}"

@mcp.tool()
def generate_quiz_questions(topic: str, num_questions: int = 5) -> str:
    """
    Generates a practice multiple-choice quiz on a topic.
    
    Args:
        topic: The topic of the quiz (e.g. Python, CSS, History).
        num_questions: Number of questions (1 to 10).
    """
    try:
        is_valid_topic, err_topic = validate_topic(topic)
        if not is_valid_topic:
            return f"Validation Error: {err_topic}"
            
        topic_san = sanitize_input_text(topic)
        
        if not (1 <= num_questions <= 10):
            return "Validation Error: Number of questions must be between 1 and 10."
            
        questions = quiz_agent.generate_quiz(topic_san, num_questions)
        
        # Format for readability
        output = [f"# Quiz: {topic_san.capitalize()}"]
        for idx, q in enumerate(questions):
            output.append(f"\nQ{idx+1}: {q['question']}")
            for o_idx, opt in enumerate(q['options']):
                output.append(f"  {chr(65+o_idx)}) {opt}")
            output.append(f"Answer: Option {chr(65 + q['correct'])}")
            output.append(f"Explanation: {q['explanation']}")
            
        return "\n".join(output)
    except Exception as e:
        error_clean = sanitize_api_error(str(e))
        return f"Execution Error: An error occurred while generating quiz: {error_clean}"

@mcp.tool()
def analyze_study_notes(filename: str, content: str) -> str:
    """
    Validates, uploads, and generates an executive summary of study notes.
    
    Args:
        filename: Name of the file (must end in .txt or .md).
        content: The text content of the notes.
    """
    try:
        filename_san = os.path.basename(filename)
        file_path = os.path.join(UPLOAD_DIR, filename_san)
        
        # Validate path traversal
        if not is_safe_path(file_path, UPLOAD_DIR):
            return "Security Error: Invalid path or filename (path traversal attempted)."
            
        content_bytes = content.encode("utf-8")
        
        is_valid, err_msg = validate_uploaded_file(filename_san, content_bytes)
        if not is_valid:
            return f"Security Error: {err_msg}"
            
        # Save file to uploads sandbox
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            return f"File Write Error: Could not save notes. Details: {str(e)}"
            
        # Summarize notes
        summary = notes_agent.summarize_notes(content, filename_san)
        
        # Save note metadata to database
        add_uploaded_note({
            "filename": filename_san,
            "keywords": summary["keywords"],
            "word_count": len(content.split()),
            "summary_markdown": summary["summary_markdown"]
        })
        
        return summary["summary_markdown"]
    except Exception as e:
        error_clean = sanitize_api_error(str(e))
        return f"Execution Error: An error occurred while analyzing notes: {error_clean}"

@mcp.tool()
def get_progress_report() -> str:
    """
    Returns the student progress report, current XP, level, and next topics.
    """
    try:
        analysis = progress_agent.analyze_progress()
        
        report = [
            f"# StudyPilot Progress Analysis",
            f"**XP**: {analysis['xp']} | **Current Level**: {analysis['level']}",
            f"**Study Plans Created**: {analysis['num_plans']}",
            f"**Quizzes Taken**: {analysis['num_quizzes']} | **Average Score**: {analysis['avg_score']}%",
            f"**Notes Uploaded**: {analysis['num_notes']}",
            f"\nAssessment: {analysis['recommendation']}",
            f"\nRecommended Next Topics:"
        ]
        for topic in analysis['next_topics']:
            report.append(f"- {topic}")
            
        return "\n".join(report)
    except Exception as e:
        error_clean = sanitize_api_error(str(e))
        return f"Execution Error: An error occurred while compiling progress report: {error_clean}"

if __name__ == "__main__":
    mcp.run()

