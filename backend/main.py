import secrets
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database

database.create_tables()

app = FastAPI(title="Barbearia Vintage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_tokens = set()

N8N_WEBHOOK_URL = "https://rafaelnovakalberto.app.n8n.cloud/webhook/cca70a2a-f25e-4375-957b-72ab41423c83"

def check_auth(token: str):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Token inválido")
    
class LoginRequest(BaseModel):
    username: str
    password: str

class ClientRequest(BaseModel):
    name: str
    email: str | None = None
    notes: str | None = None

class AppointmentRequest(BaseModel):
    client_id: int
    date: str
    time: str
    service: str

class StatusRequest(BaseModel):
    status: str

@app.post("/login")
def login(data: LoginRequest):
    if not database.verify_login(data.username, data.password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    token = secrets.token_hex(16)
    active_tokens.add(token)
    return {"token": token}

def get_clients(token: str):
    check_auth(token)
    return database.list_clients()

def post_client(client: ClientRequest, token: str):
    check_auth(token)
    new_id = database.create_client(client.name, client.email, client.notes)
    return {"id": new_id}

def put_client(client_id: int, client: ClientRequest, token: str):
    check_auth(token)
    database.update_client(client_id, client.name, client.email, client.notes)
    return {"ok": True}

def delete_client_route(client_id: int, token: str):
    check_auth(token)
    database.delete_client(client_id)
    return {"ok": True}

app.add_api_route("/clients", get_clients, methods=["GET"])
#requisicao GET no endereco /clients executa a funcao get_clients
app.add_api_route("/clients", post_client, methods=["POST"])
app.add_api_route("/clients/{client_id}", put_client, methods=["PUT"])
app.add_api_route("/clients/{client_id}", delete_client_route, methods=["DELETE"])

def get_appointments(token: str):
    check_auth(token)
    return database.list_appointments()

def post_appointment(appt: AppointmentRequest, token: str):
    check_auth(token)
    new_id = database.create_appointment(appt.client_id, appt.date, appt.time, appt.service)
    client = database.get_client(appt.client_id)

    try:
        requests.post(N8N_WEBHOOK_URL, json={
            "appointment_id": new_id,
            "client_name": client["name"] if client else "Cliente",
            "client_email": client["email"] if client else None,
            "date": appt.date,
            "time": appt.time,
            "service": appt.service,
        }, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"[aviso] Não foi possível notificar o n8n: {e}")

    return {"id": new_id}

def put_appointment_status(appointment_id: int, data: StatusRequest, token: str):
    check_auth(token)
    database.update_appointment_status(appointment_id, data.status)
    return {"ok": True}

def delete_appointment_route(appointment_id: int, token: str):
    check_auth(token)
    database.delete_appointment(appointment_id)
    return {"ok": True}

app.add_api_route("/appointments", get_appointments, methods=["GET"])
app.add_api_route("/appointments", post_appointment, methods=["POST"])
app.add_api_route("/appointments/{appointment_id}/status", put_appointment_status, methods=["PUT"])
app.add_api_route("/appointments/{appointment_id}", delete_appointment_route, methods=["DELETE"])