#!/usr/bin/env python3
"""
Service generator script for Aurora microservices
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any


def generate_service(
    service_name: str,
    service_port: int,
    service_title: str = None,
    service_description: str = None,
    db_name: str = None
):
    """
    Generate a new microservice from templates
    
    Args:
        service_name: Name of the service (e.g., 'user-service')
        service_port: Port number for the service
        service_title: Human-readable title
        service_description: Service description
        db_name: Database name (defaults to service_name with underscores)
    """
    
    # Set defaults
    if not service_title:
        service_title = service_name.replace('-', ' ').title()
    
    if not service_description:
        service_description = f"Aurora {service_title} microservice"
    
    if not db_name:
        db_name = service_name.replace('-', '_') + '_db'
    
    # Template variables
    template_vars = {
        'SERVICE_NAME': service_name,
        'SERVICE_PORT': str(service_port),
        'SERVICE_TITLE': service_title,
        'SERVICE_DESCRIPTION': service_description,
        'DB_NAME': db_name
    }
    
    # Paths
    microservices_dir = Path(__file__).parent.parent
    templates_dir = microservices_dir / 'shared' / 'templates'
    service_dir = microservices_dir / service_name
    
    # Create service directory
    service_dir.mkdir(exist_ok=True)
    
    # Generate files from templates
    template_files = [
        ('service_template.py', 'main.py'),
        ('Dockerfile.template', 'Dockerfile'),
        ('docker-compose.service.yml', 'docker-compose.yml')
    ]
    
    for template_file, output_file in template_files:
        template_path = templates_dir / template_file
        output_path = service_dir / output_file
        
        if template_path.exists():
            # Read template
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Replace template variables
            for var, value in template_vars.items():
                content = content.replace(f'{{{{{var}}}}}', value)
            
            # Write output file
            with open(output_path, 'w') as f:
                f.write(content)
            
            print(f"Generated: {output_path}")
    
    # Create additional directories and files
    directories = [
        'models',
        'schemas',
        'repositories',
        'services',
        'routers',
        'tests'
    ]
    
    for directory in directories:
        dir_path = service_dir / directory
        dir_path.mkdir(exist_ok=True)
        
        # Create __init__.py files
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text('')
    
    # Create requirements.txt
    requirements_path = service_dir / 'requirements.txt'
    if not requirements_path.exists():
        requirements_content = """# Service-specific requirements
# Add any additional dependencies here

# Example:
# requests==2.31.0
# pillow==10.1.0
"""
        requirements_path.write_text(requirements_content)
    
    # Create .env.example
    env_example_path = service_dir / '.env.example'
    if not env_example_path.exists():
        env_content = f"""# Environment variables for {service_name}

# Service configuration
SERVICE_NAME={service_name}
SERVICE_PORT={service_port}
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database configuration
DB_HOST=localhost
DB_PORT=4000
DB_USERNAME=root
DB_PASSWORD=your_password
DB_DATABASE={db_name}
DB_SSL_CA=ca-cert.pem
DB_SSL_DISABLED=false

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Service URLs
API_GATEWAY_URL=http://localhost:8000
SUBJECT_SERVICE_URL=http://localhost:8002
SYLLABUS_SERVICE_URL=http://localhost:8001
FILE_SERVICE_URL=http://localhost:8003
CONFIG_SERVICE_URL=http://localhost:8004

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
"""
        env_example_path.write_text(env_content)
    
    # Create README.md
    readme_path = service_dir / 'README.md'
    if not readme_path.exists():
        readme_content = f"""# {service_title}

{service_description}

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
docker build -t aurora-{service_name} .
docker run -p {service_port}:{service_port} aurora-{service_name}
```

Or use Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:{service_port}/docs
- ReDoc: http://localhost:{service_port}/redoc

## Health Checks

- Basic health: http://localhost:{service_port}/health
- Readiness: http://localhost:{service_port}/health/ready
- Liveness: http://localhost:{service_port}/health/live
"""
        readme_path.write_text(readme_content)
    
    print(f"\n[SUCCESS] Service '{service_name}' generated successfully!")
    print(f"Location: {service_dir}")
    print(f"Port: {service_port}")
    print(f"\nNext steps:")
    print(f"1. cd {service_dir}")
    print(f"2. cp .env.example .env")
    print(f"3. Edit .env with your configuration")
    print(f"4. python main.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Aurora microservice")
    parser.add_argument("service_name", help="Service name (e.g., user-service)")
    parser.add_argument("service_port", type=int, help="Service port number")
    parser.add_argument("--title", help="Service title")
    parser.add_argument("--description", help="Service description")
    parser.add_argument("--db-name", help="Database name")
    
    args = parser.parse_args()
    
    generate_service(
        service_name=args.service_name,
        service_port=args.service_port,
        service_title=args.title,
        service_description=args.description,
        db_name=args.db_name
    )