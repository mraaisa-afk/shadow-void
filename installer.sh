#!/usr/bin/env bash
# Install the local, safe ShadowVoid CLI for the current user.
# This script intentionally does not require root, create services, alter cron,
# delete history, or establish persistence.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${SHADOWVOID_INSTALL_DIR:-${HOME}/.local/share/shadowvoid}"
BIN_DIR="${SHADOWVOID_BIN_DIR:-${HOME}/.local/bin}"

if ! command -v python3 >/dev/null 2>&1; then
    printf 'python3 is required but was not found\n' >&2
    exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Copy source files only; generated caches and repository metadata are excluded.
find "$SCRIPT_DIR" -maxdepth 1 -type f \( -name '*.py' -o -name '*.yaml' -o -name '*.txt' \) -exec cp -- {} "$INSTALL_DIR/" \;
mkdir -p "$INSTALL_DIR/modules"
find "$SCRIPT_DIR/modules" -maxdepth 1 -type f -name '*.py' -exec cp -- {} "$INSTALL_DIR/modules/" \;

cat > "$BIN_DIR/shadowvoid" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/shadowvoid.py" "\$@"
EOF
chmod 755 "$BIN_DIR/shadowvoid"

printf 'Installed safe ShadowVoid to %s\n' "$INSTALL_DIR"
printf 'Run: %s/shadowvoid help\n' "$BIN_DIR"
printf 'No services, cron jobs, or persistence were created.\n'
