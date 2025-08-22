# Docker Build and Deploy Setup

This document explains how to set up the Docker build and deploy workflow for the messaging app.

## Prerequisites

1. **Docker Hub Account** - You need a Docker Hub account
2. **Docker Hub Access Token** - Generate a personal access token
3. **GitHub Repository** - Your code must be in a GitHub repository

## Setup Steps

### 1. Generate Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/) and sign in
2. Click on your username → **Account Settings**
3. Go to **Security** → **New Access Token**
4. Give it a name (e.g., "GitHub Actions")
5. Copy the generated token (you won't see it again!)

### 2. Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Your Docker Hub access token |

### 3. Update Image Name

In the `.github/workflows/dep.yml` file, update the `IMAGE_NAME` environment variable:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: yourusername/messaging-app  # Change this!
```

Replace `yourusername` with your actual Docker Hub username and `messaging-app` with your desired image name.

### 4. Verify Dockerfile

Ensure you have a valid `Dockerfile` in your repository root. The workflow expects it at `./Dockerfile`.

## Workflow Features

### **Triggers:**
- **Push** to main/master/develop branches
- **Pull requests** to main/master/develop branches
- **Tags** starting with 'v' (e.g., v1.0.0)
- **Manual trigger** with custom image tag

### **Jobs:**

#### 1. **Build and Push**
- Sets up Docker Buildx for multi-platform builds
- Logs into Docker Hub using secrets
- Builds Docker image with metadata
- Pushes to Docker Hub with multiple tags
- Supports Linux AMD64 and ARM64 architectures

#### 2. **Test Deployment** (Main branch only)
- Pulls the built image
- Tests container startup
- Verifies container is running
- Cleans up test containers

#### 3. **Security Scan** (Main branch only)
- Runs Trivy vulnerability scanner
- Uploads results to GitHub Security tab
- Provides security scan summary

### **Image Tagging Strategy:**
- `latest` - For main branch pushes
- `branch-name` - For feature branch pushes
- `v1.0.0` - For semantic version tags
- `sha-abc123` - For commit-based tags

## Usage Examples

### **Automatic Builds:**
- Push to main branch → Builds and pushes `latest` tag
- Push to feature branch → Builds and pushes `feature-name` tag
- Create tag `v1.0.0` → Builds and pushes `v1.0.0` tag

### **Manual Build:**
1. Go to **Actions** tab in your repository
2. Select **Docker Build and Deploy** workflow
3. Click **Run workflow**
4. Enter custom image tag (optional)
5. Click **Run workflow**

## Troubleshooting

### **Common Issues:**

1. **Authentication Failed**
   - Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
   - Ensure token has write permissions

2. **Build Failed**
   - Check if `Dockerfile` exists in repository root
   - Verify Dockerfile syntax

3. **Push Failed**
   - Ensure Docker Hub repository exists
   - Check if you have write permissions

### **Debug Steps:**
1. Check workflow logs in GitHub Actions
2. Verify secrets are set correctly
3. Test Docker build locally first
4. Check Docker Hub repository permissions

## Security Features

- **Secrets Management** - Credentials stored securely in GitHub
- **Vulnerability Scanning** - Trivy scans for security issues
- **Multi-platform Support** - AMD64 and ARM64 architectures
- **Cache Optimization** - GitHub Actions cache for faster builds

## Next Steps

1. **Set up secrets** as described above
2. **Update image name** in the workflow
3. **Push changes** to trigger the workflow
4. **Monitor builds** in the Actions tab
5. **Check Docker Hub** for your published images

## Support

If you encounter issues:
1. Check the workflow logs
2. Verify your setup matches this guide
3. Ensure all prerequisites are met
4. Check GitHub Actions documentation
