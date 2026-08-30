# Deployment Guide: College Bot on Render (Backend) & Vercel (Frontend)

This guide provides step-by-step instructions for deploying the College Bot application to **Render** for the Python FastAPI backend and **Vercel** for the Web Frontend.

---

## 1. Deploying the Backend on Render (`render.com`)

### Option A: Automatic Blueprint Deployment (Recommended)

1. Push your repository to GitHub / GitLab.
2. Log into your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository.
5. Render will automatically detect `render.yaml` and provision the `college-bot-backend` Web Service.
6. Click **Apply**.
7. Once deployed, Render will provide a live URL (e.g. `https://college-bot-backend.onrender.com`).

### Option B: Manual Web Service Setup

1. Click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Set the following parameters:
   - **Name**: `college-bot-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Click **Create Web Service**.

---

## 2. Deploying the Frontend on Vercel (`vercel.com`)

### Option A: Vercel CLI (Quickest)

1. Open your terminal in the `frontend` folder:
   ```cmd
   cd frontend
   ```
2. Install Vercel CLI (if not already installed):
   ```cmd
   npm install -g vercel
   ```
3. Run deployment:
   ```cmd
   vercel
   ```
4. Follow the prompts (Root directory: `./`, framework: `Other` / `Vite`).
5. Run `vercel --prod` to deploy to production.

### Option B: Vercel Web Dashboard

1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Import your Git repository.
4. Set **Root Directory** to `frontend`.
5. Vercel will automatically detect `vercel.json` and Vite build configuration.
6. Click **Deploy**.

---

## 3. Connecting Frontend to Render Backend

Once both services are deployed:
1. Open your live Vercel frontend URL (e.g., `https://college-bot-frontend.vercel.app`).
2. Paste your Render backend URL (e.g., `https://college-bot-backend.onrender.com`) into the **Render API Endpoint** input box in the left sidebar.
3. Click **Save API Endpoint**. The indicator will switch to green (**Render API Connected**).
