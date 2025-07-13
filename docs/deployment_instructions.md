# 🚀 Deployment Instructions: Production Setup & Maintenance

**دليل النشر والصيانة | Production Deployment and Maintenance Guide**

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Azure Environment Setup](#azure-environment-setup)
3. [Configuration Management](#configuration-management)
4. [Database Setup](#database-setup)
5. [Security Configuration](#security-configuration)
6. [Monitoring and Logging](#monitoring-logging)
7. [Performance Optimization](#performance-optimization)
8. [Backup and Recovery](#backup-recovery)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Troubleshooting Guide](#troubleshooting-guide)

## 📋 Pre-Deployment Checklist

### Essential Requirements
- [ ] Azure subscription with sufficient credits
- [ ] OpenAI API key with GPT-4o access
- [ ] Anthropic API key with Claude Opus access
- [ ] Azure Speech Services subscription
- [ ] Domain name and SSL certificate
- [ ] Database setup (Azure SQL Database)
- [ ] Redis cache configuration
- [ ] GitHub repository access

### API Keys and Services
```bash
# Required API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus

# Optional but Recommended
AZURE_SUBSCRIPTION_ID=...
AZURE_RESOURCE_GROUP=omani-mental-health-rg
```

### System Requirements
- **Python Version**: 3.8+
- **Memory**: Minimum 4GB RAM
- **Storage**: 20GB available space
- **Network**: Stable internet connection
- **SSL Certificate**: Valid HTTPS certificate

## ☁️ Azure Environment Setup

### 1. Resource Group Creation
```bash
# Create resource group
az group create \
  --name omani-mental-health-rg \
  --location eastus

# Verify creation
az group show --name omani-mental-health-rg
```

### 2. App Service Plan Configuration
```bash
# Create App Service Plan
az appservice plan create \
  --name omani-mental-health-plan \
  --resource-group omani-mental-health-rg \
  --sku B2 \
  --is-linux

# Scale plan if needed
az appservice plan update \
  --name omani-mental-health-plan \
  --resource-group omani-mental-health-rg \
  --sku P1V2
```

### 3. Web App Creation
```bash
# Create Web App
az webapp create \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --plan omani-mental-health-plan \
  --runtime "PYTHON|3.9"

# Configure startup command
az webapp config set \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --startup-file startup.sh
```

### 4. Database Setup
```bash
# Create Azure SQL Database
az sql server create \
  --name omani-mental-health-db-server \
  --resource-group omani-mental-health-rg \
  --location eastus \
  --admin-user dbadmin \
  --admin-password SecurePassword123!

# Create database
az sql db create \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --name omani-mental-health-db \
  --service-objective S1
```

### 5. Redis Cache Configuration
```bash
# Create Redis Cache
az redis create \
  --name omani-mental-health-cache \
  --resource-group omani-mental-health-rg \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

## ⚙️ Configuration Management

### Environment Variables Setup
```bash
# Set application settings
az webapp config appsettings set \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --settings \
    OPENAI_API_KEY="your_openai_key" \
    ANTHROPIC_API_KEY="your_anthropic_key" \
    AZURE_SPEECH_KEY="your_speech_key" \
    AZURE_SPEECH_REGION="eastus" \
    MAX_RESPONSE_TIME="15" \
    ENABLE_CRISIS_DETECTION="true" \
    PRIMARY_LANGUAGE="ar-OM" \
    CULTURAL_CONTEXT="gulf_arab" \
    THERAPEUTIC_APPROACH="cbt_islamic"
```

### Database Connection String
```bash
# Configure database connection
az webapp config connection-string set \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --connection-string-type SQLServer \
  --settings DefaultConnection="Server=tcp:omani-mental-health-db-server.database.windows.net,1433;Database=omani-mental-health-db;User ID=dbadmin;Password=SecurePassword123!;Encrypt=True;Connection Timeout=30;"
```

### Application Configuration File
```python
# config/production.py
import os

class ProductionConfig:
    """Production configuration"""
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://omani-mental-health-cache.redis.cache.windows.net:6380')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/omani-mental-health.log'
    
    # Performance
    MAX_WORKERS = 4
    TIMEOUT = 30
    
    # Security
    SSL_REQUIRED = True
    HTTPS_ONLY = True
```

## 🔒 Security Configuration

### SSL Certificate Setup
```bash
# Upload SSL certificate
az webapp config ssl upload \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --certificate-file certificate.pfx \
  --certificate-password CertPassword123!

# Bind certificate to domain
az webapp config ssl bind \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg \
  --certificate-thumbprint THUMBPRINT \
  --ssl-type SNI
```

### Firewall Rules
```bash
# Configure database firewall
az sql server firewall-rule create \
  --server omani-mental-health-db-server \
  --resource-group omani-mental-health-rg \
  --name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Add specific IP ranges if needed
az sql server firewall-rule create \
  --server omani-mental-health-db-server \
  --resource-group omani-mental-health-rg \
  --name "AllowOfficeIP" \
  --start-ip-address 203.0.113.0 \
  --end-ip-address 203.0.113.255
```

### Security Headers
```python
# security/headers.py
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}
```

## 📊 Monitoring and Logging

### Application Insights Setup
```bash
# Create Application Insights
az monitor app-insights component create \
  --app omani-mental-health-insights \
  --location eastus \
  --resource-group omani-mental-health-rg

# Get instrumentation key
az monitor app-insights component show \
  --app omani-mental-health-insights \
  --resource-group omani-mental-health-rg \
  --query instrumentationKey
```

### Logging Configuration
```python
# logging_config.py
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor
configure_azure_monitor(
    connection_string="InstrumentationKey=your-instrumentation-key"
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/omani-mental-health.log'),
        logging.StreamHandler()
    ]
)

# Logger for different components
logger = logging.getLogger(__name__)
```

### Health Check Endpoint
```python
# health_check.py
import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    
    try:
        # Check database connection
        db_status = check_database_connection()
        
        # Check Redis connection
        redis_status = check_redis_connection()
        
        # Check API services
        api_status = check_api_services()
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {
                'database': db_status,
                'redis': redis_status,
                'apis': api_status
            }
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500
```

## 🚀 Performance Optimization

### Auto-Scaling Configuration
```bash
# Configure auto-scaling
az monitor autoscale create \
  --resource-group omani-mental-health-rg \
  --resource omani-mental-health-bot \
  --resource-type Microsoft.Web/serverfarms \
  --name omani-mental-health-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 2

# Add scaling rules
az monitor autoscale rule create \
  --resource-group omani-mental-health-rg \
  --autoscale-name omani-mental-health-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

az monitor autoscale rule create \
  --resource-group omani-mental-health-rg \
  --autoscale-name omani-mental-health-autoscale \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

### CDN Configuration
```bash
# Create CDN profile
az cdn profile create \
  --name omani-mental-health-cdn \
  --resource-group omani-mental-health-rg \
  --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
  --name omani-mental-health-endpoint \
  --profile-name omani-mental-health-cdn \
  --resource-group omani-mental-health-rg \
  --origin omani-mental-health-bot.azurewebsites.net
```

### Caching Strategy
```python
# caching.py
import redis
import json
from functools import wraps

# Redis connection
redis_client = redis.StrictRedis(
    host='omani-mental-health-cache.redis.cache.windows.net',
    port=6380,
    password='your-redis-password',
    ssl=True
)

def cache_response(expiration=300):
    """Cache decorator for API responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key, 
                expiration, 
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

## 💾 Backup and Recovery

### Database Backup Configuration
```bash
# Configure automated backups
az sql db long-term-retention-policy set \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --database omani-mental-health-db \
  --weekly-retention P4W \
  --monthly-retention P12M \
  --yearly-retention P7Y \
  --week-of-year 1
```

### Application Backup Script
```bash
#!/bin/bash
# backup.sh - Application backup script

BACKUP_DIR="/backup/omani-mental-health"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="omani-mental-health-backup-$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/$BACKUP_FILE \
  --exclude='*.log' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  /var/www/omani-mental-health/

# Backup database
az sql db export \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --name omani-mental-health-db \
  --storage-uri "https://storage.blob.core.windows.net/backups/db-backup-$DATE.bacpac" \
  --storage-key "your-storage-key"

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Recovery Procedures
```bash
# Database recovery
az sql db import \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --name omani-mental-health-db-restored \
  --storage-uri "https://storage.blob.core.windows.net/backups/db-backup-20240315.bacpac" \
  --storage-key "your-storage-key"

# Application recovery
cd /var/www/
tar -xzf /backup/omani-mental-health/omani-mental-health-backup-20240315.tar.gz
systemctl restart omani-mental-health
```

## 🔧 Maintenance Procedures

### Daily Maintenance Tasks
```bash
#!/bin/bash
# daily_maintenance.sh

# Check system health
curl -f https://omani-mental-health-bot.azurewebsites.net/health

# Check disk space
df -h /var/www/omani-mental-health/

# Check logs for errors
grep -i "error\|exception\|failed" /var/log/omani-mental-health.log | tail -50

# Check API rate limits
python scripts/check_api_limits.py

# Clean temporary files
find /tmp -name "*.tmp" -mtime +1 -delete

# Update security patches
az webapp restart \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg
```

### Weekly Maintenance Tasks
```bash
#!/bin/bash
# weekly_maintenance.sh

# Update dependencies
pip install --upgrade -r requirements.txt

# Database maintenance
az sql db show-usage \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --name omani-mental-health-db

# Performance analysis
python scripts/performance_analysis.py

# Security scan
python scripts/security_scan.py

# Generate weekly report
python scripts/generate_weekly_report.py
```

### Monthly Maintenance Tasks
```bash
#!/bin/bash
# monthly_maintenance.sh

# Full system backup
./backup.sh

# Comprehensive security audit
python scripts/security_audit.py

# Performance optimization review
python scripts/performance_review.py

# Update documentation
python scripts/update_documentation.py

# Review and update configurations
python scripts/config_review.py
```

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: High Response Times
```bash
# Check CPU and memory usage
az webapp log tail \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg

# Check database performance
az sql db show-usage \
  --resource-group omani-mental-health-rg \
  --server omani-mental-health-db-server \
  --name omani-mental-health-db

# Solution: Scale up resources
az appservice plan update \
  --name omani-mental-health-plan \
  --resource-group omani-mental-health-rg \
  --sku P2V2
```

#### Issue 2: API Rate Limits
```python
# check_api_limits.py
import openai
import anthropic
from datetime import datetime

def check_openai_limits():
    """Check OpenAI API rate limits"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        print(f"OpenAI API: OK - {datetime.now()}")
        return True
    except openai.error.RateLimitError as e:
        print(f"OpenAI Rate Limit: {e}")
        return False
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return False

def check_anthropic_limits():
    """Check Anthropic API rate limits"""
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1,
            messages=[{"role": "user", "content": "test"}]
        )
        print(f"Anthropic API: OK - {datetime.now()}")
        return True
    except Exception as e:
        print(f"Anthropic Error: {e}")
        return False

if __name__ == "__main__":
    check_openai_limits()
    check_anthropic_limits()
```

#### Issue 3: Database Connection Issues
```python
# db_health_check.py
import pyodbc
import os

def check_database_connection():
    """Check database connectivity"""
    try:
        conn_str = os.environ.get('DATABASE_CONNECTION_STRING')
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result[0] == 1:
            print("Database connection: OK")
            return True
        else:
            print("Database connection: Failed")
            return False
            
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_connection()
```

#### Issue 4: Memory Leaks
```python
# memory_monitor.py
import psutil
import logging
import time

def monitor_memory():
    """Monitor memory usage"""
    process = psutil.Process()
    
    while True:
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        if memory_percent > 80:
            logging.warning(f"High memory usage: {memory_percent:.2f}%")
            
        if memory_info.rss > 1024 * 1024 * 1024:  # 1GB
            logging.error("Memory usage exceeds 1GB")
            
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    monitor_memory()
```

### Emergency Procedures

#### System Failure Recovery
```bash
#!/bin/bash
# emergency_recovery.sh

echo "Starting emergency recovery..."

# Restart application
az webapp restart \
  --name omani-mental-health-bot \
  --resource-group omani-mental-health-rg

# Check health status
sleep 30
curl -f https://omani-mental-health-bot.azurewebsites.net/health

# If still failing, rollback to previous version
if [ $? -ne 0 ]; then
    echo "Rolling back to previous version..."
    az webapp deployment slot swap \
      --name omani-mental-health-bot \
      --resource-group omani-mental-health-rg \
      --slot staging \
      --target-slot production
fi

echo "Emergency recovery completed"
```

#### Crisis Response Escalation
```python
# crisis_escalation.py
import smtplib
from email.mime.text import MIMEText
import requests

def send_alert(message, severity="HIGH"):
    """Send alert to operations team"""
    
    # Email notification
    msg = MIMEText(f"ALERT: {message}")
    msg['Subject'] = f"[{severity}] Omani Mental Health Bot Alert"
    msg['From'] = "alerts@omani-mental-health.com"
    msg['To'] = "ops-team@omani-mental-health.com"
    
    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('alerts@omani-mental-health.com', 'password')
    server.send_message(msg)
    server.quit()
    
    # Slack notification
    webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    slack_message = {
        "text": f"🚨 [{severity}] {message}",
        "username": "Omani Mental Health Bot",
        "channel": "#alerts"
    }
    requests.post(webhook_url, json=slack_message)

if __name__ == "__main__":
    send_alert("System experiencing high error rate", "CRITICAL")
```

## 📊 Performance Monitoring

### Key Performance Indicators (KPIs)
```python
# kpi_monitor.py
import time
import logging
from datetime import datetime, timedelta

class KPIMonitor:
    def __init__(self):
        self.metrics = {
            'response_time': [],
            'error_rate': 0,
            'user_satisfaction': 0,
            'api_calls': 0,
            'concurrent_users': 0
        }
    
    def record_response_time(self, duration):
        """Record response time metric"""
        self.metrics['response_time'].append(duration)
        
        # Keep only last 100 measurements
        if len(self.metrics['response_time']) > 100:
            self.metrics['response_time'].pop(0)
    
    def calculate_averages(self):
        """Calculate average metrics"""
        if self.metrics['response_time']:
            avg_response = sum(self.metrics['response_time']) / len(self.metrics['response_time'])
            
            if avg_response > 20:  # 20 second threshold
                logging.warning(f"High average response time: {avg_response:.2f}s")
                
            return {
                'avg_response_time': avg_response,
                'error_rate': self.metrics['error_rate'],
                'api_calls': self.metrics['api_calls'],
                'concurrent_users': self.metrics['concurrent_users']
            }
        
        return None

# Usage
monitor = KPIMonitor()
```

### Automated Scaling
```python
# auto_scaling.py
import requests
import json
import time

def check_load_and_scale():
    """Check current load and scale if necessary"""
    
    # Get current metrics
    response = requests.get("https://omani-mental-health-bot.azurewebsites.net/health")
    
    if response.status_code == 200:
        health_data = response.json()
        
        # Check if scaling is needed
        if health_data.get('concurrent_users', 0) > 40:
            # Scale up
            subprocess.run([
                'az', 'appservice', 'plan', 'update',
                '--name', 'omani-mental-health-plan',
                '--resource-group', 'omani-mental-health-rg',
                '--sku', 'P2V2'
            ])
            
            logging.info("Scaled up due to high user load")
        
        elif health_data.get('concurrent_users', 0) < 10:
            # Scale down
            subprocess.run([
                'az', 'appservice', 'plan', 'update',
                '--name', 'omani-mental-health-plan',
                '--resource-group', 'omani-mental-health-rg',
                '--sku', 'P1V2'
            ])
            
            logging.info("Scaled down due to low user load")

if __name__ == "__main__":
    while True:
        check_load_and_scale()
        time.sleep(300)  # Check every 5 minutes
```

## 🎯 Conclusion

This deployment guide provides comprehensive instructions for setting up, configuring, and maintaining the Omani Arabic Mental Health Chatbot in a production Azure environment. Following these procedures ensures:

### Deployment Success Factors
1. **Scalability**: Auto-scaling configuration for varying user loads
2. **Security**: Comprehensive security measures and monitoring
3. **Reliability**: Backup and recovery procedures
4. **Performance**: Optimization techniques and monitoring
5. **Maintainability**: Automated maintenance procedures

### Key Operational Metrics
- **Uptime Target**: 99.9% availability
- **Response Time**: <15 seconds average
- **Error Rate**: <1% system errors
- **Security**: Zero security incidents
- **User Satisfaction**: >95% positive feedback

### Support and Maintenance
- **24/7 Monitoring**: Continuous system health monitoring
- **Automated Scaling**: Dynamic resource allocation
- **Regular Updates**: Weekly security and performance updates
- **Expert Support**: Mental health and technical expert availability

This deployment framework establishes a robust foundation for delivering culturally sensitive mental health support to the Omani community while maintaining the highest standards of security, performance, and reliability.

---

**Deployment Guide Version**: 1.0  
**Last Updated**: July 2025  
**Environment**: Azure Production  
**Support Contact**: Technical Operations Team - Available 24/7  
**Emergency Escalation**: crisis-response@omani-mental-health.com 