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

        if hasattr(g, 'user') and g.user:
            identifier = g.user.api_token
            limit_count = g.user.requests_limit
            window_size = g.user.window_seconds
        else:
            identifier = request.remote_addr
            limit_count = 5
            window_size = 60
        
        now = datetime.now()

        if identifier in blocked_users:
            expiry_time = blocked_users[identifier]
            
            if now < expiry_time:
                wait_seconds = int((expiry_time - now).total_seconds())
                raise APIError(
                    message=f"You are temporarily banned due to excessive requests. You made more than {limit_count} requests in 1 minute.",
                    status_code=429,
                    details={
                        "retry_after_seconds": wait_seconds
                    }
                )
            else:
                del blocked_users[identifier]
                if identifier in request_history:
                    del request_history[identifier]

        window_start = now - timedelta(seconds=window_size)
        request_history[identifier] = [t for t in request_history[identifier] if t > window_start]
        
        if len(request_history[identifier]) >= limit_count:
            ban_expiry = now + timedelta(seconds=BAN_DURATION)
            blocked_users[identifier] = ban_expiry

            raise APIError(
                message=f"Too many requests! You are now blocked for {BAN_DURATION//60} minutes.",
                status_code=429,
                details={
                    "retry_after_seconds": BAN_DURATION
                }
            )
        request_history[identifier].append(now)