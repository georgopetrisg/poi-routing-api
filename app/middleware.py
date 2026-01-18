from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, jsonify
from app.errors import APIError

request_history = defaultdict(list)

blocked_users = {}

TRIGGER_LIMIT = 6
TRIGGER_WINDOW = 60 
BAN_DURATION = 180

def setup_middleware(app):
    
    @app.before_request
    def rate_limit():
        if request.path != '/routes/compute':
            return

        user_id = request.headers.get('X-API-KEY') or request.remote_addr
        
        now = datetime.now()

        if user_id in blocked_users:
            expiry_time = blocked_users[user_id]
            
            if now < expiry_time:
                wait_seconds = int((expiry_time - now).total_seconds())
                raise APIError(
                    message=f"You are temporarily banned due to excessive requests. You made more than {TRIGGER_LIMIT} requests in 1 minute.",
                    status_code=429,
                    details={
                        "retry_after_seconds": wait_seconds
                    }
                )
            else:
                del blocked_users[user_id]
                if user_id in request_history:
                    del request_history[user_id]

        window_start = now - timedelta(seconds=TRIGGER_WINDOW)
        request_history[user_id] = [t for t in request_history[user_id] if t > window_start]
        
        if len(request_history[user_id]) >= TRIGGER_LIMIT:
            ban_expiry = now + timedelta(seconds=BAN_DURATION)
            blocked_users[user_id] = ban_expiry

            raise APIError(
                message=f"Too many requests! You are now blocked for {BAN_DURATION//60} minutes.",
                status_code=429,
                details={
                    "retry_after_seconds": BAN_DURATION
                }
            )
        request_history[user_id].append(now)