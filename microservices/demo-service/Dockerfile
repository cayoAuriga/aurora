# Dockerfile for demo-service
FROM microservices/shared:base

# Set service-specific environment variables
ENV SERVICE_NAME=demo-service \
    SERVICE_PORT=9998

# Copy service-specific requirements
COPY requirements.txt /app/service-requirements.txt

# Install service-specific dependencies
RUN pip install --no-cache-dir -r service-requirements.txt

# Copy service code
COPY . /app/

# Set ownership
USER root
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 9998

# Run the service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9998"]