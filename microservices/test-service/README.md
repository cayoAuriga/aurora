# Test Service

Service for testing shared libraries

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
docker build -t aurora-test-service .
docker run -p 8999:8999 aurora-test-service
```

Or use Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8999/docs
- ReDoc: http://localhost:8999/redoc

## Health Checks

- Basic health: http://localhost:8999/health
- Readiness: http://localhost:8999/health/ready
- Liveness: http://localhost:8999/health/live
