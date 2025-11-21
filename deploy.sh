#!/bin/bash

# Portfolio API Backend Deployment Script
# Run this script on the VPS server as the deploy user

set -e  # Exit on error

BACKEND_DIR="/var/www/portfolio/backend"
VENV_DIR="$BACKEND_DIR/venv"

echo "========================================"
echo "Portfolio API Backend Deployment"
echo "========================================"

# Navigate to backend directory
cd $BACKEND_DIR

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install gunicorn if not in requirements.txt
echo "Installing gunicorn..."
pip install gunicorn

# Check if .env.production exists
if [ ! -f "$BACKEND_DIR/.env.production" ]; then
    echo "ERROR: .env.production file not found!"
    exit 1
fi

# Create symbolic link for .env if needed
if [ ! -f "$BACKEND_DIR/.env" ]; then
    ln -s $BACKEND_DIR/.env.production $BACKEND_DIR/.env
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=portfolio_api.settings

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=portfolio_api.settings

# Create logs directory if it doesn't exist
mkdir -p $BACKEND_DIR/logs

# Set proper permissions
echo "Setting permissions..."
chmod 755 $BACKEND_DIR
chmod -R 755 $BACKEND_DIR/staticfiles
chmod -R 755 $BACKEND_DIR/media

echo "========================================"
echo "Deployment completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Copy the systemd service file:"
echo "   sudo cp $BACKEND_DIR/portfolio_api.service /etc/systemd/system/"
echo ""
echo "2. Reload systemd:"
echo "   sudo systemctl daemon-reload"
echo ""
echo "3. Enable and start the service:"
echo "   sudo systemctl enable portfolio_api"
echo "   sudo systemctl start portfolio_api"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status portfolio_api"
echo ""
echo "5. Reload nginx:"
echo "   sudo systemctl reload nginx"
