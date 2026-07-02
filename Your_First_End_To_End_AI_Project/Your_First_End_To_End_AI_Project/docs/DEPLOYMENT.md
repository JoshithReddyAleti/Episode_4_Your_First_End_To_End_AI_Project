# 🚀 Deployment Guide

> How to give your project a URL.

---

## Option 1: Streamlit Cloud (Fastest — 5 minutes)

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repo → `app/ui/streamlit_app.py`
5. Add your `OPENAI_API_KEY` in the "Secrets" section:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
6. Click "Deploy"

Your app will be live at: `https://your-app.streamlit.app`

---

## Option 2: Railway

1. Push repo to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Add environment variable: `OPENAI_API_KEY`
5. Set start command: `streamlit run app/ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

---

## Option 3: Docker (For Production)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t ai-assistant .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-your-key ai-assistant
```

---

## Security Checklist Before Deploying

- [ ] `.env` is in `.gitignore` (never committed)
- [ ] No hardcoded API keys in source code (`git grep "sk-"`)
- [ ] API key is set via environment variables or platform secrets
- [ ] `requirements.txt` is up to date

---

*Back to [README](../README.md)*
