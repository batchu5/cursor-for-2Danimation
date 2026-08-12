from fastapi import Request, HTTPException, Depends
from auth import verify_token

def get_current_user_id(request: Request):
    token = request.cookies.get("token")
    
    print("access_token cookie:", token)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
