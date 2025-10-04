# Scríobh - Secure Notes App

A full-stack web application for securely creating, storing, and managing personal notes — built with **FastAPI**, **React**, **PostgreSQL**, and **Docker**, and deployed to the cloud using **AWS EC2**, **RDS**, and **NGINX**. This project demonstrates my ability to build, containerize, and deploy secure, scalable applications using modern development practices.

**Live Demo:** [https://www.scriobh.io](https://www.scriobh.io)

---

## Why This Project?

This app showcases my ability to:

- Build secure, production-ready APIs  
- Design clean, responsive UIs  
- Manage environment-specific configurations  
- Automate database migrations  
- Containerize and deploy full-stack apps to the cloud  
- Configure HTTPS and reverse proxies for secure traffic  
- Integrate cloud services like EC2 and RDS for scalable infrastructure  

I built this as part of my portfolio to demonstrate end-to-end development and deployment skills across both application and infrastructure layers.

---

## Features

- Secure user authentication with JWT tokens  
- Encrypted note storage for privacy  
- RESTful API built with FastAPI and SQLAlchemy  
- Responsive React frontend  
- Dockerized for easy local development  
- Alembic migrations run automatically on startup  
- Cloud deployment on AWS EC2 with HTTPS via NGINX reverse proxy  
- PostgreSQL hosted on AWS RDS  
- HTTPS enabled using Let's Encrypt SSL certificates  

---

## Tech Stack

| Layer       | Technology                           |
|-------------|--------------------------------------|
| Frontend    | React, Vite                          |
| Backend     | FastAPI, SQLAlchemy, Alembic         |
| Database    | PostgreSQL (AWS RDS)                 |
| Auth        | JWT                                  |
| DevOps      | Docker, Docker Compose, NGINX        |
| Cloud       | AWS EC2, AWS RDS                     |
| Security    | HTTPS via Let's Encrypt              |
| Testing     | Pytest (backend)                     |

---

## Project Structure

```text

├── backend
├── certbot-webroot
├── docker-compose.override.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── frontend
├── init.sql
├── nginx.Dockerfile
├── notes-app.conf
├── pytest.ini
├── README.md
├── requirements.txt
└── venv
```

---

## Getting Started (Local Development)

### Prerequisites

- Docker & Docker Compose installed  
- Git installed  

### Setup

```bash
git clone https://github.com/Stiofain-MacMathuna/scriobh.git
cd secure-notes-app
docker-compose up --build
```

The app will be available at:

**Frontend**: http://localhost:3000

**Backend**: http://localhost:8000

### Cleanup

```bash
docker-compose down --volumes --remove-orphans
docker container prune
docker image prune -a
```

---

## Cloud Deployment

The production version of this app is deployed on:

- **AWS EC2** — Hosts the Dockerized backend and frontend  
- **AWS RDS** — Manages the PostgreSQL database  
- **NGINX** — Acts as a reverse proxy, routing traffic to frontend/backend and enforcing HTTPS  
- **HTTPS** — Secured using Let's Encrypt certificates  

### Deployment Highlights

- Docker containers orchestrated on EC2 using `docker-compose`  
- NGINX routes `/api` to FastAPI and `/` to React  
- SSL certificates auto-renewed via Certbot  
- Environment variables managed securely via `.env.prod`  
- Backend connects to RDS with secure credentials and connection pooling  

---

## Testing 

This project includes a comprehensive test suite for authentication, notes, health checks, and security. Here's how to run it locally.

## Step 1: Start Postgres via Docker

Make sure Docker is installed and running. Then start the test database:

```bash
docker run --name notes-app-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=notes-app-db \
  -p 5432:5432 \
  -d postgres:15
```

##  Step 2: Apply Alembic Migrations

Run this from the backend/ directory to initialize the schema:

```bash
cd backend
DOTENV=.env.test alembic upgrade head
```

Note: Environment variables are hardcoded in .env.test. No setup required beyond starting the database.

## Step 3: Run the Tests (from backend/)

Tests must be run from the backend/ folder to ensure correct path resolution and environment loading:

```bash
cd backend
pytest -v
```

This will execute all tests across the following modules:

| Module          | Description                            |
|-----------------|----------------------------------------|
| test_auth.py    | Registration, login, and auth endpoints|
| test_notes.py   | CRUD operations for notes              |
| test_health.py  | Health check and DB connectivity       |
| test_security.py| Password hashing and JWT validation    |

## Clean Up

To stop and remove the test database:

```bash
docker stop notes-app-db
docker rm notes-app-db
```
---
