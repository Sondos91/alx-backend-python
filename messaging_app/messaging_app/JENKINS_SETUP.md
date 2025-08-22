# Jenkins Pipeline Setup Guide

## Prerequisites
- Jenkins running in Docker container
- GitHub repository access
- Python 3.9+ available on Jenkins agent

## Jenkins Setup Steps

### 1. Access Jenkins Dashboard
- Open your browser and navigate to: http://localhost:8080
- Use the initial admin password: `648a8a14538548ec89711328d5fbccc1`

### 2. Install Required Plugins
After initial setup, install these plugins:
- **Git plugin** - For source code management
- **Pipeline** - For pipeline as code
- **ShiningPanda Plugin** - For Python support
- **HTML Publisher Plugin** - For test reports
- **JUnit Plugin** - For test results

### 3. Configure GitHub Credentials
1. Go to **Manage Jenkins** > **Manage Credentials**
2. Click on **Jenkins** > **Global credentials** > **Add Credentials**
3. Choose **SSH Username with private key** or **Username with password**
4. Add your GitHub credentials

### 4. Create New Pipeline Job
1. Click **New Item**
2. Enter job name (e.g., "messaging-app-pipeline")
3. Select **Pipeline**
4. Click **OK**

### 5. Configure Pipeline
1. In **Pipeline** section, select **Pipeline script from SCM**
2. Choose **Git** as SCM
3. Enter your repository URL: `https://github.com/yourusername/alx-backend-python.git`
4. Select credentials
5. Set branch to `*/main` or your default branch
6. Set script path to `messaging_app/Jenkinsfile`
7. Click **Save**

### 6. Run Pipeline
1. Click **Build Now** to trigger the pipeline manually
2. Monitor the build progress in the console output
3. View test reports and coverage reports after successful build

## Pipeline Features

The pipeline includes:
- **Checkout**: Pulls code from GitHub
- **Setup Python Environment**: Creates virtual environment
- **Install Dependencies**: Installs requirements and pytest
- **Run Tests**: Executes Django and pytest tests
- **Generate Reports**: Creates HTML coverage and test reports
- **Cleanup**: Removes temporary files

## Test Reports

After successful pipeline execution, you can view:
- **Coverage Report**: Shows code coverage statistics
- **Test Report**: Displays test execution results
- **JUnit Results**: Test results in Jenkins format

## Troubleshooting

### Common Issues:
1. **Python not found**: Ensure Python 3.9+ is installed on Jenkins agent
2. **Permission denied**: Check file permissions and Jenkins user access
3. **Dependencies fail**: Verify requirements.txt and network connectivity
4. **Tests fail**: Check Django settings and database configuration

### Manual Pipeline Trigger
To manually trigger the pipeline:
1. Go to your pipeline job
2. Click **Build Now**
3. Monitor the build in real-time
4. Check console output for any errors
