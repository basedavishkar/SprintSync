# flake8: noqa: E501
from typing import Optional
from google import genai
from app.core.config import settings


class AIService:
    """Service for handling AI operations with Gemini."""

    def __init__(self):
        self.client = self._get_gemini_client()

    def _get_gemini_client(self) -> Optional[genai.Client]:
        """Initialize Gemini client if API key is available."""
        if not settings.gemini_api_key:
            return None

        try:
            return genai.Client(api_key=settings.gemini_api_key)
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            return None

    def generate_task_description(self, title: str) -> str:
        """Generate a task description using AI."""
        if not self.client:
            print("Warning: No Gemini client available, using fallback")
            return self._get_fallback_description(title)

        try:
            prompt = f"""Create a brief, concise task description for: "{title}"

Keep it under 100 words. Focus on:
- What needs to be done
- Key steps (2-3 points)
- Expected outcome

Make it practical and actionable. Use plain text only, no markdown formatting or asterisks."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return self._clean_response(response.text)
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._get_fallback_description(title)

    def generate_daily_plan(
        self, username: str, user_tasks: list = None
    ) -> str:
        """Generate a daily productivity plan using AI based on user's actual tasks."""
        if not self.client:
            print("Warning: No Gemini client available, using fallback")
            return self._get_fallback_plan(username)

        try:
            # Build task context from user's actual tasks, prioritizing by status
            task_context = ""
            if user_tasks and len(user_tasks) > 0:
                # Sort tasks by priority: in_progress first, then todo, then done
                priority_order = {"in_progress": 1, "todo": 2, "done": 3}
                sorted_tasks = sorted(
                    user_tasks,
                    key=lambda x: priority_order.get(x["status"], 4),
                )

                task_context = (
                    "Based on your current tasks (prioritized by status):\n"
                )
                for i, task in enumerate(
                    sorted_tasks[:5], 1
                ):  # Show top 5 prioritized tasks
                    status_emoji = (
                        "🔄"
                        if task["status"] == "in_progress"
                        else "📋"
                        if task["status"] == "todo"
                        else "✅"
                    )
                    task_context += f"{i}. {status_emoji} {task['title']} ({task['status']})\n"
                task_context += "\n"

            prompt = f"""Create a brief daily productivity plan for {username}.

{task_context}Focus on:
- Prioritize in-progress tasks first, then todo tasks
- 3 priority tasks for today with time estimates
- One success tip

Keep it under 150 words. Make it practical and motivating. Use plain text only, no markdown formatting or asterisks."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return self._clean_response(response.text)
        except Exception as e:
            print(f"AI plan generation failed: {e}")
            return self._get_fallback_plan(username)

    def _get_fallback_description(self, title: str) -> str:
        """Fallback task description when AI is unavailable."""
        title_lower = title.lower()

        if any(word in title_lower for word in ["eat", "food", "healthy"]):
            return """Plan nutritious meals with protein, vegetables, and whole grains.
Focus on balanced portions and hydration. Track progress weekly."""

        elif any(
            word in title_lower for word in ["workout", "exercise", "gym"]
        ):
            return """Design 30-minute workout routine: 5-min warmup, 20-min cardio/strength,
5-min cooldown. Include 2-3 rest days per week."""

        elif any(word in title_lower for word in ["study", "learn", "read"]):
            return """Create focused study sessions: 25-min blocks with 5-min breaks.
Set specific goals, use active learning, and review regularly."""

        else:
            return f"""Plan and execute: {title}

Steps:
1. Define clear objectives
2. Break into smaller tasks
3. Set timeline and milestones
4. Track progress and adjust"""

    def _clean_response(self, text: str) -> str:
        """Clean up AI response by removing excessive asterisks and formatting."""
        # Remove excessive asterisks (markdown bold formatting)
        text = text.replace("**", "")
        text = text.replace("***", "")
        text = text.replace("*", "")

        # Clean up extra whitespace
        text = " ".join(text.split())

        # Remove any remaining markdown artifacts
        text = text.replace("#", "")
        text = text.replace("##", "")
        text = text.replace("###", "")

        return text.strip()

    def _get_fallback_plan(self, username: str) -> str:
        """Fallback daily plan when AI is unavailable."""
        return f"""Daily Plan for {username}:

📋 Today's Focus:
• Complete 3 priority tasks
• 2-hour deep work session
• 30-min planning and review

⏰ Schedule:
• 9-11am: Deep work
• 11-12pm: Meetings/collaboration
• 2-4pm: Task execution
• 4-4:30pm: Review and planning

💡 Success Tip: Take 5-min breaks every hour to stay focused and energized."""


# Global AI service instance
ai_service = AIService()
