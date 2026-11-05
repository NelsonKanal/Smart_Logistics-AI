# SmartLogistics secure API patch
 
## What changed
- Registration and login with Argon2 password hashes and short-lived signed bearer tokens.
- New users always register as `customer`; the public registration endpoint cannot create admins.
- Customer shipment queries are filtered by the authenticated account.
- Shipment status updates require an admin role.
- Existing database shipments are migrated with nullable `owner_user_id`; legacy rows are hidden from customers until an admin verifies and assigns them.
- Stage 5 pricing, tracking and support are exposed as fixed backend operations. The API does not execute arbitrary shell commands.

## Apply
1. Back up `stage3_systems/smartlogistics.db` before changing code.
2. Copy the files from this patch into the matching paths in the project. The supplied `main_stage 3.py` should become `stage3_systems/main.py` (keep a backup of the original).
3. Ensure `stage3_systems/routers/__init__.py` exists (it can be empty).
4. Install dependencies from the project root:
   `python -m pip install -r requirements.txt`
5. Generate a secret locally, for example:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`
   Set that value as `SMARTLOGISTICS_JWT_SECRET` in your local environment or deployment secrets. Do not use the example placeholder.
6. Set `FRONTEND_ORIGINS` to the exact frontend origin. For local Live Server, `http://127.0.0.1:5500,http://localhost:5500`; for production, use only the real HTTPS frontend origin.
7. Run from the project root:
   `python -m uvicorn stage3_systems.main:app --reload`
8. Visit `/docs`, register a test customer with a password of at least 12 characters, and use the returned access token as `Authorization: Bearer <token>`.

## Frontend request contract
- `POST /auth/register` JSON: `{"full_name":"Test Customer","email":"test@example.com","password":"use-a-unique-long-password"}`.
- `POST /auth/login` JSON: `{"email":"test@example.com","password":"use-the-same-password"}`.
- Both return `access_token`, `token_type`, and `user`.
- `GET /auth/me` with `Authorization: Bearer <access_token>`.
- All `/shipments/` and `/agents/` endpoints require that header.
- When creating a shipment, send only `origin`, `destination`, `weight_kg`, and `service`. The backend takes the customer name and user ID from the authenticated account.
- Store access tokens in memory where possible; localStorage is vulnerable if an attacker can execute JavaScript on the page. For a production web app, consider a backend-for-frontend with Secure, HttpOnly, SameSite cookies and CSRF protections.

## Promote the first admin
Do not add a public “make me admin” endpoint. After registering your own trusted account, run this command from the project root, replacing the email:
`python -c "from stage3_systems.database import SessionLocal; from stage3_systems.models import User; db=SessionLocal(); u=db.query(User).filter(User.email=='your-admin-email@example.com').first(); assert u, 'Register this account first'; u.role='admin'; db.commit(); print('Admin role assigned'); db.close()"`

## Important migration note
Existing shipments are not automatically assigned to any customer. Verify each old record and its intended owner before using the admin assignment endpoint. Do not expose legacy shipments to customers based only on matching display names.

## Before real customer data / public launch
This patch is a security foundation, not a full production audit. Add HTTPS at the host, login rate limiting, email verification/password reset, audit logs, monitoring, backup/restore tests, dependency pinning and vulnerability checks. SQLite is best suited to a small single-instance deployment; use a managed database such as PostgreSQL if the host runs multiple instances or needs concurrent production writes. Avoid collecting real customer information until these protections have been tested.

## Stage 5 limitation
The `/agents/track/{shipment_id}` endpoint checks ownership before invoking the existing tracking agent. Confirm the tracking agent itself returns only the requested shipment and does not expose unrelated data. The `/agents/price` and `/agents/support` endpoints invoke fixed task names. No client input is treated as a command or Python module.
