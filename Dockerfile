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
CMD ["sh", "-c", "python -m scripts.seed_data && python -m scripts.embed_knowledge_base && uvicorn app.main:app --host 0.0.0.0 --port 7860"]