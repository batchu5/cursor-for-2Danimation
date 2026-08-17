from fastapi import Request, HTTPException
from auth import verify_auth0_token
from jose import JWTError


def get_current_user_id(request: Request) -> str:
    """
    Extract and verify the Auth0 JWT from the Authorization header.
    Returns the Auth0 'sub' claim (e.g. 'google-oauth2|1234567890').
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ", 1)[1]

    try:
        payload = verify_auth0_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing 'sub' claim")
        return user_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
