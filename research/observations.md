# Experimental Observations

## Stage 0 — No authorization

The APIs initially exposed synthetic company data without access
controls. The agent could retrieve records across all resource
categories.

## Stage 1 — Simple application-level authorization

The APIs enforced local authorization rules based on the
X-Acting-User request header.

The Stage 1 test suite contained 29 scenarios and all passed.

Limitation: X-Acting-User was not cryptographically authenticated.
A caller able to modify the header could impersonate another user.

## Stage 2 — OAuth2 Client Credentials with broad Bearer token

### Configuration

- Authorization server: Keycloak 26.4.2
- Realm: ai-agent-lab
- OAuth2 client: ai-agent
- Grant type: client_credentials
- Token format: JWT
- Signing algorithm: RS256
- Resource audience: ai-agent-apis
- Access-token lifetime: approximately five minutes
- Resource servers: Documents, HR and Finance APIs

The machine client was assigned four Keycloak realm roles:

- documents
- employees
- finance
- customers

These are realm roles, not OAuth2 scopes. The roles were included
in the JWT under realm_access.roles.

The APIs validated the JWT signature, issuer, audience, expiration
and required realm role.

### Automated test results

Test report: reports/stage2-results.json

Total tests: 15
Passed: 15
Failed: 0

#### Successful access

The valid machine token accessed all four resource categories:

- Documents: 3 records, HTTP 200
- Employees: 3 records, HTTP 200
- Financial reports: 3 records, HTTP 200
- Customers: 2 records, HTTP 200

#### Rejected requests

- Missing token: HTTP 401 on all four APIs.
- Invalid token: HTTP 401.
- Forged X-Acting-User header without a bearer token: HTTP 401.

#### Token replay

The same valid bearer token was reused by a separate HTTP client
to access the Customers API.

Result: HTTP 200.

This demonstrates that possession of the valid bearer token was
sufficient for access from another client during its validity period.

The test simulates token theft and replay; it does not simulate
remote compromise of a real agent host.

#### Agent integration

The local Ollama-powered agent successfully invoked all four tools
and retrieved all expected records.

A manual natural-language test also successfully requested an
overview of documents, employees, financial reports and customers.

### Interpretation

OAuth2 Client Credentials successfully authenticated the AI agent
as a machine client. JWT validation prevented unauthenticated and
invalid-token requests.

However, the machine client had broad permissions. The APIs
therefore allowed access to all four resource categories.

Bearer-token authentication did not prevent replay by another
client possessing the same valid token.

### Limitations

- The data is synthetic.
- The experiment uses one broadly authorized machine client.
- The current test suite does not test denial based on missing
  individual realm roles.
- The experiment does not yet compare restricted permissions,
  DPoP or mTLS.
- The replay test uses a separate local HTTP client, not a
  remote attacker or a compromised production environment.
- No human-user delegation is implemented in this stage.

## Stage 2 conclusion

Stage 2 demonstrates that OAuth2 machine authentication and JWT
validation provide an important authentication boundary, but do
not by themselves enforce least privilege or prevent replay of
a stolen bearer token.
