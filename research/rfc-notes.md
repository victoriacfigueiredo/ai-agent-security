# RFC Notes

## RFC 6749 — The OAuth 2.0 Authorization Framework

https://www.rfc-editor.org/rfc/rfc6749

Relevant to Stage 2:

- Section 4.4 defines the Client Credentials grant.
- The grant is intended for confidential clients.
- The client authenticates to the authorization server and
  obtains an access token.
- It represents machine-client authorization, not interactive
  human-user authentication.

Experiment mapping:

The ai-agent client uses the Client Credentials grant to obtain
an access token from Keycloak.

Important distinction:

The client credentials identify the machine client. They do not
establish the identity of an individual employee.

## RFC 6750 — The OAuth 2.0 Authorization Framework: Bearer Token Usage

https://www.rfc-editor.org/rfc/rfc6750

Relevant to Stage 2:

- Bearer tokens are usable by any party possessing them.
- The standard Authorization header format is:
  Authorization: Bearer <token>
- Bearer-token disclosure is therefore a security risk.

Experiment mapping:

The replay test reused the same valid bearer token from a separate
HTTP client. The Customers API accepted it with HTTP 200.

This is consistent with the bearer-token possession model.

## RFC 7519 — JSON Web Token (JWT)

https://www.rfc-editor.org/rfc/rfc7519

Relevant to Stage 2:

JWT defines a compact claims representation.

Claims relevant to this experiment include:

- iss: token issuer
- aud: intended audience
- exp: token expiration time

Experiment mapping:

The APIs validate the issuer, audience and expiration claims,
as well as the JWT signature.

JWT is the token format used by this Keycloak implementation.
OAuth2 itself does not require access tokens to be JWTs.

## RFC 9700 — Best Current Practice for OAuth 2.0 Security

https://www.rfc-editor.org/rfc/rfc9700

Relevant to the research:

This document provides current OAuth 2.0 security
recommendations and discusses risks associated with access
tokens, token leakage, and authorization-server/client security.

It is relevant to the later evaluation of token protection,
audience restriction and secure client behavior.

## RFC 8705 — OAuth 2.0 Mutual-TLS Client Authentication and
Certificate-Bound Access Tokens

https://www.rfc-editor.org/rfc/rfc8705

Planned for Stage 5:

Defines OAuth 2.0 mutual-TLS client authentication and
certificate-bound access tokens.

The experiment will evaluate whether a stolen token can be
replayed without possession of the associated client certificate
and private key.

## RFC 9449 — OAuth 2.0 Demonstrating Proof of Possession (DPoP)

https://www.rfc-editor.org/rfc/rfc9449

Planned for Stage 4:

Defines a mechanism for sender-constraining OAuth 2.0 access
and refresh tokens using proof-of-possession.

The experiment will evaluate whether a stolen token alone is
sufficient for replay when DPoP binding is enforced.

## Additional considerations

The current Stage 2 implementation uses Keycloak realm roles
as application permissions. These roles are not OAuth2 scopes.

The OAuth2 scope claim in the current token must not be confused
with the realm_access.roles claim used by the API authorization
checks.

Resource Indicators (RFC 8707) and Token Exchange (RFC 8693)
may be considered in a later delegated-authorization design.
They are not implemented in Stage 2.
