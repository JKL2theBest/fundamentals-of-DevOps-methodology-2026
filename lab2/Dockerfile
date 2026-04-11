# Этап 1: Сборщик (Builder)
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .


# Этап 2: Финальный образ (Production)
FROM python:3.11-slim-bullseye

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY --from=builder /app /app

RUN chown -R appuser:appgroup /app

USER appuser

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
