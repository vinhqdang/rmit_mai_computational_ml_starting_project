#!/usr/bin/env python3
"""
RMIT ML Course - Exchange Rate Predictor Runner
Simple script to start the application with proper setup
"""

import os
import sys
import subprocess
import json

def check_config():
    """Check if config.json exists and is properly configured"""
    if not os.path.exists('config.json'):
        print("❌ config.json not found!")
        print("📝 Please copy config.json.example to config.json and add your API key")
        print("🔗 Get your free API key from: https://www.exchangerate-api.com/")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        if config.get('api_key') == 'your_exchangerate_api_key_here':
            print("❌ Please update your API key in config.json")
            print("🔗 Get your free API key from: https://www.exchangerate-api.com/")
            return False
        
        print("✅ Configuration looks good!")
        return True
    except Exception as e:
        print(f"❌ Error reading config.json: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        import plotly
        import requests
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Run: pip install -r requirements.txt")
        return False

def main():
    """Main runner function"""
    print("🚀 RMIT ML Course - Exchange Rate Predictor")
    print("=" * 50)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    print("✅ Directories created!")
    
    print("\n🌐 Starting Flask application...")
    print("📱 Open your browser to: http://localhost:5000")
    print("👤 Use demo credentials shown on the homepage")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()