# Demo Service

Demo service for testing

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
docker build -t aurora-demo-service .
docker run -p 9998:9998 aurora-demo-service
```

Or use Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:9998/docs
- ReDoc: http://localhost:9998/redoc

## Health Checks

- Basic health: http://localhost:9998/health
- Readiness: http://localhost:9998/health/ready
- Liveness: http://localhost:9998/health/live
