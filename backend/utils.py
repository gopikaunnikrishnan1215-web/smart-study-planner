from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from .models import Subject, Progress


def compute_hours_per_day(
    exam_date: date, current_date: date, total_hours_needed: float
) -> float:
    """
    Compute the recommended hours per day for a subject.

    If the exam is today or in the past, this returns the full remaining
    hours as a single-day recommendation.
    """
    days_remaining = (exam_date - current_date).days
    if days_remaining <= 0:
        return round(float(total_hours_needed), 2)
    hours_per_day = float(total_hours_needed) / float(days_remaining)
    return round(hours_per_day, 2)


def _load_topics(json_str: str) -> List[str]:
    try:
        raw = json.loads(json_str or "[]")
    except Exception:
        return []
    if isinstance(raw, list):
        return [str(t) for t in raw]
    return []


def _unique_topics_from_progress(records: Iterable[Progress]) -> Set[str]:
    completed: Set[str] = set()
    for rec in records:
        for topic in _load_topics(rec.topics_completed):
            completed.add(topic)
    return completed


def compute_subject_progress(
    subject: Subject, progress_records: Sequence[Progress]
) -> Dict[str, object]:
    """
    Aggregate progress information for a single subject.
    """
    total_hours_studied = float(sum(p.hours_studied for p in progress_records))
    all_topics = _load_topics(subject.topics)
    completed_topics = _unique_topics_from_progress(progress_records)
    remaining_topics = [t for t in all_topics if t not in completed_topics]

    percentage_complete = (
        (total_hours_studied / float(subject.total_hours_needed)) * 100.0
        if subject.total_hours_needed > 0
        else 0.0
    )

    return {
        "subject_id": subject.id,
        "total_hours_studied": round(total_hours_studied, 2),
        "progress_percent": round(percentage_complete, 2),
        "topics_completed": sorted(completed_topics),
        "topics_remaining": remaining_topics,
    }


def compute_overall_stats(
    subjects: Sequence[Subject], progress_by_subject: Dict[int, Dict[str, object]]
) -> Dict[str, object]:
    """
    Compute overall hours and topics statistics across all subjects.
    """
    total_hours_needed = float(sum(s.total_hours_needed for s in subjects))
    total_hours_studied = float(
        sum(float(info.get("total_hours_studied", 0.0)) for info in progress_by_subject.values())
    )
    hours_remaining = max(total_hours_needed - total_hours_studied, 0.0)

    total_topics = 0
    total_topics_completed = 0
    for subj in subjects:
        topics = _load_topics(subj.topics)
        total_topics += len(topics)
        info = progress_by_subject.get(subj.id)
        if info:
            total_topics_completed += len(info.get("topics_completed", []))

    total_topics_remaining = max(total_topics - total_topics_completed, 0)

    return {
        "total_hours_studied": round(total_hours_studied, 2),
        "total_hours_needed": round(total_hours_needed, 2),
        "hours_remaining": round(hours_remaining, 2),
        "total_topics": int(total_topics),
        "total_topics_completed": int(total_topics_completed),
        "total_topics_remaining": int(total_topics_remaining),
        "overall_progress_percent": round(
            (total_hours_studied / total_hours_needed * 100) if total_hours_needed > 0 else 0,
            1,
        ),
    }


def compute_priority_score(
    subject: Subject, current_date: date, progress_info: Dict[str, object]
) -> float:
    """
    Compute a priority score for a subject based on urgency and remaining work.
    Higher score = higher priority.
    """
    days_remaining = (subject.exam_date - current_date).days
    hours_remaining = max(
        subject.total_hours_needed - float(progress_info.get("total_hours_studied", 0.0)), 0.0
    )

    if days_remaining <= 0:
        return 1000.0  # Past due = highest priority

    if days_remaining <= 3:
        urgency_multiplier = 5.0
    elif days_remaining <= 7:
        urgency_multiplier = 3.0
    elif days_remaining <= 14:
        urgency_multiplier = 2.0
    else:
        urgency_multiplier = 1.0

    # Priority = (hours remaining / days remaining) * urgency_multiplier
    if days_remaining > 0:
        score = (hours_remaining / float(days_remaining)) * urgency_multiplier
    else:
        score = hours_remaining * urgency_multiplier

    return round(score, 2)


def get_motivational_message(progress_percent: float) -> str:
    """
    Generate a motivational message based on study progress percentage.
    """
    if progress_percent <= 40:
        messages = [
            "Every small step counts! Keep pushing forward and you'll make great progress.",
            "You're just getting started. Consistency will help you reach your goals.",
            "Remember, slow progress is still progress. Keep going!",
            "Don't worry about how much is left. Focus on what you can do today.",
            "You've got this! Break it into smaller parts and tackle them one by one.",
        ]
    else:
        messages = [
            "Great work! You're doing really well. Keep up the momentum!",
            "You're more than halfway there! Your hard work is paying off.",
            "Impressive progress! Stay consistent and you'll reach your goal soon.",
            "You're crushing it! Keep this pace and you'll finish strong.",
            "Well done! Your dedication is showing. Keep it up!",
        ]
    
    # Return a deterministic message based on progress
    import hashlib
    hash_val = int(hashlib.md5(str(progress_percent).encode()).hexdigest(), 16)
    idx = hash_val % len(messages)
    return messages[idx]


def get_chatbot_response(message: str, user_id: int) -> str:
    """
    Generate a chatbot response based on user message.
    Provides helpful, beginner-friendly, structured advice for study planning and doubt clearance.
    """
    message_lower = message.lower().strip()

    # Default questions - Concept Explanation
    if "explain this concept in simple words" in message_lower or "explain the concept" in message_lower:
        return """📚 Breaking Down Concepts:

Step 1: Start with the basics
• Understand what the concept is about
• Identify the main idea

Step 2: Break it into smaller parts
• Divide the concept into simple components
• Focus on one part at a time

Step 3: Use simple language
• Avoid technical jargon
• Use everyday examples you know

Example process:
1. Read the concept carefully
2. Write it in your own simple words
3. Create a mental picture or diagram
4. Explain it to someone else

Pro Tip: The best way to understand is to explain it to a friend without looking at notes!"""

    # Default questions - Examples
    if "give a clear example for better understanding" in message_lower or "example for understanding" in message_lower:
        return """💡 Learning Through Examples:

Step 1: Find relatable examples
• Connect to things you know
• Use real-world situations

Step 2: Work through the example
• Follow the steps carefully
• Understand each part

Step 3: Create your own example
• Apply the concept yourself
• Test your understanding

Why examples work:
• They make abstract ideas concrete
• Your brain remembers stories better than facts
• You can test if you really understand

Learning Sequence:
1. Learn the concept
2. Study worked examples
3. Practice similar problems
4. Create your own examples

Remember: Understanding through examples is much stronger than memorizing definitions!"""

    # Default questions - Exam Points
    if "key exam-oriented points" in message_lower or "exam-important points" in message_lower or "points to remember" in message_lower:
        return """📝 Key Exam-Oriented Points:

For any concept, remember these important aspects:

1. Definition & Core Concept
• What is it exactly?
• Why is it important?

2. Important Formulas/Rules
• Learn the exact formula/rule
• Know when to apply it

3. Common Examples
• Most frequently appearing examples
• Things that appear in past papers

4. Common Mistakes
• What mistakes do students make?
• How to avoid them

5. Application Areas
• Where is this concept used?
• Real-world applications

Study Strategy:
✓ Focus on these points in your revision
✓ Practice previous year questions
✓ Create a summary card for each concept
✓ Review 24 hours after learning

Exam Tips:
• Read questions carefully
• Start with concepts you're confident about
• Manage your time wisely
• Review your answers before submitting"""

    # Greeting responses
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "👋 Hello! I'm your Study Helper. I can explain concepts simply, provide clear examples, and highlight exam-important points. What would you like help with?"

    # Doubt clearance - general
    if any(word in message_lower for word in ["doubt", "confused", "understand", "how", "what is"]):
        return """🤔 Helping You Understand:

I'm here to help in three ways:

1. 📚 Concept Explanation
• Breaking down complex ideas into simple parts
• Using easy language without jargon
• Step-by-step understanding

2. 💡 Clear Examples
• Real-world examples you can relate to
• Worked solutions you can follow
• Practice problems to try

3. 📝 Exam-Important Points
• Key facts that appear in exams
• Common question types
• Revision tips

How to ask clearly:
• Mention the specific topic or concept
• Share what you've already understood
• Ask what confuses you

I'll explain it step-by-step in simple words!"""

    # Time management
    if any(word in message_lower for word in ["time", "manage", "hours", "schedule", "daily", "plan"]):
        return """⏰ Smart Time Management:

Step 1: Assess your total time
• Calculate days until exam
• Count available study hours
• Be realistic about your schedule

Step 2: Distribute subjects wisely
• Difficult subjects: more time
• Easy subjects: regular practice
• Balance your load

Step 3: Daily routine
• 45-60 minute study blocks
• 10-15 minute breaks between
• Mix different subjects

Sample Daily Schedule:
Morning (2-3 hours): New concepts
Afternoon (1-2 hours): Practice problems
Evening (1-2 hours): Revision

Pro Tips:
✓ Study when your mind is fresh
✓ Don't study late night before exam
✓ Review what you learned daily
✓ Adjust schedule based on progress"""

    # Motivation
    if any(word in message_lower for word in ["motivation", "tired", "stressed", "overwhelmed", "difficult", "hard"]):
        return """💪 Staying Motivated:

Remember why you're studying:
• Your future goals matter
• This effort will pay off
• You're building skills that last

When feeling overwhelmed:
1. Take a break (not the whole day!)
2. Do something you enjoy
3. Remember your past successes
4. Break tasks into smaller chunks

Daily motivation boosts:
✓ Celebrate small wins
✓ Track your progress
✓ Study with friends
✓ Remember: progress beats perfection

Quick energy boost:
• 5-minute walk
• Drink water
• Stretch
• Change location

You're doing great! 🎯 Keep going!"""

    # Revision strategies
    if any(word in message_lower for word in ["revision", "review", "revise", "remember", "memorize"]):
        return """🔄 Effective Revision Strategy:

The 24-Hour Rule:
• Review within 24 hours of learning
• Your brain forgets quickly otherwise
• Reviewing anchors the concept

Active Revision (Best Method):
1. Close your notes
2. Write/explain from memory
3. Check what you missed
4. Review those parts again

Revision Techniques:
• Active Recall: Test yourself without notes
• Flashcards: For definitions and formulas
• Mind Maps: Show connections
• Teaching: Explain to others
• Practice Problems: Apply concepts

Weekly Schedule:
Mon-Fri: New concepts
Sat: Deep revision of week's topics
Sun: Weak topics + practice

Exam Week:
✓ Short revision sessions (30 min)
✓ Focus on weak areas
✓ Practice past papers
✓ Get enough sleep

Track your progress to stay motivated!"""

    # Subject-specific help
    if any(word in message_lower for word in ["math", "formula", "calculate", "algebra", "geometry"]):
        return """🔢 Mathematics Learning:

Understanding Math:
1. Learn the concept (not just formula)
2. See why the formula works
3. Practice step-by-step
4. Solve similar problems

Steps to solve problems:
• Read carefully
• Identify what you know and need to find
• Choose the right concept/formula
• Work through steps clearly
• Check your answer

Common difficulties:
• Don't memorize formulas, understand them
• Do many practice problems
• Make shortcuts only after understanding

Formula learning tips:
✓ Derive it step-by-step
✓ Understand each part
✓ Memorize the 'why'

Practice Strategy:
Level 1: Textbook problems
Level 2: Mixed problems
Level 3: Previous year papers
Level 4: Challenge problems"""

    # Science
    if any(word in message_lower for word in ["science", "lab", "experiment", "theory", "law", "reaction"]):
        return """🔬 Science Learning:

Understanding Concepts:
1. Learn the theory first
2. Understand the working
3. Practice with examples
4. Connect to real world

For Physics/Chemistry:
• Understand the concept
• Draw diagrams if possible
• Use numerical examples
• Solve practice problems

For Biology:
• Visualize biological processes
• Draw and label diagrams
• Learn cause and effects
• Connect to human body/life

Study Tips:
✓ Watch animations/videos
✓ Draw your own diagrams
✓ Explain mechanism step-step
✓ Do virtual labs if possible

Exam Strategy:
• Label diagrams correctly
• Explain processes clearly
• Use scientific terms properly
• Show your understanding"""

    # History/Geography
    if any(word in message_lower for word in ["history", "geography", "event", "location", "timeline", "map"]):
        return """📖 History & Geography Learning:

History Study Method:
1. Understand the context (time period)
2. Learn causes → event → effects
3. Remember key dates
4. Create timelines

Geography Study Method:
1. Locate on the map
2. Understand physical features
3. Learn about resources/climate
4. Connect to human impact

Memory Techniques:
• Timeline for events
• Mind maps for causes
• Maps for locations
• Stories for connecting events

Study Approach:
✓ Read multiple sources
✓ Create your own notes
✓ Make timelines and maps
✓ Discuss with peers

Exam Tips:
• Explain why not just what
• Show connections
• Use examples from history
• Reference dates when asked"""

    # Language/Writing
    if any(word in message_lower for word in ["language", "essay", "grammar", "writing", "sentence", "literature"]):
        return """📚 Language & Writing:

Grammar Learning:
1. Understand the rule
2. See examples
3. Practice sentences
4. Write your own

Essay Writing:
Step 1: Plan (5 min)
• Main idea
• Key points
• Examples

Step 2: Write (20 min)
• Introduction
• Body (points with examples)
• Conclusion

Step 3: Review (5 min)
• Check grammar
• Improve flow
• Add details

For Literature:
• Understand the story/poem
• Identify themes
• Analyze characters
• Support with quotes

Writing Tips:
✓ Simple, clear sentences
✓ Good flow and structure
✓ Use examples
✓ Review before submitting

Practice Method:
1. Read good examples
2. Understand structure
3. Practice writing
4. Get feedback and improve"""

    # General study advice
    return """📝 Smart Study Tips:

Before You Start:
1. Clear your study space
2. Close all distractions
3. Have water nearby
4. Set realistic goal

During Study:
• Focus for 45-60 minutes
• Take 10-15 minute breaks
• Use active learning (don't just read)
• Make your own notes

Study Techniques:
✓ Active Recall: Test yourself
✓ Spaced Repetition: Review regularly
✓ Practice Problems: Apply concepts
✓ Teaching: Explain to others
✓ Visual Learning: Use diagrams

What to avoid:
✗ Passive reading
✗ Highlighting everything
✗ Memorizing without understanding
✗ Studying tired or stressed

Track Progress:
• Set weekly goals
• Keep a progress log
• Celebrate achievements
• Adjust as needed

Remember: Quality beats quantity! 🎯

What topic would you like help with?"""

