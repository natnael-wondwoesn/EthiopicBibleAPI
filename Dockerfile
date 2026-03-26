FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# MODE controls what runs: "api", "bot", or "both" (default)
ENV MODE=both
ENV TELEGRAM_BOT_TOKEN=""

EXPOSE 8000

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
