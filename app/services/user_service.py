from sqlalchemy.orm import Session
from app.models.user import User, UserCreate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user management operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = (
            self.db.query(User)
            .filter(User.username == user_data.username)
            .first()
        )

        if existing_user:
            raise ValueError("Username already registered")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username, hashed_password=hashed_password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate a user with username and password."""
        user = self.db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def get_user_by_username(self, username: str) -> User:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
