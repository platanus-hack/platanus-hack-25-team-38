# Memo 👴

Sistema de recordatorios y gestión de cuidado para adultos mayores.

## 🚀 Inicio Rápido

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

### Backend (FastAPI)
```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

El API estará disponible en `http://localhost:8000`

## 📋 Requisitos

- Node.js 20+
- Python 3.13+
- PostgreSQL (Neon)

## 🏗️ Stack Tecnológico

- **Frontend:** Next.js 16, React 19, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, PostgreSQL (Neon)
- **Integraciones:** Gemini AI, Kapso, Telegram, Twilio

## 📦 Funcionalidades

- ✅ Recordatorios automáticos de medicamentos vía WhatsApp/Telegram
- 📅 Calendario de eventos médicos
- 👪 Dashboard para familiares
- 📊 Seguimiento de medicación