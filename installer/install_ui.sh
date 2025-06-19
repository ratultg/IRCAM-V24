#!/bin/bash

# Installation UI Script for IRCAM V24
BACKTITLE="IRCAM V24 Installation"
DIALOG_OK=0
DIALOG_CANCEL=1
DIALOG_ESC=255
DIALOG_HEIGHT=20
DIALOG_WIDTH=70

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Check if dialog is installed
if ! command -v dialog &> /dev/null; then
    apt-get update && apt-get install -y dialog
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

show_error() {
    dialog --backtitle "$BACKTITLE" --title "Error" --msgbox "$1" 8 60
}

get_input() {
    local value
    value=$(dialog --backtitle "$BACKTITLE" --title "$1" --inputbox "$2" 8 60 "$3" 3>&1 1>&2 2>&3)
    echo "$value"
}

ask_yn() {
    dialog --backtitle "$BACKTITLE" --title "$1" --yesno "$2" 8 60
    return $?
}

# Reset RaspberryPi to clean config
reset_rpi_config() {
    # Show reset options menu
    local choice
    choice=$(dialog --backtitle "$BACKTITLE" \
        --title "Reset Options" \
        --menu "Choose reset level:" 15 60 4 \
        1 "Clean IRCAM installation only" \
        2 "Clean OS packages and update system" \
        3 "Full OS reset (will reboot)" \
        4 "Skip reset" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        1)
            dialog --backtitle "$BACKTITLE" \
                --title "Reset IRCAM" \
                --yesno "This will reset IRCAM installation:\n\n- Stop existing services\n- Clear previous database\n- Reset network config\n- Clean previous installations\n\nContinue?" 12 60
            
            if [ $? -eq $DIALOG_OK ]; then
                {
                    echo "10"; echo "XXX"; echo "Stopping services..."; echo "XXX"
                    # Stop all related services
                    systemctl stop ircam.service ircam-health.service tailscaled nginx 2>/dev/null
                    systemctl disable ircam.service ircam-health.service tailscaled nginx 2>/dev/null
                    
                    echo "20"; echo "XXX"; echo "Removing service files..."; echo "XXX"
                    # Remove service files and reload
                    rm -f /etc/systemd/system/ircam*.service
                    systemctl daemon-reload
                    
                    echo "30"; echo "XXX"; echo "Cleaning databases and data..."; echo "XXX"
                    # Clean all application data
                    rm -f /var/lib/ircam/*.db
                    rm -rf /var/lib/ircam/frames/*
                    rm -rf /var/log/ircam/*
                    rm -rf /var/run/ircam/*
                    
                    echo "40"; echo "XXX"; echo "Backing up and resetting network..."; echo "XXX"
                    # Network configuration cleanup
                    if [ -f "/etc/dhcpcd.conf" ]; then
                        cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
                        sed -i '/^interface/d; /^static ip_address/d; /^static routers/d; /^static domain_name_servers/d' /etc/dhcpcd.conf
                    fi
                    # Reset wpa_supplicant
                    cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.backup 2>/dev/null
                    
                    echo "50"; echo "XXX"; echo "Cleaning Python environments..."; echo "XXX"
                    # Clean Python environments and caches
                    rm -rf venv/ .venv/
                    rm -rf ~/.cache/pip
                    rm -rf ~/.local/lib/python*
                    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
                    find . -type f -name "*.pyc" -delete
                    
                    echo "60"; echo "XXX"; echo "Removing Tailscale..."; echo "XXX"
                    # Clean Tailscale completely
                    if command -v tailscale >/dev/null 2>&1; then
                        tailscale logout 2>/dev/null
                        systemctl stop tailscaled 2>/dev/null
                        systemctl disable tailscaled 2>/dev/null
                        rm -rf /var/lib/tailscale/*
                        rm -f /etc/tailscale/*.conf
                    fi
                    
                    echo "70"; echo "XXX"; echo "Cleaning system logs..."; echo "XXX"
                    # Clean logs
                    find /var/log -type f -name "*.gz" -delete
                    find /var/log -type f -name "*.old" -delete
                    find /var/log -type f -name "*.1" -delete
                    truncate -s 0 /var/log/*.log 2>/dev/null
                    journalctl --vacuum-time=1d 2>/dev/null
                    
                    echo "80"; echo "XXX"; echo "Cleaning user data..."; echo "XXX"
                    # Clean user caches and temps
                    rm -rf ~/.cache/*
                    rm -rf /tmp/*
                    rm -rf /var/tmp/*
                    
                    echo "90"; echo "XXX"; echo "Resetting permissions..."; echo "XXX"
                    # Reset permissions
                    mkdir -p /var/lib/ircam/frames
                    mkdir -p /var/log/ircam
                    mkdir -p /var/run/ircam
                    chown -R root:root /var/lib/ircam
                    chmod -R 755 /var/lib/ircam
                    
                    echo "100"; echo "XXX"; echo "Cleanup complete!"; echo "XXX"
                } | dialog --backtitle "$BACKTITLE" --title "Cleaning System" --gauge "Starting cleanup..." 8 60 0
                dialog --backtitle "$BACKTITLE" --title "Success" --msgbox "IRCAM configuration has been reset successfully.\nA backup of network config is saved as dhcpcd.conf.backup" 8 60
                return 0
            fi
            ;;
        2)
            dialog --backtitle "$BACKTITLE" --title "OS Package Reset" --yesno "This will:\n\n- Remove unnecessary packages\n- Clean package cache\n- Update system packages\n- Reset system configurations\n- Clean user installations\n\nThis may take several minutes.\nContinue?" 15 60
            if [ $? -eq $DIALOG_OK ]; then
                {
                    echo "10"; echo "XXX"; echo "Stopping services...\\nThis may take a while"; echo "XXX"
                    systemctl stop ircam.service ircam-health.service tailscaled 2>/dev/null
                    
                    echo "20"; echo "XXX"; echo "Removing unnecessary packages..."; echo "XXX"
                    apt-get -y autoremove 2>/dev/null
                    
                    echo "40"; echo "XXX"; echo "Cleaning package cache..."; echo "XXX"
                    apt-get -y clean 2>/dev/null
                    apt-get -y autoclean 2>/dev/null
                    
                    echo "60"; echo "XXX"; echo "Updating package lists..."; echo "XXX"
                    apt-get update 2>/dev/null
                    
                    echo "80"; echo "XXX"; echo "Upgrading system packages..."; echo "XXX"
                    apt-get -y upgrade 2>/dev/null
                    
                    echo "90"; echo "XXX"; echo "Cleaning user installations..."; echo "XXX"
                    rm -rf /home/pi/.local/lib/python* 2>/dev/null
                    rm -rf /home/pi/.cache/* 2>/dev/null
                    
                    echo "100"; echo "XXX"; echo "Reset complete!"; echo "XXX"
                } | dialog --backtitle "$BACKTITLE" --title "Resetting OS" --gauge "Starting OS reset..." 8 60 0
                dialog --backtitle "$BACKTITLE" --title "Success" --msgbox "OS has been reset and updated successfully." 6 60
                return 0
            fi
            ;;
        3)
            dialog --backtitle "$BACKTITLE" --title "Full OS Reset" --yesno "WARNING: This will reset the entire OS to factory settings!\n\n- All data will be erased\n- All configurations will be reset\n- System will reboot\n- You will need to reconfigure network\n\nThis operation cannot be undone!\nAre you absolutely sure?" 16 60
            if [ $? -eq $DIALOG_OK ]; then
                dialog --backtitle "$BACKTITLE" --title "Confirm Full Reset" --yesno "FINAL WARNING:\n\nSystem will be completely reset.\nAll data will be lost.\n\nType 'RESET' to confirm:" 10 60
                if [ $? -eq $DIALOG_OK ]; then
                    CONFIRM=$(dialog --backtitle "$BACKTITLE" --title "Confirm Reset" --inputbox "Type 'RESET' to confirm:" 8 40 3>&1 1>&2 2>&3)
                    if [ "$CONFIRM" = "RESET" ]; then
                        dialog --backtitle "$BACKTITLE" --title "Resetting OS" --infobox "Preparing for full system reset...\nSystem will reboot when complete." 5 50
                        raspi-config --erase-all >/dev/null 2>&1
                        reboot
                        exit 0
                    fi
                fi
            fi
            ;;
        4|"")
            dialog --backtitle "$BACKTITLE" --title "Skip Reset" --msgbox "Skipping system reset." 6 50
            return 0
            ;;
    esac
}

# Tailscale VPN configuration menu
configure_tailscale_ui() {
    local auth_key
    local hostname
    local tailscale_cmd
    local routes
    
    auth_key=$(get_input "Tailscale Auth Key" "Enter your Tailscale auth key\n(from login.tailscale.com/admin/settings/keys):" "")
    if [ -z "$auth_key" ]; then return 1; fi
    
    hostname=$(get_input "Hostname" "Enter hostname for this device:" "ircam-thermal")
    if [ -z "$hostname" ]; then return 1; fi
    
    tailscale_cmd="$SCRIPT_DIR/configure_tailscale.sh -k \"$auth_key\" -n \"$hostname\""
    
    # Ask about exit node
    if ask_yn "Exit Node" "Configure this device as an exit node?"; then
        tailscale_cmd="$tailscale_cmd -e"
    fi
    
    # Ask about subnet routes
    if ask_yn "Subnet Routes" "Would you like to advertise local subnet routes?"; then
        routes=$(get_input "Routes" "Enter subnet routes to advertise\n(comma-separated, e.g., 192.168.0.0/24,10.0.0.0/24):" "")
        if [ -n "$routes" ]; then
            tailscale_cmd="$tailscale_cmd -r \"$routes\""
        fi
        
        if ask_yn "Accept Routes" "Accept routes from other nodes?"; then
            tailscale_cmd="$tailscale_cmd -a"
        fi
    fi
    
    # Configure Tailscale
    dialog --backtitle "$BACKTITLE" \
        --title "Tailscale Setup" \
        --infobox "Configuring Tailscale..." 5 50
    
    if eval "$tailscale_cmd" >/dev/null 2>&1; then
        dialog --backtitle "$BACKTITLE" \
            --title "Success" \
            --msgbox "Tailscale configuration successfully applied" 6 50
        return 0
    else
        show_error "Failed to configure Tailscale"
        return 1
    fi
}

# Set up Python virtual environment
setup_python_env() {
    dialog --backtitle "$BACKTITLE" \
        --title "Python Environment Setup" \
        --yesno "This will set up a Python virtual environment and install requirements.\nDo you want to continue?" 8 60
    
    if [ $? -eq $DIALOG_OK ]; then
        {
            echo "20"; echo "XXX"; echo "Creating virtual environment..."; echo "XXX"
            # Create virtual environment
            python3 -m venv /opt/ircam/venv
            
            echo "40"; echo "XXX"; echo "Setting up activation script..."; echo "XXX"
            # Create activation script
            cat > /etc/profile.d/ircam-venv.sh << 'EOF'
#!/bin/bash
# Activate IRCAM Python virtual environment
if [ -f "/opt/ircam/venv/bin/activate" ]; then
    source /opt/ircam/venv/bin/activate
fi
EOF
            chmod +x /etc/profile.d/ircam-venv.sh
            
            echo "60"; echo "XXX"; echo "Activating virtual environment..."; echo "XXX"
            # Activate venv for current installation
            source /opt/ircam/venv/bin/activate
            
            echo "80"; echo "XXX"; echo "Installing Python requirements..."; echo "XXX"
            # Install requirements
            pip install --upgrade pip
            pip install -r requirements.txt
            
            echo "100"; echo "XXX"; echo "Setup complete!"; echo "XXX"
        } | dialog --backtitle "$BACKTITLE" --title "Python Setup" --gauge "Setting up Python environment..." 8 60 0
        
        dialog --backtitle "$BACKTITLE" \
            --title "Success" \
            --msgbox "Python environment has been set up successfully.\nThe virtual environment will be automatically activated on login." 8 60
        return 0
    else
        dialog --backtitle "$BACKTITLE" \
            --title "Skip Python Setup" \
            --msgbox "Skipping Python environment setup." 6 50
        return 0
    fi
}

# Installation process
install_ircam() {
    local step=1
    local total_steps=3
    
    # Step 1: Reset RPI Configuration
    dialog --backtitle "$BACKTITLE" \
        --title "Step $step/$total_steps" \
        --msgbox "Step 1: Reset RaspberryPi Configuration" 6 50
    reset_rpi_config || return 1
    
    # Step 2: Configure Tailscale
    ((step++))
    dialog --backtitle "$BACKTITLE" \
        --title "Step $step/$total_steps" \
        --msgbox "Step 2: Configure Tailscale VPN" 6 50
    configure_tailscale_ui || return 1
    
    # Step 3: Setup Python Environment
    ((step++))
    dialog --backtitle "$BACKTITLE" \
        --title "Step $step/$total_steps" \
        --msgbox "Step 3: Setup Python Environment" 6 50
    setup_python_env || return 1
    
    # Installation complete
    dialog --backtitle "$BACKTITLE" \
        --title "Installation Complete" \
        --msgbox "IRCAM V24 has been successfully installed.\n\nThe system is now configured with:\n- Clean RaspberryPi configuration\n- Tailscale VPN access\n- Python environment and dependencies" 12 60
    
    return 0
}

# Main script execution
clear
dialog --backtitle "$BACKTITLE" \
    --title "Welcome" \
    --yesno "Welcome to IRCAM V24 Installer\n\nThis installer will:\n1. Reset RaspberryPi to clean configuration\n2. Configure Tailscale VPN\n3. Setup Python environment\n\nEach step will ask for confirmation.\nWould you like to continue?" \
    15 60

case $? in
    $DIALOG_OK)
        install_ircam
        ;;
    $DIALOG_CANCEL|$DIALOG_ESC)
        clear
        exit 1
        ;;
esac

clear
