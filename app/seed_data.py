from app.database import SessionLocal
from app.models.database_models import User, Task, TimeLog, Estimate
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database():
    """Seed the database with professional demo data."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already seeded, skipping...")
            return
        
        # Create professional demo users
        demo_user = User(
            username="demo_user",
            hashed_password=pwd_context.hash("demo123"),
            is_admin=False
        )
        
        admin_user = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            is_admin=True
        )
        
        db.add(demo_user)
        db.add(admin_user)
        db.commit()
        
        # Create professional demo tasks
        tasks = [
            Task(
                title="Implement user authentication system",
                description="Build secure JWT-based authentication with login and signup functionality",
                status="done",
                total_minutes=240.0,
                user_id=demo_user.id
            ),
            Task(
                title="Design database schema and models",
                description="Create comprehensive database schema with proper relationships and constraints",
                status="in_progress",
                total_minutes=180.0,
                user_id=demo_user.id
            ),
            Task(
                title="Build task management API",
                description="Develop RESTful API endpoints for task CRUD operations and status management",
                status="todo",
                total_minutes=0.0,
                user_id=demo_user.id
            ),
            Task(
                title="Deploy application to cloud platform",
                description="Set up containerization and deploy to production environment",
                status="todo",
                total_minutes=0.0,
                user_id=admin_user.id
            )
        ]
        
        for task in tasks:
            db.add(task)
        db.commit()
        
        # Create professional demo time logs
        now = datetime.utcnow()
        timelogs = [
            TimeLog(
                task_id=tasks[0].id,
                start_time=now - timedelta(hours=4),
                end_time=now - timedelta(hours=2),
                duration=120.0
            ),
            TimeLog(
                task_id=tasks[0].id,
                start_time=now - timedelta(hours=2),
                end_time=now - timedelta(hours=1),
                duration=60.0
            ),
            TimeLog(
                task_id=tasks[1].id,
                start_time=now - timedelta(hours=3),
                end_time=now - timedelta(hours=1.5),
                duration=90.0
            )
        ]
        
        for timelog in timelogs:
            db.add(timelog)
        db.commit()
        
        # Create professional demo estimates
        estimates = [
            Estimate(
                task_id=tasks[2].id,
                estimated_min=2.0,
                estimated_max=4.0
            ),
            Estimate(
                task_id=tasks[3].id,
                estimated_min=1.0,
                estimated_max=2.0
            )
        ]
        
        for estimate in estimates:
            db.add(estimate)
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created {len([demo_user, admin_user])} users")
        print(f"Created {len(tasks)} tasks")
        print(f"Created {len(timelogs)} time logs")
        print(f"Created {len(estimates)} estimates")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database() 