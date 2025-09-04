# Sample API Service

A sample API service generated for demonstration

## Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r ../shared/requirements.txt
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   python main.py
   ```

## Docker

Build and run with Docker:

```bash
docker build -t aurora-sample-api .
docker run -p 8888:8888 aurora-sample-api
```

Or use Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8888/docs
- ReDoc: http://localhost:8888/redoc

## Health Checks

- Basic health: http://localhost:8888/health
- Readiness: http://localhost:8888/health/ready
- Liveness: http://localhost:8888/health/live
