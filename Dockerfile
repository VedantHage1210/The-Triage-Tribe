FROM node:20-alpine AS frontend-build
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_URL=/api
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-build /workspace/frontend/dist ./frontend_dist/
WORKDIR /app/backend

EXPOSE 7860
# Data init runs to completion FIRST, then uvicorn starts — sequential,
# not concurrent. Running these at the same time (the old setup) doubles
# peak memory during boot: FastAPI's own startup overlapping with
# sentence-transformers loading its embedding model into RAM. On a
# memory-constrained host that combination was enough to trigger an OOM
# kill before uvicorn ever printed its startup banner, causing an
# endless restart→re-embed→OOM loop. Running them one at a time keeps
# peak memory lower at the cost of a slightly longer boot.
CMD ["sh", "-c", "(python -m scripts.seed_data && python -m scripts.embed_knowledge_base) || echo 'Data initialization failed; starting API anyway'; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]