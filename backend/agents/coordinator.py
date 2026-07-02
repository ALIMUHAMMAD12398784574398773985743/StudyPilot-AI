import re
import os
import json
from .google_adk import Agent, SessionState
from .planner import StudyPlannerAgent
from .quiz import QuizAgent
from .notes import NotesAgent
from .progress import ProgressAgent

class CoordinatorAgent(Agent):
    """
    Coordinator Agent: Serves as the central manager of StudyPilot AI.
    It routes tasks, coordinates workflows, and provides answers to student questions.
    """
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            instruction="You are the StudyPilot AI Coordinator. You manage workflows and direct queries to specialist agents."
        )
        # Instantiate specialist agents
        self.planner = StudyPlannerAgent()
        self.quiz = QuizAgent()
        self.notes = NotesAgent()
        self.progress = ProgressAgent()

    def process_query(self, user_query: str, session_state: SessionState = None) -> str:
        """
        Orchestrates and routes the query.
        """
        if not session_state:
            session_state = SessionState()

        # Log query in history
        history = session_state.get("history", [])
        history.append(f"User Query: '{user_query}'")
        session_state.set("history", history)

        api_key = os.environ.get("GEMINI_API_KEY")
        routes = []

        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                # Fetch student level from profile if possible for context
                student_level = self._get_student_level()

                prompt = (
                    "You are the routing and parameter extraction engine for StudyPilot AI, a multi-agent system.\n"
                    "Your job is to analyze the user's query and decide which of the specialized agents need to be called and with what parameters.\n\n"
                    "Available Agents:\n"
                    "1. StudyPlannerAgent: Generates structured, day-by-day study schedules/plans.\n"
                    "   Parameters to extract and set in SessionState:\n"
                    "     - planner_topic (string): The subject/topic (e.g. 'Python', 'Java', 'Machine Learning').\n"
                    "     - planner_weeks (int): Duration in weeks (default 4, range 1-12).\n"
                    "     - planner_hours (float): Daily study hours (default 2.0, range 0.5-8.0).\n"
                    f"     - planner_level (string): 'Beginner', 'Intermediate', or 'Advanced' (default '{student_level}').\n"
                    "2. QuizAgent: Generates practice quizzes/exams.\n"
                    "   Parameters to extract and set in SessionState:\n"
                    "     - quiz_topic (string): Subject/topic of the quiz.\n"
                    "     - quiz_count (int): Number of questions (default 3, range 1-10).\n"
                    "3. NotesAgent: Summarizes uploaded notes or answers questions about them.\n"
                    "   Note: This agent should only be invoked if the user is asking about summaries, documents, notes, files, or questions about study content AND notes_text is present. If notes_text is NOT present, do not route here unless the user is explicitly referring to notes.\n"
                    "4. ProgressAgent: Analyzes student stats, performance, XP, quiz scores, and recommends study topics.\n"
                    "   Invoked when user asks about: progress, score, stats, level, performance, XP, recommendations, study tips.\n\n"
                    f"User Query: '{user_query}'\n\n"
                    "Instructions:\n"
                    "1. A query can contain multiple tasks (e.g. 'Give me a plan for Python and a quiz on Java'). In such cases, identify ALL relevant agents.\n"
                    "2. For each relevant agent, extract its specific parameters from the query. If a parameter is not explicitly mentioned, use the standard defaults.\n"
                    "3. For each agent, formulate a specific 'sub_query' representing the part of the user's request directed to that agent.\n"
                    "4. If no specialized agent is relevant, do not route to any agent.\n\n"
                    "Output a raw JSON array of route objects (no markdown wrappers like ```json or formatting, just the raw array). Each object must have the following keys:\n"
                    "  - 'agent': The exact name of the agent class ('StudyPlannerAgent', 'QuizAgent', 'NotesAgent', 'ProgressAgent')\n"
                    "  - 'sub_query': The sub-query/clause directed at this agent.\n"
                    "  - 'parameters': A dictionary of parameters to set in SessionState (e.g. {'planner_topic': 'Python', 'planner_weeks': 6} or {'quiz_topic': 'Java', 'quiz_count': 5})\n\n"
                    "Example output: [{\"agent\": \"StudyPlannerAgent\", \"sub_query\": \"Create a plan for Python\", \"parameters\": {\"planner_topic\": \"Python\", \"planner_weeks\": 4}}, {\"agent\": \"QuizAgent\", \"sub_query\": \"give me a quiz on Java\", \"parameters\": {\"quiz_topic\": \"Java\", \"quiz_count\": 3}}]"
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response and response.text:
                    clean_text = response.text.strip()
                    if clean_text.startswith("```"):
                        lines = clean_text.splitlines()
                        if lines[0].startswith("```json") or lines[0].startswith("```"):
                            lines = lines[1:-1]
                        clean_text = "\n".join(lines).strip()
                    routes = json.loads(clean_text)
            except Exception as e:
                print(f"Gemini Routing Exception: {e}. Falling back to rule-based routing.")
                routes = []

        # Offline/Rule-based routing fallback
        if not routes:
            routes = self._route_offline(user_query, session_state)

        # If no routes were determined, return friendly concierge fallback response
        if not routes:
            return self._get_fallback_response()

        # Execute matched agents
        agent_responses = {}
        for route in routes:
            agent_name = route["agent"]
            sub_query = route["sub_query"]
            params = route.get("parameters", {})

            # Populate state parameters
            for k, v in params.items():
                session_state.set(k, v)

            target_agent = None
            if agent_name == "StudyPlannerAgent":
                target_agent = self.planner
            elif agent_name == "QuizAgent":
                target_agent = self.quiz
            elif agent_name == "NotesAgent":
                target_agent = self.notes
            elif agent_name == "ProgressAgent":
                target_agent = self.progress

            if target_agent:
                try:
                    resp = target_agent.run(sub_query, session_state)
                    agent_responses[agent_name] = resp
                except Exception as e:
                    agent_responses[agent_name] = f"Error running {agent_name}: {str(e)}"

        # Combine responses
        if len(agent_responses) == 1:
            agent_name, resp = list(agent_responses.items())[0]
            if agent_name == "StudyPlannerAgent":
                return (
                    f"🗺️ **Study Planner Route Activated**\n\n"
                    f"I've delegated this request to the **Study Planner Agent**.\n\n"
                    f"{resp}\n\n"
                    f"*Note: You can also use the **Study Planner tab** in the dashboard to generate and save interactive plans!*"
                )
            elif agent_name == "QuizAgent":
                return (
                    f"📝 **Quiz Agent Route Activated**\n\n"
                    f"I've delegated this request to the **Quiz Agent**. Here is a mini-quiz for you:\n\n"
                    f"{resp}\n\n"
                    f"*Use the **Quiz Generator tab** in the dashboard to take fully interactive graded quizzes!*"
                )
            elif agent_name == "NotesAgent":
                return f"📂 **Notes Agent Route Activated**\n\n{resp}"
            elif agent_name == "ProgressAgent":
                return f"📈 **Progress Agent Route Activated**\n\n{resp}"
            else:
                return resp

        # Multiple responses: synthesize
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                synthesis_prompt = (
                    "You are the StudyPilot AI Coordinator. You have coordinated multiple specialized agents to answer the user's request.\n"
                    f"User Request: '{user_query}'\n\n"
                    "Here are the responses from the individual agents:\n"
                )
                for agent_name, agent_resp in agent_responses.items():
                    synthesis_prompt += f"--- {agent_name} Response ---\n{agent_resp}\n\n"
                
                synthesis_prompt += (
                    "Synthesize these responses into a single, cohesive, professional, and friendly response. "
                    "Integrate them naturally using clear, beautiful markdown formatting. "
                    "Make sure to keep the detailed content from each agent intact, but present them as a unified answer from StudyPilot AI."
                )

                synthesis_resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=synthesis_prompt
                )
                if synthesis_resp and synthesis_resp.text:
                    return synthesis_resp.text
            except Exception as e:
                print(f"Gemini Synthesis Exception: {e}. Falling back to standard joining.")

        # Offline/Standard joining fallback for multiple responses
        combined = []
        combined.append("🤝 **Multi-Agent Collaboration Response**\n")
        combined.append("I have coordinated with the specialized agents to fulfill your request:\n")
        
        for agent_name, response in agent_responses.items():
            if agent_name == "StudyPlannerAgent":
                combined.append("### 📅 Study Planner Agent\n" + response)
            elif agent_name == "QuizAgent":
                combined.append("### 📝 Quiz Agent\n" + response)
            elif agent_name == "NotesAgent":
                combined.append("### 📂 Notes Agent\n" + response)
            elif agent_name == "ProgressAgent":
                combined.append("### 📈 Progress Agent\n" + response)
            combined.append("\n" + "-" * 40 + "\n")
            
        return "\n".join(combined).strip()

    def _route_offline(self, user_query: str, session_state: SessionState) -> list:
        """
        Processes query offline using clause-splitting and keyword/regex matching.
        """
        query_clean = user_query.strip().lower()
        
        # Split query by coordinate conjunctions/delimiters
        clauses = re.split(r'\band\b|\bthen\b|\balso\b|;', user_query, flags=re.IGNORECASE)
        clauses = [c.strip() for c in clauses if c.strip()]
        if not clauses:
            clauses = [user_query.strip()]

        routes = []
        planner_keywords = ["plan", "schedule", "calendar", "timeline"]
        quiz_keywords = ["quiz", "test", "question", "exam", "practice"]
        notes_keywords = ["note", "summary", "summarize", "document", "file", "explain"]
        progress_keywords = ["progress", "score", "stats", "performance", "recommend", "level", "xp"]

        student_level = self._get_student_level()

        # Check each clause for agent activations
        for clause in clauses:
            clause_clean = clause.lower()
            
            # Study Planner
            if any(w in clause_clean for w in planner_keywords):
                params = self._extract_planner_params(clause, user_query, student_level)
                routes.append({
                    "agent": "StudyPlannerAgent",
                    "sub_query": clause,
                    "parameters": params
                })
            
            # Quiz
            if any(w in clause_clean for w in quiz_keywords):
                params = self._extract_quiz_params(clause, user_query)
                routes.append({
                    "agent": "QuizAgent",
                    "sub_query": clause,
                    "parameters": params
                })

            # Notes
            if any(w in clause_clean for w in notes_keywords):
                routes.append({
                    "agent": "NotesAgent",
                    "sub_query": clause,
                    "parameters": {}
                })

            # Progress
            if any(w in clause_clean for w in progress_keywords):
                routes.append({
                    "agent": "ProgressAgent",
                    "sub_query": clause,
                    "parameters": {}
                })

        # Resolve topic sharing
        planner_route = next((r for r in routes if r["agent"] == "StudyPlannerAgent"), None)
        quiz_route = next((r for r in routes if r["agent"] == "QuizAgent"), None)
        
        if planner_route and quiz_route:
            p_topic = planner_route["parameters"].get("planner_topic")
            q_topic = quiz_route["parameters"].get("quiz_topic")
            if p_topic and p_topic != "General Subject" and (not q_topic or q_topic == "General Studies"):
                quiz_route["parameters"]["quiz_topic"] = p_topic
                if "quiz" in quiz_route["sub_query"].lower() and "on" not in quiz_route["sub_query"].lower():
                    quiz_route["sub_query"] += f" on {p_topic}"
            elif q_topic and q_topic != "General Studies" and (not p_topic or p_topic == "General Subject"):
                planner_route["parameters"]["planner_topic"] = q_topic

        # Deduplicate multiple routes targeting the same agent
        unique_routes = []
        seen_agents = set()
        for r in routes:
            if r["agent"] not in seen_agents:
                seen_agents.add(r["agent"])
                unique_routes.append(r)

        return unique_routes

    def _extract_topic(self, clause: str, query: str, default_topic: str) -> str:
        clause_lower = clause.lower()
        query_lower = query.lower()
        
        known_topics = {
            "python": "Python",
            "javascript": "JavaScript",
            "java": "Java",
            "web development": "Web Development",
            "data structures": "Data Structures & Algorithms",
            "data structure": "Data Structures & Algorithms",
            "algorithms": "Data Structures & Algorithms",
            "algorithm": "Data Structures & Algorithms",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "data science": "Data Science",
            "html": "HTML",
            "css": "CSS"
        }
        
        for k, v in known_topics.items():
            if k in clause_lower:
                return v
        for k, v in known_topics.items():
            if k in query_lower:
                return v

        topic_match = re.search(r"\b(for|on|about)\s+([a-zA-Z0-9\s#\+\-\.]+)", clause, re.IGNORECASE)
        if not topic_match:
            topic_match = re.search(r"\b(for|on|about)\s+([a-zA-Z0-9\s#\+\-\.]+)", query, re.IGNORECASE)
        if not topic_match:
            topic_match = re.search(r"\b(plan|subject|quiz|test|study)\s+([a-zA-Z0-9\s#\+\-\.]+)", clause, re.IGNORECASE)
        if not topic_match:
            topic_match = re.search(r"\b(plan|subject|quiz|test|study)\s+([a-zA-Z0-9\s#\+\-\.]+)", query, re.IGNORECASE)
            
        if not topic_match:
            return default_topic
            
        topic = topic_match.group(2).strip()
        topic = re.sub(r'\b(for|on|about|\d+|week|hour|hr|beginner|intermediate|advanced)\b.*$', '', topic, flags=re.IGNORECASE).strip()
        topic = re.sub(r'[.,;:!?\-]+$', '', topic).strip()
        
        return topic if topic else default_topic

    def _extract_planner_params(self, clause: str, query: str, progress_level: str) -> dict:
        topic = self._extract_topic(clause, query, "General Subject")
                
        weeks_match = re.search(r"(\d+)\s*week", clause + " " + query, re.IGNORECASE)
        weeks = int(weeks_match.group(1)) if weeks_match else 4
        if not (1 <= weeks <= 12):
            weeks = 4
            
        hours_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hour|hr)", clause + " " + query, re.IGNORECASE)
        hours = float(hours_match.group(1)) if hours_match else 2.0
        if not (0.5 <= hours <= 8.0):
            hours = 2.0
            
        level = progress_level
        if re.search(r"\bbeginner\b", clause + " " + query, re.IGNORECASE):
            level = "Beginner"
        elif re.search(r"\bintermediate\b", clause + " " + query, re.IGNORECASE):
            level = "Intermediate"
        elif re.search(r"\badvanced\b", clause + " " + query, re.IGNORECASE):
            level = "Advanced"
            
        return {
            "planner_topic": topic,
            "planner_weeks": weeks,
            "planner_hours": hours,
            "planner_level": level
        }

    def _extract_quiz_params(self, clause: str, query: str) -> dict:
        topic = self._extract_topic(clause, query, "General Studies")
                
        count_match = re.search(r"(\d+)\s*(?:question|quiz|test|q\b)", clause + " " + query, re.IGNORECASE)
        count = int(count_match.group(1)) if count_match else 3
        if not (1 <= count <= 10):
            count = 3
            
        return {
            "quiz_topic": topic,
            "quiz_count": count
        }

    def _get_student_level(self) -> str:
        try:
            from ..utils.db import get_user_profile
            profile = get_user_profile()
            student_level = profile.get("level", "Beginner")
            if isinstance(student_level, str):
                return student_level
            return "Beginner"
        except Exception:
            return "Beginner"

    def _get_fallback_response(self) -> str:
        return (
            "👋 **Welcome to StudyPilot AI!**\n\n"
            "I am your central Coordinator Agent. I collaborate with four specialized agents to help you learn offline:\n\n"
            "1. 📅 **Study Planner Agent**: Generates structured timelines. Try typing: *'Create a plan for Python'*.\n"
            "2. 📝 **Quiz Agent**: Provides practice quizzes. Try typing: *'Give me a quiz on Web Development'*.\n"
            "3. 📂 **Notes Agent**: Summarizes text files and answers questions. (Upload your `.txt` files in the upload section).\n"
            "4. 📈 **Progress Agent**: Tracks your performance and XP. Try typing: *'Show my progress'*.\n\n"
            "How can I assist you in your study session today?"
        )

    def _execute_simulation(self, prompt: str, session_state: SessionState) -> str:
        return self.process_query(prompt, session_state)

