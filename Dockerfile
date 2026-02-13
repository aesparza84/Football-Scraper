FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium
CMD ["uvicorn", "PlaywrightScrape:app", "--host", "0.0.0.0", "--port", "8000"]