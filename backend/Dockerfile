FROM python:3.11-slim

WORKDIR /app

# Accept build-time environment (default to production)
ARG ENV=prod
ENV APP_ENV=$ENV
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

# Use APP_ENV to optionally switch behavior later if needed
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]