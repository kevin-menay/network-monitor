#!/usr/bin/env python3
"""
Port Scanner - Scan common ports on target hosts
"""
import socket
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from colorama import init, Fore, Style
from tabulate import tabulate

init(autoreset=True)

# Common ports with service names
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
    161: "SNMP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


def scan_port(host: str, port: int, timeout: float = 1.0) -> tuple[int, bool, str]:
    """Attempt TCP connection to host:port."""
    service = COMMON_PORTS.get(port, "Unknown")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return port, result == 0, service
    except Exception:
        return port, False, service


def scan_host(host: str, ports: list[int] = None, timeout: float = 1.0,
              max_workers: int = 100) -> list[dict]:
    """
    Scan a host for open ports.
    
    Args:
        host: Target IP or hostname
        ports: List of ports (defaults to COMMON_PORTS)
        timeout: Connection timeout in seconds
        max_workers: Concurrent connection threads
    
    Returns:
        List of dicts with port, status, service info
    """
    if ports is None:
        ports = list(COMMON_PORTS.keys())

    print(f"\n{Fore.CYAN}[*] Scanning {host} ({len(ports)} ports){Style.RESET_ALL}")
    start_time = datetime.now()

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, host, p, timeout): p for p in ports}
        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                results.append({"Port": port, "Service": service, "Status": "OPEN"})
                print(f"  {Fore.GREEN}[+] {port}/tcp  OPEN  ({service}){Style.RESET_ALL}")

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{Fore.CYAN}[*] Scan completed in {elapsed:.2f}s{Style.RESET_ALL}")

    return sorted(results, key=lambda x: x["Port"])


def main():
    parser = argparse.ArgumentParser(
        description="TCP port scanner for common services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python port_scanner.py 192.168.1.1
  python port_scanner.py 10.0.0.1 --ports 22 80 443 8080
  python port_scanner.py scanme.nmap.org --timeout 2 --output report.txt
        """
    )
    parser.add_argument("host", help="Target IP address or hostname")
    parser.add_argument("--ports", nargs="+", type=int,
                        help="Ports to scan (default: common ports)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Timeout per port (default: 1.0)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrent threads (default: 100)")
    parser.add_argument("--output", help="Save report to file")

    args = parser.parse_args()

    open_ports = scan_host(args.host, args.ports, args.timeout, args.workers)

    if open_ports:
        print(f"\n{Fore.YELLOW}Open Ports on {args.host}:{Style.RESET_ALL}")
        print(tabulate(open_ports, headers="keys", tablefmt="grid"))
    else:
        print(f"\n{Fore.RED}No open ports found on {args.host}{Style.RESET_ALL}")

    if args.output and open_ports:
        with open(args.output, "w") as f:
            f.write(f"Port scan report for {args.host}\n")
            f.write(f"Scanned at: {datetime.now().isoformat()}\n\n")
            f.write(tabulate(open_ports, headers="keys", tablefmt="grid"))
        print(f"\n{Fore.YELLOW}[*] Report saved to {args.output}{Style.RESET_ALL}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
