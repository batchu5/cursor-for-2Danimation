import os
import requests
from jose import jwt, JWTError
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
ALGORITHMS = ["RS256"]


@lru_cache()
def get_jwks():
    """Fetch and cache Auth0's JSON Web Key Set (public keys for RS256 verification)."""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def verify_auth0_token(token: str) -> dict:
    """
    Verify an Auth0 JWT access token using RS256 + JWKS.
    Returns the decoded payload if valid, or raises an exception.
    """
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)

    # Find the matching key from JWKS
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break

    if not rsa_key:
        raise JWTError("Unable to find matching key in JWKS")

    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=ALGORITHMS,
        audience=AUTH0_API_AUDIENCE,
        issuer=f"https://{AUTH0_DOMAIN}/",
    )

    return payload