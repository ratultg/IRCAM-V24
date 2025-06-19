#!/bin/bash

# Exit on error
set -e

echo "IRCAM V24 Installation Script"
echo "----------------------------"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Function to configure network
configure_network() {
    echo
    echo "Network Configuration"
    echo "--------------------"
    echo "Would you like to configure a static IP? (y/n)"
    read -r configure_ip
    
    if [[ $configure_ip =~ ^[Yy]$ ]]; then
        echo "Which interface would you like to configure?"
        echo "1. Ethernet (eth0)"
        echo "2. WiFi (wlan0)"
        read -r interface_choice
        
        case $interface_choice in
            1)
                interface="eth0"
                ;;
            2)
                interface="wlan0"
                ;;
            *)
                echo "Invalid choice. Skipping network configuration."
                return
                ;;
        esac
        
        echo "Enter static IP address (e.g., 192.168.1.100):"
        read -r ip_address
        
        echo "Enter gateway IP address (e.g., 192.168.1.1):"
        read -r gateway
        
        echo "Enter netmask (default is 24 for /24):"
        read -r netmask
        netmask=${netmask:-24}
        
        echo "Configuring static IP..."
        ./configure_network.sh -i "$interface" -p "$ip_address" -n "$netmask" -g "$gateway"
    fi
}

# Function to configure Tailscale
configure_tailscale() {
    echo
    echo "Tailscale Configuration"
    echo "----------------------"
    echo "Would you like to configure Tailscale VPN for remote access? (y/n)"
    read -r configure_vpn
    
    if [[ $configure_vpn =~ ^[Yy]$ ]]; then
        echo "Enter your Tailscale auth key (from https://login.tailscale.com/admin/settings/keys):"
        read -r auth_key
        
        echo "Enter hostname for this device (default: ircam-thermal):"
        read -r hostname
        hostname=${hostname:-ircam-thermal}
        
        echo "Configure this device as an exit node? (y/n)"
        read -r exit_node
        
        echo "Would you like to advertise local subnet routes? (y/n)"
        read -r advertise_routes
        
        TAILSCALE_CMD="./configure_tailscale.sh -k \"$auth_key\" -n \"$hostname\""
        
        if [[ $exit_node =~ ^[Yy]$ ]]; then
            TAILSCALE_CMD="$TAILSCALE_CMD -e"
        fi
        
        if [[ $advertise_routes =~ ^[Yy]$ ]]; then
            echo "Enter subnet routes to advertise (comma-separated, e.g., 192.168.0.0/24,10.0.0.0/24):"
            read -r routes
            if [ -n "$routes" ]; then
                TAILSCALE_CMD="$TAILSCALE_CMD -r \"$routes\""
            fi
            
            echo "Accept routes from other nodes? (y/n)"
            read -r accept_routes
            if [[ $accept_routes =~ ^[Yy]$ ]]; then
                TAILSCALE_CMD="$TAILSCALE_CMD -a"
            fi
        fi
        
        echo "Configuring Tailscale..."
        eval "$TAILSCALE_CMD"
    fi
}

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip i2c-tools python3-psutil

# Create ircam user and group if they don't exist
echo "Setting up ircam user..."
id -u ircam &>/dev/null || useradd -r -s /bin/false ircam
getent group ircam || groupadd ircam

# Add ircam user to i2c group for sensor access
usermod -a -G i2c ircam

# Create installation directory
echo "Creating installation directory..."
install -d -m 755 -o ircam -g ircam /opt/ircam-v24
install -d -m 755 -o ircam -g ircam /opt/ircam-v24/tmp
install -d -m 755 -o ircam -g ircam /var/log/ircam

# Copy application files
echo "Copying application files..."
cp -r ../backend /opt/ircam-v24/
cp ../requirements.txt /opt/ircam-v24/
cp health_check.py /opt/ircam-v24/
chown -R ircam:ircam /opt/ircam-v24
chown -R ircam:ircam /var/log/ircam

# Set up virtual environment
echo "Setting up Python virtual environment..."
sudo -u ircam python3 -m venv /opt/ircam-v24/.venv
sudo -u ircam /opt/ircam-v24/.venv/bin/pip install -r /opt/ircam-v24/requirements.txt
sudo -u ircam /opt/ircam-v24/.venv/bin/pip install requests psutil

# Install systemd services
echo "Installing systemd services..."
cp ircam.service /etc/systemd/system/
cp ircam-health.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ircam
systemctl enable ircam-health

# Enable I2C interface
echo "Enabling I2C interface..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
fi
if ! grep -q "^i2c-dev" /etc/modules; then
    echo "i2c-dev" >> /etc/modules
fi

# Create default environment file
echo "Creating environment file..."
cat > /opt/ircam-v24/.env << EOL
# IRCAM V24 Configuration
MOCK_SENSOR=0
# Add any other configuration variables here
EOL
chown ircam:ircam /opt/ircam-v24/.env
chmod 600 /opt/ircam-v24/.env

# Network configuration
configure_network

# Tailscale configuration
configure_tailscale

# Start the services
echo "Starting IRCAM services..."
systemctl start ircam
systemctl start ircam-health

echo ""
echo "Installation complete!"
echo "Main service and health monitor are now running"
echo "You can check the status with: systemctl status ircam"
echo "View logs with: journalctl -u ircam -f"
echo "Health monitor logs are in /var/log/ircam/health.log"
