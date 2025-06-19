#!/bin/bash

# Tailscale installation and configuration script for IRCAM V24
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

TAILSCALE_AUTH_KEY=""
HOSTNAME="ircam-thermal"
ENABLE_EXIT_NODE=0
ADVERTISE_ROUTES=""
ACCEPT_ROUTES=0

# Help message
show_help() {
    echo "IRCAM V24 Tailscale Configuration"
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -k, --auth-key <key>       Tailscale auth key"
    echo "  -n, --hostname <name>      Hostname for this device (default: ircam-thermal)"
    echo "  -e, --exit-node            Configure this device as an exit node"
    echo "  -r, --routes <subnets>     Advertise routes (comma-separated, e.g., 192.168.0.0/24,10.0.0.0/24)"
    echo "  -a, --accept-routes        Accept subnet routes from other nodes"
    echo "  -h, --help                 Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--auth-key)
            TAILSCALE_AUTH_KEY="$2"
            shift 2
            ;;
        -n|--hostname)
            HOSTNAME="$2"
            shift 2
            ;;
        -e|--exit-node)
            ENABLE_EXIT_NODE=1
            shift
            ;;
        -r|--routes)
            ADVERTISE_ROUTES="$2"
            shift 2
            ;;
        -a|--accept-routes)
            ACCEPT_ROUTES=1
            shift
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

echo "Installing Tailscale..."
# Add Tailscale's GPG key and repository
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add -
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list

# Update package list and install Tailscale
apt-get update
apt-get install -y tailscale

# Configure system for IP forwarding and NAT
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf
sysctl -p /etc/sysctl.conf

# Configure iptables for NAT
if [ $ENABLE_EXIT_NODE -eq 1 ]; then
    # Save current iptables rules
    iptables-save > /etc/iptables.rules.backup

    # Add NAT rules
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    iptables -A FORWARD -i tailscale0 -j ACCEPT
    iptables -A FORWARD -o tailscale0 -j ACCEPT

    # Make iptables rules persistent
    apt-get install -y iptables-persistent
    iptables-save > /etc/iptables/rules.v4
fi

# Start Tailscale service
systemctl enable --now tailscaled

# Configure hostname
hostnamectl set-hostname "$HOSTNAME"

# Build Tailscale up command
TAILSCALE_CMD="tailscale up"

if [ -n "$TAILSCALE_AUTH_KEY" ]; then
    TAILSCALE_CMD="$TAILSCALE_CMD --authkey=$TAILSCALE_AUTH_KEY"
fi

TAILSCALE_CMD="$TAILSCALE_CMD --hostname=$HOSTNAME"

if [ $ENABLE_EXIT_NODE -eq 1 ]; then
    TAILSCALE_CMD="$TAILSCALE_CMD --advertise-exit-node"
fi

if [ -n "$ADVERTISE_ROUTES" ]; then
    TAILSCALE_CMD="$TAILSCALE_CMD --advertise-routes=$ADVERTISE_ROUTES"
fi

if [ $ACCEPT_ROUTES -eq 1 ]; then
    TAILSCALE_CMD="$TAILSCALE_CMD --accept-routes"
fi

# Execute Tailscale configuration
echo "Executing: $TAILSCALE_CMD"
eval "$TAILSCALE_CMD"

# Add periodic connectivity check with route verification
cat > /opt/ircam-v24/check_tailscale.sh << 'EOL'
#!/bin/bash

# Get Tailscale status
STATUS=$(tailscale status --json)
CONNECTED=$(echo "$STATUS" | jq -r '.BackendState')
IP=$(echo "$STATUS" | jq -r '.TailscaleIPs[0]')
ROUTES=$(echo "$STATUS" | jq -r '.AdvertisedRoutes[]' 2>/dev/null)

if [ "$CONNECTED" = "Running" ]; then
    echo "$(date): Tailscale connected - IP: $IP" >> /var/log/ircam/health.log
    if [ -n "$ROUTES" ]; then
        echo "$(date): Advertising routes: $ROUTES" >> /var/log/ircam/health.log
    fi
else
    echo "$(date): Tailscale disconnected - attempting to reconnect" >> /var/log/ircam/health.log
    tailscale up --reset
fi

# Verify NAT and routing
if ip route show | grep -q tailscale0; then
    echo "$(date): Tailscale routes verified" >> /var/log/ircam/health.log
else
    echo "$(date): Warning: Tailscale routes missing" >> /var/log/ircam/health.log
fi
EOL

chmod +x /opt/ircam-v24/check_tailscale.sh

# Add periodic check to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/ircam-v24/check_tailscale.sh") | crontab -

echo "Tailscale installation complete!"
echo "Status: $(tailscale status)"

if [ $ENABLE_EXIT_NODE -eq 1 ]; then
    echo
    echo "Exit node configuration:"
    echo "1. Go to Tailscale admin console"
    echo "2. Enable subnet routes for this device"
    echo "3. Enable exit node status for this device"
    echo
    echo "Note: Exit node feature requires Tailscale Business or Enterprise plan"
fi

if [ -n "$ADVERTISE_ROUTES" ]; then
    echo
    echo "Subnet routes configured:"
    echo "$ADVERTISE_ROUTES"
    echo
    echo "Note: Remember to enable subnet routes in Tailscale admin console"
fi
