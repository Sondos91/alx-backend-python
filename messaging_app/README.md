# Django Messaging App 🚀

A modern, real-time messaging application built with Django, Django REST Framework, and JWT authentication. This project demonstrates advanced Django concepts including custom user models, real-time messaging, authentication, and Docker deployment.

## 🏗️ Project Overview

This messaging app is built upon the week 4 Django project and includes:

- **Custom User Model** - Extended user model with additional fields
- **Real-time Messaging** - Chat functionality between users
- **JWT Authentication** - Secure token-based authentication
- **RESTful API** - Complete API endpoints for all functionality
- **Docker Support** - Containerized deployment ready
- **MySQL Database** - Production-ready database configuration

## 🚀 Quick Start

### Prerequisites

- **Docker** installed on your system
- **Docker Compose** installed on your system
- **Operating System**: Ubuntu 20.20 (or compatible)

### Running the Project

1. **Clone and navigate to the project:**
   ```bash
   cd messaging_app
   ```

2. **Start the application with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access your application:**
   - **Main App**: http://localhost:8000
   - **API Endpoints**: http://localhost:8000/api/
   - **Admin Interface**: http://localhost:8000/admin/

## 🐳 Docker Setup

### Project Structure

```
messaging_app/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .dockerignore          # Files to exclude from Docker build
├── manage.py              # Django management script
├── messaging_app/         # Django project settings
├── chats/                 # Django app with models and views
└── mysql/                 # Database initialization scripts
```

### Docker Commands

#### Option 1: Docker Compose (Recommended)
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs web

# Stop the application
docker-compose down

# Rebuild and start
docker-compose up --build
```

#### Option 2: Docker Commands
```bash
# Build the Docker image
docker build -t messaging-app .

# Run the container
docker run -d -p 8000:8000 --name messaging-app-container messaging-app

# Stop the container
docker stop messaging-app-container

# Remove the container
docker rm messaging-app-container
```

## 🛠️ Development

### Running Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Creating Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### Django Shell Access
```bash
docker-compose exec web python manage.py shell
```

### Collecting Static Files
```bash
docker-compose exec web python manage.py collectstatic
```

## 🔧 Configuration

### Environment Variables

The following environment variables are configured in docker-compose.yml:

- `DEBUG` - Django debug mode
- `SECRET_KEY` - Django secret key
- `DJANGO_SETTINGS_MODULE` - Django settings module
- `MYSQL_DATABASE` - Database name
- `MYSQL_DB` - Additional database variable
- `MYSQL_USER` - Database user
- `MYSQL_PASSWORD` - Database password
- `MYSQL_HOST` - Database host
- `MYSQL_PORT` - Database port
- `MYSQL_ROOT_PASSWORD` - Root password

### Port Configuration

- **Web Application**: Port 8000
- **MySQL Database**: Port 3306

## 📱 API Endpoints

The application provides RESTful API endpoints for:

- **Authentication**: JWT-based login/logout
- **Users**: User management and profiles
- **Chats**: Real-time messaging functionality
- **Messages**: Message creation and retrieval

## 🗄️ Database

- **Database**: MySQL 8.0
- **Authentication**: mysql_native_password
- **Initialization**: Automatic setup with init scripts
- **Persistence**: Docker volumes for data storage

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Permission issues:**
   - Ensure Docker has proper permissions
   - Check file ownership in the project directory

3. **Database connection issues:**
   - Verify MySQL service is running: `docker-compose ps db`
   - Check database logs: `docker-compose logs db`

### Logs and Debugging

```bash
# View web service logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web

# View database logs
docker-compose logs db

# Check container status
docker-compose ps
```

## 🧹 Cleanup

### Remove All Docker Resources
```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v --rmi all

# Clean up unused Docker resources
docker system prune -f
```

## 📚 Additional Documentation

- **DOCKER_README.md** - Detailed Docker setup instructions
- **DOCKER_SETUP_COMPLETE.md** - Setup completion status
- **Postman Collections** - API testing examples

## 🎯 Features

- ✅ **User Authentication** - JWT-based secure authentication
- ✅ **Real-time Messaging** - Chat functionality between users
- ✅ **RESTful API** - Complete API with Django REST Framework
- ✅ **Custom User Model** - Extended user functionality
- ✅ **Docker Deployment** - Production-ready containerization
- ✅ **MySQL Database** - Scalable database backend
- ✅ **Admin Interface** - Django admin for management

## 🚀 Production Deployment

For production use:

1. Set `DEBUG=0` in environment variables
2. Use strong, unique secret keys
3. Configure HTTPS/SSL
4. Set up proper logging
5. Use environment variables for sensitive data
6. Consider using Docker secrets

## 📞 Support

This project is part of the ALX Backend Python curriculum. For issues or questions:

1. Check the troubleshooting section above
2. Review Docker logs for error messages
3. Ensure all prerequisites are met
4. Verify Docker and Docker Compose versions

---

**Happy Coding! 🎉**

*Built with Django, Docker, and ❤️*
