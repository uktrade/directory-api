class GovukPaaSRemoteIPAddressRetriver:
    def get_ip_address(self, request):
        """
        Returns the IP of the client making a HTTP request, using the
        second-to-last IP address in the X-Forwarded-For header. This
        should not be able to be spoofed in GovukPaaS, but it is not
        safe to use in other environments.

        Args:
            request (HttpRequest): the incoming Django request object

        Returns:
            str: The IP address of the incoming request

        Raises:
            LookupError: The X-Forwarded-For header is not present, or
            does not contain enough IPs
        """
        if 'HTTP_X_FORWARDED_FOR' not in request.META:
            raise LookupError('X-Forwarded-For not in HTTP headers')

        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        ip_addesses = x_forwarded_for.split(',')
        if len(ip_addesses) < 2:
            raise LookupError('Not enough IP addresses in X-Forwarded-For')

        return ip_addesses[-2].strip()
