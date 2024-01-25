from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# verifies that user session is active before any action is taken 
# when token expires, JSON response is sent to frontend 
# react context API handles the rest 
async def verify_session_token(request: Request, call_next):
    # get managers from app state for utils
    user_manager = request.app.state.user_manager
    auth_manager = request.app.state.auth_manager
    exempt_paths = ["/auth/login", "/auth/register"]
    
    # check if the request path is in the list of exempt paths
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # intercept incoming requests to extract session token from cookies
    session_token = request.cookies.get("session_key")
    
    if(session_token):
    # if session is active, get the user
        user_id = await auth_manager.get_redis_token(session_token)
        # if this user exists, that means the token is still valid    
        if(user_id):
            return await call_next(request)
        else:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired session token"})
    else:
        # no session key exists
        return JSONResponse(status_code=401, content={"detail": "Active session not found"})