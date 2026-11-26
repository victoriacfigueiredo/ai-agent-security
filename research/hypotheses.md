# Research Hypotheses

## Overall research objective

Evaluate how OAuth2 authorization policies and sender-constraining
mechanisms affect the ability of manipulated or compromised AI agents
to access unauthorized resources and the ability of attackers to replay
stolen access tokens.

## Stage 2: Broad OAuth2 machine-client authorization

### H2.1 — Machine authentication
An AI agent using OAuth2 Client Credentials can authenticate as a
machine client and obtain an access token without an interactive
human login.

### H2.2 — Broad permissions
If the machine client is assigned broad permissions, the agent can
access every API resource permitted by those permissions, regardless
of which resources are necessary for a particular task.

### H2.3 — Token validation
Resource servers that validate token signatures, issuer, audience,
expiration and required permissions should reject requests with
missing, invalid or insufficiently authorized tokens.

### H2.4 — Bearer-token replay
A valid bearer access token is a possession credential. An attacker
who obtains the token may be able to replay it from another client
until it expires.

### H2.5 — Identity headers
An unauthenticated identity header such as X-Acting-User should not
be accepted as proof of identity when the API requires OAuth2
access-token authentication.

## Later stages

- Stage 3: Evaluate least-privilege permissions.
- Stage 4: Evaluate DPoP-bound access tokens.
- Stage 5: Evaluate mTLS-bound access tokens.

The DPoP and mTLS experiments will distinguish theft of the access
token alone from compromise of the associated private key or client.
