# flake8: noqa: E501
from app.core.database import SessionLocal
from app.models.user import User
from app.models.task import Task
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random


def seed_database():
    """Seed the database with AI development demo data."""
    db = SessionLocal()

    try:
        # Always ensure admin user exists
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            print(
                "👑 Admin user created: username='admin', password='admin123'"
            )
        else:
            print("Admin user already exists.")

        # Check if demo users already exist
        demo_users_exist = (
            db.query(User)
            .filter(User.username.in_(["user1", "user2", "user3"]))
            .count()
            >= 3
        )

        if demo_users_exist:
            print("Demo users already exist, skipping demo user creation...")
        else:
            print("Creating demo users...")
            # Create demo users
            users = []
            for i in range(1, 4):
                username = f"user{i}"
                hashed_password = get_password_hash("password123")
                user = User(
                    username=username,
                    hashed_password=hashed_password,
                    is_admin=False,
                )
                db.add(user)
                users.append(user)

            db.commit()
            print(f"✅ Created {len(users)} demo users")

        # Check if tasks already exist
        existing_tasks = db.query(Task).count()
        if existing_tasks > 0:
            print("Tasks already exist, skipping task creation...")
            return

        print("Creating demo tasks...")

        # AI Development Task Templates
        ai_tasks = [
            {
                "title": "Implement RAG system with vector database",
                "description": (
                    "Build a Retrieval-Augmented Generation system using Pinecone or "
                    "Weaviate for document search and question answering"
                ),
                "status": "todo",
            },
            {
                "title": "Fine-tune LLM for domain-specific tasks",
                "description": (
                    "Fine-tune a base model (like Llama or GPT) on custom dataset "
                    "for improved performance on specific use cases"
                ),
                "status": "in_progress",
            },
            {
                "title": "Build AI-powered code review system",
                "description": (
                    "Create an automated code review tool that uses LLMs to analyze "
                    "code quality, security, and best practices"
                ),
                "status": "todo",
            },
            {
                "title": "Implement prompt engineering framework",
                "description": (
                    "Develop a systematic approach to prompt design with A/B testing, "
                    "versioning, and performance metrics"
                ),
                "status": "done",
            },
            {
                "title": "Create AI model monitoring dashboard",
                "description": (
                    "Build real-time monitoring system for model performance, "
                    "drift detection, and alerting"
                ),
                "status": "in_progress",
            },
            {
                "title": "Design MLOps pipeline for model deployment",
                "description": (
                    "Set up automated CI/CD pipeline for ML models with testing, "
                    "validation, and rollback capabilities"
                ),
                "status": "todo",
            },
            {
                "title": "Implement multi-modal AI system",
                "description": (
                    "Build system that can process text, images, and audio using "
                    "transformer-based models"
                ),
                "status": "todo",
            },
            {
                "title": "Create AI-powered data annotation tool",
                "description": (
                    "Develop tool that uses AI to pre-annotate data and reduce "
                    "manual labeling effort"
                ),
                "status": "in_progress",
            },
            {
                "title": "Build conversational AI chatbot",
                "description": (
                    "Implement context-aware chatbot with memory, personality, "
                    "and multi-turn conversation handling"
                ),
                "status": "done",
            },
            {
                "title": "Design AI model explainability framework",
                "description": (
                    "Create system to explain model decisions using techniques like "
                    "SHAP, LIME, or attention visualization"
                ),
                "status": "todo",
            },
            {
                "title": "Implement federated learning system",
                "description": (
                    "Build distributed ML system that trains models across multiple "
                    "devices without sharing raw data"
                ),
                "status": "todo",
            },
            {
                "title": "Create AI-powered test generation",
                "description": (
                    "Develop system that automatically generates test cases using AI "
                    "to improve code coverage"
                ),
                "status": "in_progress",
            },
            {
                "title": "Build real-time AI inference API",
                "description": (
                    "Create high-performance API for real-time AI model inference "
                    "with caching and load balancing"
                ),
                "status": "done",
            },
            {
                "title": "Implement AI model versioning system",
                "description": (
                    "Build comprehensive versioning system for ML models with "
                    "metadata, lineage tracking, and rollback"
                ),
                "status": "todo",
            },
            {
                "title": "Create AI-powered documentation generator",
                "description": (
                    "Develop tool that automatically generates and updates technical "
                    "documentation from code"
                ),
                "status": "in_progress",
            },
        ]

        # Assign tasks to users with realistic distribution
        all_users = db.query(
            User
        ).all()  # Get all users including admin and demo users
        for i, user in enumerate(all_users):
            # Each user gets 4-6 tasks
            num_tasks = random.randint(4, 6)
            user_tasks = random.sample(ai_tasks, num_tasks)

            for task_data in user_tasks:
                # Create task with random creation date (within last 30 days)
                days_ago = random.randint(0, 30)
                created_at = datetime.utcnow() - timedelta(days=days_ago)

                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    user_id=user.id,
                    created_at=created_at,
                )
                db.add(task)

        db.commit()
        print(
            f"✅ Created {len(all_users)} users and {len(all_users) * 5} AI development tasks"
        )
        print("👑 Admin user: username='admin', password='admin123'")
        print("📋 Sample tasks include:")
        print("   • RAG system implementation")
        print("   • LLM fine-tuning")
        print("   • MLOps pipeline design")
        print("   • AI model monitoring")
        print("   • Prompt engineering framework")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


def force_reseed_demo_users():
    """Force re-seed demo users (for production fixes)."""
    db = SessionLocal()

    try:
        print("Force re-seeding demo users...")

        # Delete existing demo users
        demo_users = (
            db.query(User)
            .filter(User.username.in_(["user1", "user2", "user3"]))
            .all()
        )
        for user in demo_users:
            db.delete(user)

        # Create new demo users
        users = []
        for i in range(1, 4):
            username = f"user{i}"
            hashed_password = get_password_hash("password123")
            user = User(
                username=username,
                hashed_password=hashed_password,
                is_admin=False,
            )
            db.add(user)
            users.append(user)

        db.commit()
        print(f"✅ Re-created {len(users)} demo users")

    except Exception as e:
        print(f"❌ Error re-seeding demo users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--force-reseed":
        force_reseed_demo_users()
    else:
        seed_database()
