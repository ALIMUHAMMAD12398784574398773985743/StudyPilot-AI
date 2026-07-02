from typing import Dict, Any, List
from .google_adk import Agent, SessionState
from ..utils.db import get_user_profile, get_study_plans, get_quiz_scores, get_uploaded_notes

class ProgressAgent(Agent):
    """
    Progress Agent: Evaluates learner progress and recommends next steps.
    """
    def __init__(self):
        super().__init__(
            name="ProgressAgent",
            instruction="You analyze study records and quiz scores to recommend topics and study optimizations."
        )

    def analyze_progress(self) -> Dict[str, Any]:
        """
        Gathers metrics from the DB and generates recommendations, identifying weak topics (< 70%).
        """
        profile = get_user_profile()
        plans = get_study_plans()
        scores = get_quiz_scores()
        notes = get_uploaded_notes()
        
        # Calculations
        xp = profile.get("xp", 0)
        num_plans = len(plans)
        num_quizzes = len(scores)
        num_notes = len(notes)
        
        avg_score = 0
        topic_scores = {}
        if num_quizzes > 0:
            total_pct = 0
            for s in scores:
                topic = s.get("topic", "General").strip().title()
                correct = s.get("correct_answers", 0)
                total = s.get("total_questions", 1)
                pct = (correct / total) * 100
                total_pct += pct
                
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(pct)
                
            avg_score = total_pct / num_quizzes
            
        # Group and calculate average score per topic
        topic_averages = {}
        weak_topics = []
        for topic, pcts in topic_scores.items():
            avg = sum(pcts) / len(pcts)
            topic_averages[topic] = round(avg, 1)
            if avg < 70.0:
                weak_topics.append(topic)
                
        # Generate targeted recommendations for weak topics
        weak_topics_recommendations = []
        for wt in weak_topics:
            weak_topics_recommendations.append(
                f"Your average score for '{wt}' is currently {topic_averages[wt]}% (target: 70%+). "
                f"We suggest opening your '{wt}' study notes, searching for key terms using Notes Q&A, and generating a new practice quiz to boost your confidence."
            )
            
        # Level determination based on XP
        level_num = 1 + (xp // 500)
        
        # Next Topic recommendations mapping
        next_topics = []
        recent_subject = "General"
        if plans:
            recent_subject = plans[-1].get("topic", "General").lower()
            
        if "python" in recent_subject:
            next_topics = [
                "Object-Oriented Programming (OOP) in Python",
                "Working with external libraries (Pandas, NumPy)",
                "Building REST APIs with FastAPI"
            ]
        elif "web" in recent_subject or "html" in recent_subject or "css" in recent_subject:
            next_topics = [
                "Responsive CSS Layouts (Grid & Flexbox)",
                "Asynchronous JavaScript (Fetch, Promises)",
                "Introduction to Node.js Backend development"
            ]
        elif "data" in recent_subject or "machine" in recent_subject:
            next_topics = [
                "Data Preprocessing & Feature Engineering",
                "Supervised Regression & Classification Algorithms",
                "Model Evaluation and Validation techniques"
            ]
        else:
            next_topics = [
                "Active Recall study techniques",
                "Advanced Time Management (Time Blocking)",
                "Project-based learning applications"
            ]

        # Generate custom recommendation text based on performance
        recommendation_text = ""
        study_tips = []
        
        if num_quizzes == 0:
            recommendation_text = "Welcome to StudyPilot AI! Start your journey by creating a Study Plan or generating a practice quiz to set a baseline."
            study_tips = [
                "Create a Study Plan for a topic you want to learn this week.",
                "Upload a text/markdown file in the Notes section to get an immediate summary.",
                "Take a 5-question baseline quiz on your subject."
            ]
        elif avg_score < 60:
            recommendation_text = f"You are making progress (XP: {xp}), but your average quiz score is {avg_score:.1f}%. It is highly recommended to slow down and reinforce foundational concepts."
            study_tips = [
                "Re-read your uploaded notes and try the Q&A search to clarify terms.",
                "Reduce daily study hours in your planner to avoid information overload.",
                "Use the Feynman Technique: explain the concepts aloud in your own words."
            ]
        elif avg_score < 85:
            recommendation_text = f"Solid performance! Your average score is {avg_score:.1f}%. You are building a strong foundation. Keep refining your understanding."
            study_tips = [
                "Review the explanations for questions you missed on previous quizzes.",
                "Set a weekly study goal of at least 10 hours and track it on your planner.",
                "Combine study materials: create a plan that merges your notes and online practice."
            ]
        else:
            recommendation_text = f"Excellent mastery! Your average score is a stellar {avg_score:.1f}%. You are ready for advanced topics and challenges."
            study_tips = [
                "Move on to the next recommended topics below to continue growing.",
                "Try explaining the material to a classmate or writing a blog post summary.",
                "Implement a real-world coding project using the skills you have mastered."
            ]
            
        # Add dates if not present
        from datetime import datetime
        scores_history = []
        for s in scores:
            item = s.copy()
            if "date" not in item:
                item["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            scores_history.append(item)

        return {
            "xp": xp,
            "level": level_num,
            "num_plans": num_plans,
            "num_quizzes": num_quizzes,
            "num_notes": num_notes,
            "avg_score": round(avg_score, 1),
            "recommendation": recommendation_text,
            "study_tips": study_tips,
            "next_topics": next_topics,
            "history": scores_history,
            "weak_topics": weak_topics,
            "topic_averages": topic_averages,
            "weak_topics_recommendations": weak_topics_recommendations
        }

    def _execute_simulation(self, prompt: str, session_state: SessionState) -> str:
        analysis = self.analyze_progress()
        
        # Format response for general chat query
        summary = [
            f"### 📈 StudyPilot Progress Analysis",
            f"**Total XP**: {analysis['xp']} | **Current Level**: {analysis['level']}",
            f"**Activities**: {analysis['num_plans']} Study Plans | {analysis['num_quizzes']} Quizzes | {analysis['num_notes']} Notes",
            f"**Average Quiz Score**: {analysis['avg_score']}%",
        ]
        
        if analysis.get("weak_topics"):
            summary.append(f"\n⚠️ **Weak Topics Identified (Average < 70%):**")
            for wt in analysis["weak_topics"]:
                summary.append(f"- {wt}: {analysis['topic_averages'][wt]}%")
                
        summary.append(f"\n💡 **Assessment**: {analysis['recommendation']}")
        
        if analysis.get("weak_topics_recommendations"):
            summary.append(f"\n🎯 **Targeted Recommendations:**")
            for rec in analysis["weak_topics_recommendations"]:
                summary.append(f"- {rec}")
                
        summary.append(f"\n🎯 **Next Study Topics Recommended:**")
        for topic in analysis['next_topics']:
            summary.append(f"- {topic}")
            
        return "\n".join(summary)
