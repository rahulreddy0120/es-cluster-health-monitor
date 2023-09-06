FROM python:3.11-slim

RUN groupadd -r monitor && useradd -r -g monitor -d /app monitor

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

RUN chown -R monitor:monitor /app
USER monitor

STOPSIGNAL SIGTERM

ENTRYPOINT ["python", "-m", "src.monitor"]
