import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-vccrnzts.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthError(error = 'no authorization header is present', status_code = 401)
    split_header = auth_header.split(' ')
    if len(split_header)!=2:
        raise AuthError(error = 'Authorization header length is lest than 2', status_code = 401)
    if split_header[0].lower() != 'bearer':
        raise AuthError(error = 'bearer not present', status_code = 401)

    print(auth_header)
    return split_header[1]


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError(error = 'permission key not in payload', status_code = 401)
    if permission not in payload['permissions']:
        raise AuthError(error = 'User does not have permission', status_code = 401)
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError(error = 'Authorization malformed', status_code = 401)
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError(error = 'Token expired.', status_code = 401)

        except jwt.JWTClaimsError:
            raise AuthError(error = 'Incorrect claims. Please, check the audience and issuer.', status_code = 401)
        except Exception:
            raise AuthError(error = 'Unable to parse authentication token.', status_code = 400)
    raise AuthError(error = 'Unable to find the appropriate key.', status_code = 401)
        


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
