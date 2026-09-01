class RealIPMiddleware:
    """Sets REMOTE_ADDR from X-Forwarded-For for reverse proxy setups."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            if xff:
                client_ip = xff.split(',')[0].strip()
                if client_ip:
                    request.META['REMOTE_ADDR'] = client_ip
        return self.get_response(request)