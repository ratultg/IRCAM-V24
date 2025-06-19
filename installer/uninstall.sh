#!/bin/bash

# Exit on error
set -e

echo "IRCAM V24 Uninstallation Script"
echo "------------------------------"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Stop and disable services
echo "Stopping and removing services..."
systemctl stop ircam-health || true
systemctl stop ircam || true
systemctl disable ircam-health || true
systemctl disable ircam || true
rm -f /etc/systemd/system/ircam.service
rm -f /etc/systemd/system/ircam-health.service
systemctl daemon-reload

# Remove application files
echo "Removing application files..."
rm -rf /opt/ircam-v24
rm -rf /var/log/ircam

# Remove user and group
echo "Removing ircam user..."
userdel ircam || true
groupdel ircam || true

echo ""
echo "Uninstallation complete!"
echo "Note: I2C interface settings in /boot/config.txt and /etc/modules were not removed."
