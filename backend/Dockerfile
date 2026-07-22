FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
# docs/ is not backend code, but the M18 contract-test suite
# (contracts/tests/) reads docs/06-api-contracts.md as its source of
# truth rather than vendoring a copy that could drift from it independently.
COPY docs/ /app/docs/

RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
