from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token
from app.api.auth import fake_users_db

oauth2_scheme = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    payload = decode_token(token.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    username = payload["sub"]
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 