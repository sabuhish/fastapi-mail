# fastapi-mail — Claude Context

## What this is
An async Python library for sending emails from FastAPI/Starlette apps. Core features: SMTP sending, Jinja2 templates, file attachments, optional Redis-backed email validation.

## Project structure

### Library (`fastapi_mail/`)
- `fastmail.py` — main `FastMail` class, entry point for sending
- `config.py` — `ConnectionConfig` (Pydantic settings model)
- `schemas.py` — `MessageSchema`, `MessageType`
- `msg.py` — `MailMsg` builds the raw MIME message
- `connection.py` — SMTP connection handling via aiosmtplib
- `email_utils/email_check.py` — `DefaultChecker` and `WhoIsXmlApi` for email validation
- `errors.py` — custom exceptions

### Tests (`tests/`)
- `conftest.py` — shared fixtures including `redis_checker` (backed by fakeredis)
- `test_connection.py` — SMTP sending and attachment tests
- `test_checker.py` — email validation tests
- `test_redis_config.py` — Redis-backed checker tests
- `test_message.py` — MIME message construction tests
- `test_fastapi_mail.py` — FastAPI integration tests

### Docs (`docs/`)
- `index.md` — overview and quickstart
- `install.md` — installation instructions including optional extras
- `getting-started.md` — basic usage examples
- `example.md` — advanced examples (templates, attachments, Redis checker)
- `contribute.md` — contribution guide

## Key conventions
- All sending is async; never introduce blocking I/O in the sending path
- Pydantic v2 throughout — no v1 compat shims
- Redis is optional (`pip install fastapi-mail[redis]`); guard any Redis import with a try/except
- `SUPPRESS_SEND=1` in `ConnectionConfig` enables outbox mode for testing
- `DefaultChecker` requires `init_redis()` to be called before use when `db_provider="redis"`

## What to focus on in code reviews

### Async correctness
- No blocking calls (I/O, DNS, file reads) inside async functions
- DNS lookups must use `dns.asyncresolver`, not `dns.resolver`
- Database or HTTP calls must use async clients

### Security
- No credentials, passwords, or tokens hardcoded or interpolated into URLs, logs, or error messages
- Redis passwords must be passed as kwargs, not embedded in connection URLs
- New `ConnectionConfig` fields that accept secrets should use `SecretStr`
- No unsafe defaults (e.g. `VALIDATE_CERTS=False` should never be a default)

### Breaking API changes
- Any change to `ConnectionConfig`, `MessageSchema`, or `FastMail` public methods is a breaking change
- New required fields must have defaults or a migration path
- Removed fields or renamed parameters need a deprecation notice

### Dependency hygiene
- Redis must stay optional — never import it at the top level without a try/except guard
- New dependencies must be justified and added to `pyproject.toml`
- Heavy dependencies (httpx, cryptography) belong in optional extras, not core

### Test coverage
- Every new feature needs a test, especially for the Redis and attachment paths
- Tests must use `SUPPRESS_SEND=1` — never send real emails in CI
- Use `fakeredis` for Redis tests, never a real Redis instance
- Avoid asserting on internal MIME structures (`_payload`, `_headers`) — use public email API

### Docs
- New `ConnectionConfig` fields must be documented in `docs/getting-started.md`
- New features need an example in `docs/example.md`
- Optional extras must be mentioned in `docs/install.md`
- Keep code snippets in docs in sync with the actual API
