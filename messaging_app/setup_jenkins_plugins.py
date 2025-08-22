#!/usr/bin/env python3
"""
Jenkins Plugin Installation Helper Script
This script helps install required plugins for the messaging app pipeline
"""

import requests
import json
import time
import sys

def install_jenkins_plugins():
    """Install required Jenkins plugins"""
    
    # Jenkins base URL
    jenkins_url = "http://localhost:8080"
    
    # Required plugins for the messaging app pipeline
    required_plugins = [
        "git",
        "workflow-aggregator",  # Pipeline plugin
        "shiningpanda",         # Python support
        "htmlpublisher",        # HTML reports
        "junit"                 # Test results
    ]
    
    print("Jenkins Plugin Installation Helper")
    print("=" * 40)
    print(f"Jenkins URL: {jenkins_url}")
    print("\nRequired plugins:")
    for plugin in required_plugins:
        print(f"  - {plugin}")
    
    print("\nTo install these plugins:")
    print("1. Open your browser and go to:", jenkins_url)
    print("2. Use the initial admin password: 648a8a14538548ec89711328d5fbccc1")
    print("3. Complete the initial setup")
    print("4. Go to Manage Jenkins > Manage Plugins")
    print("5. Install the following plugins:")
    
    for plugin in required_plugins:
        print(f"   - {plugin}")
    
    print("\nAfter plugin installation:")
    print("1. Restart Jenkins when prompted")
    print("2. Create a new Pipeline job")
    print("3. Configure it to use the Jenkinsfile from your repository")
    print("4. Set up GitHub credentials")
    print("5. Run the pipeline manually using 'Build Now'")

if __name__ == "__main__":
    install_jenkins_plugins()
