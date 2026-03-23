# Network Monitor 🌐

A Python toolkit for network monitoring and discovery in IT infrastructure environments. Includes ping sweep scanner, port scanner, and real-time bandwidth monitor with CSV logging.

## Features

- **Ping Sweep Scanner** - Fast multi-threaded subnet discovery to identify live hosts
- **Port Scanner** - TCP port scanning for 25 common services (SSH, HTTP, RDP, SQL, etc.)
- **Bandwidth Monitor** - Real-time per-interface throughput tracking with CSV export
- Colorized terminal output for quick status identification
- Concurrent scanning with configurable thread pools
- File-based output for report archiving

## Tech Stack

- Python 3.10+
- `psutil` - System and network statistics
- `scapy` - Network packet crafting
- `colorama` - Cross-platform terminal colors
- `tabulate` - Formatted table output

## Installation

```bash
git clone https://github.com/kevinmenay/network-monitor.git
cd network-monitor
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Ping Sweep

Discover live hosts on a subnet:

```bash
# Scan an entire /24 subnet
python ping_sweep.py 192.168.1.0/24

# Custom timeout and thread count
python ping_sweep.py 10.0.0.0/24 --timeout 2 --workers 100

# Save results to file
python ping_sweep.py 192.168.1.0/24 --output active_hosts.txt
```

**Example output:**
```
[*] Starting ping sweep on 192.168.1.0/24
[*] Scanning 254 hosts with 50 threads

  [+] 192.168.1.1 is UP
  [+] 192.168.1.10 is UP
  [+] 192.168.1.25 is UP
  [+] 192.168.1.100 is UP

[*] Scan complete in 3.42s
[*] Found 4/254 active hosts
```

### Port Scanner

Scan open TCP ports on a target:

```bash
# Scan default common ports
python port_scanner.py 192.168.1.1

# Scan specific ports
python port_scanner.py 10.0.0.5 --ports 22 80 443 3389 5432

# Save report to file
python port_scanner.py 192.168.1.1 --output port_report.txt
```

**Example output:**
```
[*] Scanning 192.168.1.1 (25 ports)
  [+] 22/tcp  OPEN  (SSH)
  [+] 80/tcp  OPEN  (HTTP)
  [+] 443/tcp OPEN  (HTTPS)

+--------+----------+--------+
| Port   | Service  | Status |
+--------+----------+--------+
| 22     | SSH      | OPEN   |
| 80     | HTTP     | OPEN   |
| 443    | HTTPS    | OPEN   |
+--------+----------+--------+
```

### Bandwidth Monitor

Monitor network throughput in real-time:

```bash
# Monitor all interfaces
python bandwidth_monitor.py

# Monitor specific interface
python bandwidth_monitor.py --interface eth0

# Log 60 seconds of data to CSV
python bandwidth_monitor.py --duration 60 --log bandwidth_log.csv

# List available interfaces
python bandwidth_monitor.py --list
```

**Example output:**
```
[*] Monitoring bandwidth on eth0
[*] Interval: 1.0s | Press Ctrl+C to stop

  [2024-03-15 14:32:01]  ↓      1.2 MB/s  ↑    245.3 KB/s
  [2024-03-15 14:32:02]  ↓    892.4 KB/s  ↑    198.1 KB/s
  [2024-03-15 14:32:03]  ↓      2.1 MB/s  ↑    301.7 KB/s

[*] Summary (3 samples):
    Avg Download: 1.4 MB/s
    Avg Upload:   248.4 KB/s
```

## Project Structure

```
network-monitor/
├── ping_sweep.py        # Subnet host discovery
├── port_scanner.py      # TCP port scanning
├── bandwidth_monitor.py # Real-time bandwidth tracking
├── requirements.txt     # Python dependencies
└── README.md
```

## Use Cases

- **Network auditing** - Identify unauthorized devices on your network
- **Security assessment** - Discover exposed services on hosts
- **Performance monitoring** - Track bandwidth utilization over time
- **IT documentation** - Generate reports of active infrastructure

## Notes

- Ping sweep requires ICMP permissions (run as Administrator/root on some systems)
- Port scanning should only be performed on networks you own or have permission to scan
- CSV logs can be imported into Excel or Grafana for visualization

## License

MIT License - See [LICENSE](LICENSE) for details.
