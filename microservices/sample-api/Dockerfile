# Dockerfile for sample-api
FROM microservices/shared:base

# Set service-specific environment variables
ENV SERVICE_NAME=sample-api \
    SERVICE_PORT=8888

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
EXPOSE 8888

# Run the service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]