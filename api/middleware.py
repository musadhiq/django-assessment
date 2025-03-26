import logging
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

class BlockIPMiddleware:
    RATE_LIMIT = 100 
    TIME_WINDOW = 5 * 60  # 5 minutes in seconds
    BLOCK_TIME = 10 * 60  # 10 minutes block if exceeded

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if not ip:
            logger.warning("Missing IP address in request headers.")
            return self.get_response(request)
            
        key = f"rate_limit:{ip}"
        block_key = f"block:{ip}"

        # Check if IP is blocked
        if cache.get(block_key):
            logger.warning(f"IP {ip} blocked due to high request rate.")
            return JsonResponse(data={"error": "Access denied due to high request rate"}, status=429)

        # Increment request count on every request
        count = cache.get_or_set(key, default=1,timeout= self.TIME_WINDOW) + 1
        cache.set(key, count, self.TIME_WINDOW)


        if count > self.RATE_LIMIT:
            # if request count exceeds limit, add ip to block list
            cache.set(block_key, 1, self.BLOCK_TIME) 
            logger.warning(f"IP {ip} blocked due to high request rate.")
            return JsonResponse(data={"error": "Access denied due to high request rate"}, status=429)

        remaining = max(self.RATE_LIMIT - count, 0)
        response = self.get_response(request)
        response.headers["x-remaining-allowed-requests"] = remaining

        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip if ip else None
