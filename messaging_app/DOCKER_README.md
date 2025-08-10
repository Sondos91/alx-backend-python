# Docker Setup for Messaging App

This document provides instructions for setting up and running the messaging app using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Open your browser and go to `http://localhost:8000`
   - The Django admin interface will be available at `http://localhost:8000/admin`

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker Commands

1. **Build the Docker image:**
   ```bash
   docker build -t messaging-app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 -v $(pwd):/app messaging-app
   ```

3. **Access the application:**
   - Open your browser and go to `http://localhost:8000`

## Project Structure

```
messaging_app/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .dockerignore          # Files to exclude from Docker build
├── manage.py              # Django management script
├── messaging_app/         # Django project settings
└── chats/                 # Django app
```

## Configuration

### Environment Variables

The following environment variables can be configured:

- `DEBUG`: Set to 1 for development, 0 for production
- `DJANGO_SETTINGS_MODULE`: Django settings module (default: messaging_app.settings)

### Port Configuration

The application runs on port 8000 by default. You can change this by modifying the `docker-compose.yml` file or the `EXPOSE` directive in the `Dockerfile`.

## Development

### Running Migrations

If you need to run migrations manually:

```bash
docker-compose exec web python manage.py migrate
```

### Creating Superuser

To create a Django superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

### Shell Access

To access the Django shell:

```bash
docker-compose exec web python manage.py shell
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change the port in `docker-compose.yml` (e.g., `"8001:8000"`)

2. **Permission issues:**
   - Ensure Docker has proper permissions to access the project directory

3. **Database issues:**
   - The app uses SQLite by default, which is included in the container
   - For production, consider using PostgreSQL or MySQL

### Logs

To view application logs:

```bash
docker-compose logs web
```

To follow logs in real-time:

```bash
docker-compose logs -f web
```

## Production Considerations

For production deployment:

1. Set `DEBUG=0` in environment variables
2. Use a production database (PostgreSQL/MySQL)
3. Configure proper static file serving
4. Set up HTTPS
5. Use environment variables for sensitive configuration
6. Consider using Docker secrets for sensitive data

## Cleanup

To remove all Docker resources:

```bash
docker-compose down -v --rmi all
docker system prune -f
```
