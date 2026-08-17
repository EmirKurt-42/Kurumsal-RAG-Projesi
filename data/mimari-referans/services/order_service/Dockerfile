FROM python:3.12-slim

# Containers should not run as root.
RUN useradd --create-home appuser
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "order_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
