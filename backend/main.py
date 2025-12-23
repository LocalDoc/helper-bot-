"""
PURPOSE:
Central startup file for the Pomogator FastAPI backend server.
It initializes the API server, registers all feature routers, sets up global
error handling, and manages application lifecycle.

WHAT HAPPENS WHEN THIS FILE RUNS:
1. FASTAPI APP CREATION: A new FastAPI instance named "Pomogator Backend" is created
2. ROUTER REGISTRATION: All feature modules (messages, credits, payments, etc.) are mounted
3. EXCEPTION HANDLERS: Custom business logic errors get converted to proper HTTP responses
4. LIFECYCLE HOOKS: Startup/shutdown events log when the server starts/stops
5. SERVER START: When executed, it begins listening on HOST:PORT (default: 0.0.0.0:8000)

API STRUCTURE:
├── /api/  All feature endpoints via included routers
│   ├── /process_message: AI message processing
│   ├── /credits: Credit management
│   ├── /payments: Payment processing  
│   ├── /users: User management
│   ├── /trial: Trial system
│   └── /webhook: External service webhooks

ERROR HANDLING:
• NotEnoughCredits: 402 Payment Required / 403 Forbidden
• UserNotFound: 404 Not Found
• PaymentValidationError: 400 Bad Request
• AIServiceError: 503 Service Unavailable / 500 Internal Server Error
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.utils.logger import logger
from backend.utils.exceptions import NotEnoughCredits, UserNotFound, PaymentValidationError, AIServiceError
from backend.api import process_message, credits, payments, users, trial, webhook

app = FastAPI(title="Pomogator Backend")

app.include_router(process_message.router)
app.include_router(credits.router)
app.include_router(payments.router)
app.include_router(users.router)
app.include_router(trial.router)
app.include_router(webhook.router)


@app.on_event("startup")
async def startup():
    logger.info("Pomogator backend starting")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Pomogator backend stopping")


@app.exception_handler(NotEnoughCredits)
async def handle_no_credits(request: Request, exc: NotEnoughCredits):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(UserNotFound)
async def handle_user_not_found(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(PaymentValidationError)
async def handle_payment_validation(request: Request, exc: PaymentValidationError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(AIServiceError)
async def handle_ai_error(request: Request, exc: AIServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.get("/health")
def health():
    return {"status": "ok"}