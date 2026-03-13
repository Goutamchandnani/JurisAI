# Deploying JurisAI (Professional Architecture)

Since we have split the app into a Backend and Frontend, follow these steps to go live.

## 1. Deploy the Backend (Render)
1. Go to [Render](https://render.com/) and create a **New Web Service**.
2. Connect your GitHub repository.
3. **Build Command**: `pip install -r backend/requirements.txt`
4. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   * `GEMINI_API_KEY`: [Your Key]
   * `CHUNK_SIZE`: 1000
   * `CHUNK_OVERLAP`: 200
   * `TOP_K_RESULTS`: 5
   * `PYTHONPATH`: `backend`

## 2. Deploy the Frontend (Vercel)
1. Go to [Vercel](https://vercel.com/) and create a **New Project**.
2. Connect your GitHub repository.
3. **Framework Preset**: Next.js.
4. **Root Directory**: `frontend`.
5. **Environment Variables**:
   * `NEXT_PUBLIC_BACKEND_URL`: [The URL Render gave you, e.g., https://jurisai-backend.onrender.com]
6. Click **Deploy**.

---

## Technical Features
- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion, Axios.
- **Backend**: FastAPI, ChromaDB, Google Gemini Pro (Text + Embedding).
- **Security**: CORS enabled, Secrets managed via Cloud Dashboards.
