import os
import re
from typing import Dict, Any, List
from pydantic import BaseModel
from .google_adk import Agent, SessionState
from ..utils.security import sanitize_input_text

# Pydantic schemas for structured summaries via Gemini
class NotesSummarySchema(BaseModel):
    summary_markdown: str
    keywords: List[str]
    definitions: Dict[str, str]

class NotesAgent(Agent):
    """
    Notes Agent: Summarizes uploaded notes and answers questions about them.
    Integrates with Google Gemini API when available, and falls back to a 
    custom offline rule-based processor when offline.
    """
    def __init__(self):
        super().__init__(
            name="NotesAgent",
            instruction="You analyze uploaded study notes, extract key terms, generate summaries, and answer questions about the content."
        )

    def summarize_notes(self, content: str, title: str = "Notes Summary") -> Dict[str, Any]:
        """
        Generates a structured summary study guide. Utilizes Gemini if API key
        is active, and falls back to advanced rule-based offline processing.
        """
        clean_content = content.strip()
        if not clean_content:
            return {
                "title": title,
                "summary_markdown": "The note content is empty.",
                "keywords": [],
                "definitions": {},
                "full_content": ""
            }

        # Check for Gemini API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"Analyze the following study notes and generate a highly educational study guide.\n\n"
                    f"Document Title: {title}\n\n"
                    f"Content:\n{clean_content}\n\n"
                    f"Requirements:\n"
                    f"1. Generate a comprehensive summary markdown document (summary_markdown) with three sections: "
                    f"'### 🔍 Executive Summary', '### 📖 Key Concepts & Explanations', and '### ❓ Revision Questions & Answers'.\n"
                    f"2. Extract up to 6 key keywords (keywords) from the text.\n"
                    f"3. Build a dictionary of key terms and their definitions (definitions) found in the text.\n"
                    f"4. Respond ONLY with valid JSON matching the requested schema."
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=NotesSummarySchema,
                    ),
                )
                
                if response and response.text:
                    import json
                    data = json.loads(response.text)
                    summary_md = data.get("summary_markdown", "")
                    keywords = data.get("keywords", [])
                    definitions = data.get("definitions", {})
                    
                    if summary_md:
                        # Prepend title
                        summary_md = f"## 📝 Study Guide: {title}\n\n" + summary_md
                        return {
                            "title": title,
                            "summary_markdown": summary_md,
                            "keywords": keywords,
                            "definitions": definitions,
                            "full_content": content
                        }
            except Exception as e:
                print(f"Gemini API Notes Exception: {str(e)}. Falling back to offline generator.")

        # Offline Fallback Generator
        # 1. Extract Definitions (term is defined as/refers to/means...)
        definitions = {}
        patterns = [
            r"\b([A-Za-z][a-zA-Z\s]+)\b\s+is\s+defined\s+as\s+([^.\n]+)",
            r"\b([A-Za-z][a-zA-Z\s]+)\b\s+refers\s+to\s+([^.\n]+)",
            r"\b([A-Za-z][a-zA-Z\s]+)\b\s+means\s+([^.\n]+)",
            r"\b([A-Za-z][a-zA-Z\s]+)\b\s+is\s+a\s+([^.\n]+)"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, clean_content, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                meaning = match.group(2).strip()
                if len(term) > 3 and len(term) < 40 and len(meaning) > 10 and len(meaning) < 150:
                    definitions[term.title()] = meaning

        # 2. Extract Key Sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean_content)
        scored_sentences = []
        stop_words = {"the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on", "for", "with", "is", "are", "was", "were", "it", "that", "this", "these"}
        
        word_counts = {}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', clean_content.lower())
        for w in words:
            if w not in stop_words:
                word_counts[w] = word_counts.get(w, 0) + 1
                
        sorted_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [kw[0] for kw in sorted_keywords[:6]]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30 or len(sentence) > 200:
                continue
                
            score = 0
            for kw in top_keywords:
                if kw in sentence.lower():
                    score += 1
            if any(marker in sentence.lower() for marker in ["importantly", "however", "therefore", "in summary", "consequently"]):
                score += 2
            if " is " in sentence or " are " in sentence:
                score += 1
                
            scored_sentences.append((sentence, score))
            
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        key_bullet_points = [s[0] for s in scored_sentences[:5]]
        
        if not key_bullet_points:
            key_bullet_points = [s for s in sentences[:3] if s]

        # 3. Format overall summary document
        summary_md = []
        summary_md.append(f"## 📝 Study Guide: {title}")
        summary_md.append("\n### 🔍 Executive Summary")
        for bp in key_bullet_points:
            summary_md.append(f"- {bp}")
            
        summary_md.append("\n### 📖 Key Concepts & Explanations")
        if definitions:
            for term, val in list(definitions.items())[:6]:
                summary_md.append(f"- **{term}**: {val}")
        else:
            summary_md.append("- *No specific concepts or definitions were automatically detected. Review the main text below.*")
            
        summary_md.append("\n### ❓ Revision Questions & Answers")
        if definitions:
            for idx, (term, val) in enumerate(list(definitions.items())[:5]):
                summary_md.append(f"**Q{idx+1}: What is {term}?**")
                summary_md.append(f"**A**: {val}\n")
        else:
            # Generate generic questions based on top key sentences
            for idx, sentence in enumerate(key_bullet_points[:2]):
                summary_md.append(f"**Q{idx+1}: What is the significance of the following point?**")
                summary_md.append(f"*\"{sentence}\"*")
                summary_md.append(f"**A**: This represents a core theme in the study notes that requires attention.\n")
                
        summary_md.append("\n### 💡 Key Focus Keywords")
        summary_md.append(", ".join([f"`{kw}`" for kw in top_keywords]))
        
        return {
            "title": title,
            "summary_markdown": "\n".join(summary_md),
            "keywords": top_keywords,
            "definitions": definitions,
            "full_content": content
        }

    def answer_question(self, query: str, notes_content: str) -> str:
        """
        Answers a user question based on the note content. Utilizes Gemini 
        if API key is active, and falls back to word matching offline.
        """
        query_san = sanitize_input_text(query)
        if not notes_content or not notes_content.strip():
            return "No notes content is currently loaded to answer questions."

        # Check for Gemini API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"Answer the user's question based strictly on the provided study notes. "
                    f"If the answer cannot be found in the notes, state that clearly but use context clues if helpful. "
                    f"Keep the response professional, clear, and educational.\n\n"
                    f"Study Notes:\n{notes_content}\n\n"
                    f"User Question: {query_san}"
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini API Notes Q&A Exception: {str(e)}. Falling back to offline matcher.")

        # Offline Fallback Word Matching
        query_lower = query_san.lower()
        stop_words = {"what", "how", "why", "who", "where", "when", "is", "are", "the", "a", "an", "about", "explain", "describe", "define"}
        query_words = [w for w in re.findall(r'\b\w+\b', query_lower) if w not in stop_words]
        
        if not query_words:
            return "Please ask a specific question about the content of your notes."

        sentences = re.split(r'(?<=[.!?])\s+', notes_content)
        best_matches = []
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if not sentence_clean:
                continue
            
            match_score = 0
            for qw in query_words:
                if re.search(r'\b' + re.escape(qw) + r'\b', sentence_clean.lower()):
                    match_score += 2
                elif qw in sentence_clean.lower():
                    match_score += 1
            
            if match_score > 0:
                best_matches.append((sentence_clean, match_score))
                
        best_matches.sort(key=lambda x: x[1], reverse=True)
        
        if best_matches:
            answer_sentences = [m[0] for m in best_matches[:3]]
            return (
                "📍 **Based on your uploaded study notes:**\n\n" + 
                " ".join(answer_sentences) + 
                "\n\n*Feel free to ask more specific questions or request a practice quiz based on these notes!*"
            )
        else:
            return (
                "I couldn't find a direct match in your notes for that question.\n"
                "Try rephrasing your question or using keywords that appear exactly in your uploaded text."
            )

    def _execute_simulation(self, prompt: str, session_state: SessionState) -> str:
        notes = session_state.get("notes_text", "")
        title = session_state.get("notes_title", "Uploaded Document")
        
        if not notes:
            return "No study notes have been uploaded yet. Please upload a text file."
            
        if "summarize" in prompt.lower() or "summary" in prompt.lower():
            result = self.summarize_notes(notes, title)
            return result["summary_markdown"]
        else:
            return self.answer_question(prompt, notes)
