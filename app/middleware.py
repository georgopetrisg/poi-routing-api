from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, g
from app.errors import APIError
import time
import uuid
import logging

logger = logging.getLogger(__name__)

request_history = defaultdict(list)

blocked_users = {}

TRIGGER_LIMIT = 6
TRIGGER_WINDOW = 60 
BAN_DURATION = 180

def setup_middleware(app):
    
    @app.before_request
    def before_request():
        req_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_id = req_id
        g.start_time = time.time()

        token = request.headers.get('X-API-KEY')
        g.user = None

        if token:
            from app.models import User
            user = User.query.filter_by(api_token=token).first()
            if user:
                g.user = user

        if request.path == '/routes/compute':
            rate_limit()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            elapsed_ms = int(elapsed * 1000)
        else:
            elapsed_ms = 0
        
        response.headers['X-Request-ID'] = g.request_id
        full_path = request.full_path.rstrip('?')

        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        else:
            ip = request.remote_addr or 'unknown'

        user_info = "Guest"
        if hasattr(g, 'user') and g.user:
            user_info = f"User: {g.user.id}"
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        log_message = (
            f"[{timestamp}] "
            f"[{g.request_id}] "
            f"[{ip}] "
            f"[{user_info}] "
            f"[{request.method} {full_path}] -> "
            f"[{response.status_code} ({elapsed_ms}ms)]"
        )
        
        logger.info(log_message)

        return response

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