#!/bin/bash

# Network configuration script for IRCAM V24
# Configures static IP for ethernet (eth0) or WiFi (wlan0)

set -e

# Default values
INTERFACE="eth0"
IP_ADDRESS=""
NETMASK="24"
GATEWAY=""
DNS1="8.8.8.8"
DNS2="8.8.4.4"

# Help message
show_help() {
    echo "IRCAM V24 Network Configuration"
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -i, --interface <eth0|wlan0>    Network interface to configure"
    echo "  -p, --ip <ip_address>           Static IP address (e.g., 192.168.1.100)"
    echo "  -n, --netmask <cidr>            Network mask in CIDR notation (e.g., 24 for /24)"
    echo "  -g, --gateway <ip_address>      Gateway IP address"
    echo "  -d, --dns1 <ip_address>         Primary DNS server"
    echo "  -s, --dns2 <ip_address>         Secondary DNS server"
    echo "  -h, --help                      Show this help message"
    echo
    echo "Example:"
    echo "  $0 -i eth0 -p 192.168.1.100 -n 24 -g 192.168.1.1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interface)
            INTERFACE="$2"
            shift 2
            ;;
        -p|--ip)
            IP_ADDRESS="$2"
            shift 2
            ;;
        -n|--netmask)
            NETMASK="$2"
            shift 2
            ;;
        -g|--gateway)
            GATEWAY="$2"
            shift 2
            ;;
        -d|--dns1)
            DNS1="$2"
            shift 2
            ;;
        -s|--dns2)
            DNS2="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$IP_ADDRESS" ] || [ -z "$GATEWAY" ]; then
    echo "Error: IP address and gateway are required"
    show_help
    exit 1
fi

if [ "$INTERFACE" != "eth0" ] && [ "$INTERFACE" != "wlan0" ]; then
    echo "Error: Interface must be either eth0 or wlan0"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Backup existing configuration
echo "Backing up current network configuration..."
if [ -f /etc/dhcpcd.conf ]; then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
fi

# Configure static IP
echo "Configuring static IP for $INTERFACE..."
cat > /etc/dhcpcd.conf << EOL
# IRCAM V24 Static IP Configuration
hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option interface_mtu
require dhcp_server_identifier
slaac private

# Static IP configuration for $INTERFACE
interface $INTERFACE
static ip_address=$IP_ADDRESS/$NETMASK
static routers=$GATEWAY
static domain_name_servers=$DNS1 $DNS2
EOL

# Restart networking
echo "Restarting networking service..."
systemctl restart dhcpcd

# Verify configuration
echo "Verifying network configuration..."
sleep 5  # Wait for network to stabilize

# Test network connectivity
if ping -c 1 $GATEWAY > /dev/null 2>&1; then
    echo "Network configuration successful!"
    echo "New IP address: $IP_ADDRESS"
    echo "Gateway: $GATEWAY"
    echo "Interface: $INTERFACE"
    echo "Configuration file: /etc/dhcpcd.conf"
    echo "Backup file: /etc/dhcpcd.conf.backup"
else
    echo "Warning: Could not ping gateway. Please verify your network settings."
    echo "You can restore the backup with: sudo cp /etc/dhcpcd.conf.backup /etc/dhcpcd.conf"
fi

# Add network status to health check log
if [ -d "/var/log/ircam" ]; then
    echo "$(date): Static IP configured - Interface: $INTERFACE, IP: $IP_ADDRESS" >> /var/log/ircam/health.log
fi
