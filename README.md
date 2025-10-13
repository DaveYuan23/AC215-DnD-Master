# 🧙‍♂️ DnD Master AI — Frontend (Milestone 2)

## Overview
This project is part of **AC215: Applied Deep Learning Systems** at Harvard.  
Our team is building an **AI Dungeon Master (DM)** that can narrate, guide, and manage interactive *Dungeons & Dragons* adventures.

This branch, **`milestone2-shiyu`**, focuses on the **frontend containerization and deployment setup**.  
The frontend runs independently in Docker and will later integrate with a FastAPI backend and RAG orchestration system.

The frontend stack includes:
- ⚛️ **Next.js 14 (App Router)**
- 🟦 **TypeScript**
- 🎨 **TailwindCSS + shadcn/ui**
- 📦 **pnpm** for fast, reproducible package management
- 🐳 **Docker** for containerized deployment

---

## ⚙️ Features
- 🎮 Interactive React-based player interface for the AI DM  
- 🧩 Modular component structure (`app/`, `components/`, `lib/`)  
- 🚀 Production-ready **multi-stage Docker build**  
- 🌐 Configurable backend endpoint via `NEXT_PUBLIC_API_BASE_URL`  
- 🔁 Ready for integration with FastAPI backend and vector-DB orchestrator  
- 🧱 Compatible with **Nginx reverse proxy** for unified routing  

---

## 🧰 Project Structure
```text
AC215-DnD-Master/
├── frontend/ # Next.js app
│ ├── app/
│ ├── components/
│ ├── lib/
│ ├── public/
│ ├── styles/
│ ├── package.json
│ ├── pnpm-lock.yaml
│ └── Dockerfile # SSR build for Milestone 2
│
├── infra/
│ └── nginx.conf # reverse proxy for / and /api
│
├── docker-compose.yml # minimal frontend-only compose
└── README.md # this file
```
---

## 🐳 Docker Setup

### 1️⃣ Build and Run (frontend only)
```bash
docker compose up --build
```
Then open:
👉 http://localhost:3000

This starts the production Next.js SSR server inside a container.

### 2️⃣ Stop the containers

Press Ctrl + C, or run:
```bash
docker compose down
```
