from drf_spectacular.extensions import OpenApiAuthenticationExtension

class UserServiceAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'core_auth.authentication.UserServiceAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }