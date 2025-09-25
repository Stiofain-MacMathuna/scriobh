# Scríobh - Secure Notes App

A full-stack web application for securely creating, storing, and managing personal notes — built with **FastAPI**, **React**, **PostgreSQL**, and **Docker**, and deployed to the cloud using **AWS EC2**, **RDS**, and **NGINX**. This project demonstrates my ability to build, containerize, and deploy secure, scalable applications using modern development practices.

**Live Demo:** [https://www.scriobh.io](https://www.scriobh.io)

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

| Layer       | Technology                          |
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

## Getting Started (Local Development)

### Prerequisites

- Docker & Docker Compose installed  
- Git installed  

### Setup

```bash
git clone https://github.com/Stiofain-MacMathuna/secure-notes-app.git
cd secure-notes-app/scriobh-dev
docker-compose up --build
```

The app will be available at:

**Frontend**: http://localhost:3000

**Backend**: http://localhost:8000

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

## Running Tests

### Backend

```bash
docker-compose exec backend pytest
```

### Frontend

```bash
docker-compose exec frontend npm test
```

## Project Structure

```text
secure-notes-app/
├── backend/         # FastAPI app with Alembic migrations
├── frontend/        # React app
├── nginx/           # NGINX config for reverse proxy + HTTPS
├── docker-compose.yml
├── docker-compose.override.yml
└── pg_hba.override.conf
```

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
