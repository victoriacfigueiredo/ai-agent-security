import os

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080").rstrip("/")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ai-agent-lab")

ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"
AUDIENCE = "ai-agent-apis"

jwks_client = PyJWKClient(JWKS_URL)
bearer_scheme = HTTPBearer(auto_error=False)


def require_role(required_role: str):
    def verify_token(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    ):
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(
                credentials.credentials
            )

            claims = jwt.decode(
                credentials.credentials,
                signing_key.key,
                algorithms=["RS256"],
                issuer=ISSUER,
                audience=AUDIENCE,
                options={"require": ["exp", "iss", "aud"]},
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        roles = claims.get("realm_access", {}).get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return claims

    return verify_token
