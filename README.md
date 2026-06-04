# Credit Bureau Assistant

A full-stack project that combines:

- a Django REST API for KYC and credit-report request handling
- a Chainlit chatbot that guides users through the request flow
- PostgreSQL for persistent storage
- Docker Compose for local orchestration

The chatbot collects user details, checks KYC status, creates credit bureau requests, and lets the user choose a delivery method for the report.

## Project Structure

- `backend/` - Django REST API
- `chatbot/` - Chainlit agent and conversation flow
- `docker-compose.yml` - local multi-container setup
- `README.md` - this guide

## Main Flow

1. The user chats with the Chainlit assistant.
2. The assistant checks whether a KYC record exists.
3. If KYC is missing, the bot asks for name, phone number, and email.
4. Once KYC is marked as `verified`, the bot creates a credit bureau request.
5. The user chooses delivery by `email` or `postal`.
6. The bot stores the delivery preference and can later show request status.

## Tech Stack

- Python 3.11+ for the chatbot
- Python 3.12 for the backend container
- Django 6
- Django REST Framework
- PostgreSQL 17
- Chainlit
- DSPy / LiteLLM
- Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- An LLM API key for the chatbot
- A PostgreSQL database if you run the backend outside Docker

## Environment Variables

Create a `.env` file in the project root with at least these values:

```env
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword

BACKEND_URL=http://backend:8000
API_KEY_2=your_llm_api_key
NGROK_AUTHTOKEN=your_ngrok_token
```

Optional notes:

- `BACKEND_URL` should point to the backend service from the chatbot container.
- `NGROK_AUTHTOKEN` is only needed if you use the included ngrok service.
- The backend currently reads Postgres settings from `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

## Run With Docker

1. Make sure your `.env` file is in the project root.
2. Start the stack:

```bash
docker compose up --build
```

3. Open the services:

- Backend: `http://localhost:8000`
- Chainlit chatbot: `http://localhost:8501`
- ngrok admin UI: `http://localhost:4040`

## Run Locally Without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Chatbot

```bash
cd chatbot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chainlit run app.py --host 0.0.0.0 --port 8501
```

When running locally, set `BACKEND_URL` to the backend address your chatbot can reach, for example `http://127.0.0.1:8000`.

## Backend API

Base path: `/api/`

### KYC

- `POST /api/kyc/create/` - create a new KYC record
- `GET /api/kyc/status/?kyc_id=<uuid>` - fetch KYC status

### Credit bureau requests

- `POST /api/credit-request/create/` - create a request for a verified KYC
- `GET /api/credit-request/status/<track_id>/` - fetch a request by track ID
- `GET /api/credit-request/by-user/?kyc_id=<uuid>` - fetch the latest request for a KYC record
- `POST /api/credit-request/delivery/` - set delivery method and destination
- `POST /api/credit-request/verify-track/` - verify a track ID against an email address

## Data Model Summary

### `KYC`

- `first_name`
- `last_name`
- `email`
- `phone_number`
- `kyc_status` - `pending`, `verified`, or `rejected`
- timestamps

### `CreditBureauRequest`

- `track_id`
- foreign key to `KYC`
- `status` - `requested`, `processing`, `completed`, or `rejected`
- `delivery_method` - `email` or `postal`
- `email_delivery`
- `postal_address`
- `document_url`
- `admin_note`
- timestamps

## Useful Notes

- The backend uses PostgreSQL and expects the database container to be available at host `db` when running in Docker.
- The chatbot stores temporary session data in Chainlit user session memory.
- The current backend allows KYC creation and request creation, but KYC verification status is managed in the database or admin interface rather than through a separate approval workflow in code.
- `backend/config/settings.py` currently enables `DEBUG=True`, which is fine for local development but should be changed for production.

## Troubleshooting

- If the chatbot cannot reach the backend, check `BACKEND_URL` in `.env`.
- If Postgres connection fails, verify the database credentials in `.env` and that the `db` service is running.
- If the chatbot cannot call the LLM, confirm `API_KEY_2` is set correctly.
- If you change model choice or provider, update `chatbot/config.py`.

## License

No license file is included yet. Add one if you plan to share or publish this project.
