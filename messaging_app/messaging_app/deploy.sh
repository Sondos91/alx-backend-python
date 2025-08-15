#!/bin/bash

# Kubernetes Deployment Script for Django Messaging App
# This script builds the Docker image and deploys it to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    print_success "kubectl found: $(kubectl version --client --short)"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t messaging-app:latest .
    print_success "Docker image built successfully"
}

# Load image into minikube (if using minikube)
load_image_to_minikube() {
    if command -v minikube &> /dev/null && minikube status &> /dev/null; then
        print_status "Loading image into minikube..."
        minikube image load messaging-app:latest
        print_success "Image loaded into minikube"
    else
        print_warning "minikube not found or not running, skipping image load"
    fi
}

# Create secrets (you need to update these values)
create_secrets() {
    print_status "Creating Kubernetes secrets..."
    
    # Generate a random secret key if not provided
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    MYSQL_PASSWORD="messaging_password_123"
    MYSQL_ROOT_PASSWORD="root_password_123"
    
    # Create the secret
    kubectl create secret generic django-secret \
        --from-literal=SECRET_KEY="$SECRET_KEY" \
        --from-literal=MYSQL_PASSWORD="$MYSQL_PASSWORD" \
        --from-literal=MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Secrets created successfully"
}

# Deploy to Kubernetes
deploy() {
    print_status "Deploying to Kubernetes..."
    
    # Apply the deployment
    kubectl apply -f deployment.yaml
    
    print_success "Deployment applied successfully"
}

# Wait for deployment to be ready
wait_for_deployment() {
    print_status "Waiting for deployment to be ready..."
    
    kubectl wait --for=condition=available --timeout=300s deployment/messaging-app
    kubectl wait --for=condition=available --timeout=300s deployment/mysql-db
    
    print_success "All deployments are ready!"
}

# Show deployment status
show_status() {
    print_status "Deployment status:"
    echo ""
    
    print_status "Pods:"
    kubectl get pods -l app=messaging-app
    kubectl get pods -l app=mysql-db
    
    echo ""
    print_status "Services:"
    kubectl get services -l app=messaging-app
    kubectl get services -l app=mysql-db
    
    echo ""
    print_status "Deployments:"
    kubectl get deployments -l app=messaging-app
    kubectl get deployments -l app=mysql-db
}

# Show logs
show_logs() {
    print_status "Showing logs for messaging app pods..."
    
    PODS=$(kubectl get pods -l app=messaging-app -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $PODS; do
        echo ""
        print_status "Logs for pod: $pod"
        echo "----------------------------------------"
        kubectl logs $pod --tail=20
    done
}

# Main execution
main() {
    echo "=========================================="
    echo "    Kubernetes Deployment Script"
    echo "=========================================="
    echo ""
    
    # Check prerequisites
    check_kubectl
    check_docker
    
    # Build and deploy
    build_image
    load_image_to_minikube
    create_secrets
    deploy
    wait_for_deployment
    
    # Show results
    show_status
    show_logs
    
    echo ""
    print_success "Deployment completed successfully!"
    print_status "Your Django app is now running on Kubernetes!"
    print_status "Use 'kubectl get pods' to check status"
    print_status "Use 'kubectl logs <pod-name>' to view logs"
}

# Handle command line arguments
case "${1:-}" in
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Full deployment"
        echo "  status      Show deployment status"
        echo "  logs        Show application logs"
        echo "  help        Show this help message"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
