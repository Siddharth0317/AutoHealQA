# 🚀 AutoHealQA Production Deployment Guide

This guide provides step-by-step instructions for deploying **AutoHealQA** to production using **Render / Railway (Backend + Playwright)** and **Vercel (Frontend)**, or deploying via **Docker Compose**.

---

## 🛠️ Prerequisites

Before deploying, ensure you have:
1. **GitHub Repository**: Code pushed to GitHub (`git push origin main`).
2. **Groq API Key**: Production key from [console.groq.com](https://console.groq.com).
3. **Supabase Cloud Project**: Database project at [supabase.com](https://supabase.com) with [`storage/schema.sql`](file:///c:/Projects/AutoHealQA/storage/schema.sql) executed.

---

## 🌐 Option A: Managed Cloud Deployment (Render + Vercel)

### Step 1: Execute Database Schema on Supabase
1. Log into your Supabase Dashboard.
2. Go to **SQL Editor** -> **New Query**.
3. Copy & paste the contents of [`storage/schema.sql`](file:///c:/Projects/AutoHealQA/storage/schema.sql) and click **Run**.

### Step 2: Deploy Backend Container to Render / Railway
1. Log into [Render.com](https://render.com) or [Railway.app](https://railway.app).
2. Click **New +** -> **Web Service** -> Connect your GitHub repo `AutoHealQA`.
3. Select **Docker** as the Runtime environment.
4. Set the build directory to `/` (Root directory where `Dockerfile` lives).
5. Add the following **Environment Variables**:

| Variable | Recommended Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Production environment flag |
| `GROQ_API_KEY` | `gsk_...` | Groq Llama-3.3 70B API Key |
| `SUPABASE_URL` | `https://xxxx.supabase.co` | Your Supabase Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJ...` | Supabase Service Role Secret Key |
| `ADMIN_PASSCODE` | `admin123` | Security Passcode for Admin Telemetry |
| `CORS_ORIGINS` | `https://autohealqa.vercel.app,*` | Allowed frontend domains |

6. Click **Deploy Web Service**. Render/Railway will build the Docker container and pre-install Chromium, Firefox, and WebKit binaries automatically.
7. Note down your live Backend API URL: e.g. `https://autohealqa-backend.onrender.com`.

### Step 3: Deploy Frontend to Vercel
1. Log into [Vercel.com](https://vercel.com).
2. Click **Add New Project** -> Import `AutoHealQA`.
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://autohealqa-backend.onrender.com/api/v1`
5. Click **Deploy**. Vercel will build Next.js 15 and issue a free SSL HTTPS domain (`https://autohealqa.vercel.app`).

---

## 🐳 Option B: One-Click Docker Compose Deployment

If deploying on a Cloud VPS (AWS EC2, DigitalOcean Droplet, Hetzner Ubuntu 24.04):

```bash
# 1. Clone repository
git clone https://github.com/your-username/AutoHealQA.git
cd AutoHealQA

# 2. Copy production environment file
cp .env.example .env

# 3. Add your production API keys in .env
nano .env

# 4. Launch full stack with Docker Compose
docker-compose up -d --build

# 5. Check container status
docker-compose ps
```

- Backend API: `http://your-server-ip:8000/docs`
- Frontend Dashboard: `http://your-server-ip:3000`

---

## 🔍 Verification & Health Check

1. Verify backend health endpoint:
   `curl https://autohealqa-backend.onrender.com/api/v1/health`
2. Open `https://autohealqa.vercel.app` in your browser.
3. Execute a test story on `https://www.saucedemo.com`.
4. Verify execution history & download PDF reports.
