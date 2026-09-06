# Hugging Face Spaces deployment

Create a new Hugging Face Space with **Docker** as the SDK and connect this repository. The root `Dockerfile` serves both the React app and FastAPI API on port `7860`.

Add these Space secrets:

```text
DATABASE_URL=your_supabase_postgresql_url
LLM_PROVIDER=gemini
LLM_API_KEY=your_google_ai_studio_key
LLM_MODEL=gemini-1.5-flash
JWT_SECRET=generate_a_long_random_value
FRONTEND_ORIGIN=https://your-space-name-your-username.hf.space
VECTOR_STORE_PATH=./chroma_store
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

The container seeds the database and builds the Chroma index on startup. The free Space may sleep when idle, so the first request after inactivity can take a few minutes.