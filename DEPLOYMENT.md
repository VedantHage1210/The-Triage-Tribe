# Free deployment guide

The recommended hackathon setup is:

- Frontend: Vercel
- Backend: Render Web Service
- Database: Supabase PostgreSQL free project
- LLM: Google AI Studio Gemini API free tier

## 1. Create the database

1. Create a free project at https://supabase.com.
2. Open **Connect** and copy the direct PostgreSQL connection string.
3. Replace the password placeholder in the connection string.
4. Keep the connection string ready as `DATABASE_URL`.

Use the direct connection string for this project because SQLAlchemy and `psycopg2` already expect PostgreSQL.

## 2. Deploy the backend on Render

1. Open https://render.com and sign in with GitHub.
2. Select **New > Blueprint** and choose `VedantHage1210/The-Triage-Tribe`.
3. Render detects the root `render.yaml` file.
4. Set these secret values when prompted:
   - `DATABASE_URL`: Supabase PostgreSQL URL
   - `LLM_API_KEY`: Google AI Studio API key
   - `FRONTEND_ORIGIN`: temporary value `https://example.com` for the first deploy
5. Deploy and wait for the health check to pass.
6. Verify `https://YOUR-RENDER-SERVICE.onrender.com/api/health` returns `{"status":"ok"}`.

The first deployment can take several minutes because the embedding model is downloaded and the seed data is embedded during startup. Render's free service may sleep when idle; the first request after sleeping can be slow.

## 3. Deploy the frontend on Vercel

1. Open https://vercel.com and sign in with GitHub.
2. Select **Add New > Project** and import `The-Triage-Tribe`.
3. Set **Root Directory** to `frontend`.
4. Keep the detected Vite settings:
   - Build command: `npm run build`
   - Output directory: `dist`
5. Add this environment variable:
   - `VITE_API_URL`: `https://YOUR-RENDER-SERVICE.onrender.com/api`
6. Deploy and copy the Vercel URL.

The included `frontend/vercel.json` keeps React Router routes working on refresh.

## 4. Lock CORS to the frontend

Return to Render environment variables and replace `FRONTEND_ORIGIN` with the exact Vercel URL, for example:

```text
https://the-triage-tribe.vercel.app
```

Redeploy the backend after saving the variable.

## 5. Create the admin account

After the backend is deployed, open the Render Shell and run:

```bash
python -m scripts.create_admin admin@example.com CHANGE_THIS_PASSWORD
```

Use that account at `/admin/login` on the Vercel URL.

## 6. Judge smoke test

1. Open the Vercel URL.
2. Run the Safety Lab scenarios on the home page.
3. Test **Heart / Cardiac** with `I have chest pain and cannot breathe`.
4. Test **Eyes** with `My eye is red and itchy for two days`.
5. Switch to German and repeat one scenario.
6. Verify the PDF report and admin login.

Do not commit `.env` files or API keys. Rotate any key immediately if it is accidentally exposed.
