#!/bin/bash

# setup-ingress.sh - Automated Kubernetes Ingress Setup Script
# Objective: Install Nginx Ingress controller and configure Ingress for Django app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INGRESS_NAMESPACE="ingress-nginx"
INGRESS_RELEASE="ingress-nginx"
INGRESS_CHART="ingress-nginx/ingress-nginx"

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}==========================================${NC}"
    echo -e "${PURPLE}    $1${NC}"
    echo -e "${PURPLE}==========================================${NC}"
    echo ""
}

print_subheader() {
    echo -e "${CYAN}--- $1 ---${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check kubectl
    if ! command_exists kubectl; then
        print_error "kubectl is not installed!"
        exit 1
    fi
    print_success "kubectl found: $(kubectl version --client --short)"
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster!"
        exit 1
    fi
    print_success "Connected to Kubernetes cluster"
    
    # Check Helm
    if ! command_exists helm; then
        print_warning "Helm is not installed. Installing Helm..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install helm
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        else
            print_error "Please install Helm manually for your OS"
            exit 1
        fi
    fi
    print_success "Helm found: $(helm version --short)"
}

# Function to install Nginx Ingress controller
install_ingress_controller() {
    print_header "Installing Nginx Ingress Controller"
    
    # Add Helm repository
    print_status "Adding Helm repository..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install Ingress controller
    print_status "Installing Ingress controller..."
    helm install $INGRESS_RELEASE $INGRESS_CHART \
        --namespace $INGRESS_NAMESPACE \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.ingressClassResource.default=true
    
    if [ $? -eq 0 ]; then
        print_success "Ingress controller installed successfully!"
    else
        print_error "Failed to install Ingress controller!"
        exit 1
    fi
}

# Function to wait for Ingress controller to be ready
wait_for_ingress_controller() {
    print_header "Waiting for Ingress Controller to be Ready"
    
    print_status "Waiting for Ingress controller pods to be ready..."
    kubectl wait --namespace $INGRESS_NAMESPACE \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    if [ $? -eq 0 ]; then
        print_success "Ingress controller is ready!"
    else
        print_error "Ingress controller failed to become ready!"
        exit 1
    fi
}

# Function to check Ingress controller status
check_ingress_controller_status() {
    print_header "Checking Ingress Controller Status"
    
    print_subheader "Pods Status"
    kubectl get pods -n $INGRESS_NAMESPACE
    
    print_subheader "Services Status"
    kubectl get services -n $INGRESS_NAMESPACE
    
    print_subheader "Deployments Status"
    kubectl get deployments -n $INGRESS_NAMESPACE
}

# Function to apply Ingress configuration
apply_ingress_config() {
    print_header "Applying Ingress Configuration"
    
    print_status "Applying Ingress resource..."
    kubectl apply -f ingress.yaml
    
    if [ $? -eq 0 ]; then
        print_success "Ingress configuration applied successfully!"
    else
        print_error "Failed to apply Ingress configuration!"
        exit 1
    fi
}

# Function to verify Ingress setup
verify_ingress_setup() {
    print_header "Verifying Ingress Setup"
    
    print_subheader "Ingress Resources"
    kubectl get ingress
    
    print_subheader "Ingress Details"
    kubectl describe ingress messaging-app-ingress
    
    print_subheader "Ingress Controller Logs"
    kubectl logs -n $INGRESS_NAMESPACE -l app.kubernetes.io/component=controller --tail=20
}

# Function to test Ingress endpoints
test_ingress_endpoints() {
    print_header "Testing Ingress Endpoints"
    
    # Check if we're using minikube
    if command_exists minikube && minikube status &> /dev/null; then
        print_status "Using minikube tunnel for testing..."
        
        # Start minikube tunnel in background
        print_status "Starting minikube tunnel..."
        minikube tunnel &
        TUNNEL_PID=$!
        sleep 15
        
        # Test endpoints
        print_subheader "Testing Health Endpoint"
        curl -s -H "Host: messaging-app.local" http://localhost/health/ || print_warning "Health endpoint test failed"
        
        print_subheader "Testing API Endpoint"
        curl -s -H "Host: messaging-app.local" http://localhost/chats/ || print_warning "API endpoint test failed"
        
        # Stop tunnel
        kill $TUNNEL_PID 2>/dev/null || true
    else
        print_warning "minikube not detected. Manual testing required."
        print_status "Use these commands to test:"
        echo "  curl -H 'Host: messaging-app.local' http://<EXTERNAL-IP>/health/"
        echo "  curl -H 'Host: messaging-app.local' http://<EXTERNAL-IP>/chats/"
    fi
}

# Function to show Ingress information
show_ingress_info() {
    print_header "Ingress Information"
    
    print_subheader "External IP/Port"
    kubectl get service -n $INGRESS_NAMESPACE
    
    print_subheader "Ingress Rules"
    kubectl get ingress messaging-app-ingress -o yaml | grep -A 20 "rules:"
    
    print_subheader "Available Endpoints"
    echo "  - http://messaging-app.local/ (Root)"
    echo "  - http://messaging-app.local/api/ (API)"
    echo "  - http://messaging-app.local/chats/ (Chats)"
    echo "  - http://messaging-app.local/admin/ (Admin)"
    echo "  - http://messaging-app.local/health/ (Health Check)"
}

# Function to show help
show_help() {
    echo "setup-ingress.sh - Automated Kubernetes Ingress Setup"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  (no args)  Full Ingress setup and configuration"
    echo "  install     Install Ingress controller only"
    echo "  configure   Apply Ingress configuration only"
    echo "  verify      Verify Ingress setup"
    echo "  test        Test Ingress endpoints"
    echo "  status      Show Ingress status"
    echo "  info        Show Ingress information"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Run full setup"
    echo "  $0 install   # Install controller only"
    echo "  $0 test      # Test endpoints only"
}

# Main execution
main() {
    print_header "Kubernetes Ingress Setup"
    
    # Check prerequisites
    check_prerequisites
    
    # Install Ingress controller
    install_ingress_controller
    
    # Wait for controller to be ready
    wait_for_ingress_controller
    
    # Check status
    check_ingress_controller_status
    
    # Apply Ingress configuration
    apply_ingress_config
    
    # Verify setup
    verify_ingress_setup
    
    # Test endpoints
    test_ingress_endpoints
    
    # Show information
    show_ingress_info
    
    print_success "Ingress setup completed successfully!"
    print_status "Your Django app is now accessible via Ingress!"
    print_status "Use 'kubectl get ingress' to check status"
}

# Handle command line arguments
case "${1:-}" in
    "install")
        check_prerequisites
        install_ingress_controller
        wait_for_ingress_controller
        check_ingress_controller_status
        ;;
    "configure")
        check_prerequisites
        apply_ingress_config
        verify_ingress_setup
        ;;
    "verify")
        check_prerequisites
        verify_ingress_setup
        ;;
    "test")
        check_prerequisites
        test_ingress_endpoints
        ;;
    "status")
        check_prerequisites
        check_ingress_controller_status
        verify_ingress_setup
        ;;
    "info")
        check_prerequisites
        show_ingress_info
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
