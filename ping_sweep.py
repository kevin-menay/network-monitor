#!/usr/bin/env python3
"""
Ping Sweep Scanner - Discover active hosts on a subnet
"""
import subprocess
import ipaddress
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)


def ping_host(ip: str, timeout: int = 1) -> tuple[str, bool]:
    """Ping a single host and return (ip, is_alive)."""
    cmd = ["ping", "-c", "1", "-W", str(timeout), str(ip)]
    result = subprocess.run(cmd, capture_output=True, timeout=timeout + 2)
    return str(ip), result.returncode == 0


def ping_sweep(subnet: str, timeout: int = 1, max_workers: int = 50) -> list[str]:
    """
    Scan a subnet and return list of active hosts.
    
    Args:
        subnet: CIDR notation (e.g. 192.168.1.0/24)
        timeout: Ping timeout in seconds
        max_workers: Number of concurrent ping threads
    
    Returns:
        List of active IP addresses
    """
    network = ipaddress.ip_network(subnet, strict=False)
    hosts = list(network.hosts())
    active_hosts = []

    print(f"\n{Fore.CYAN}[*] Starting ping sweep on {subnet}")
    print(f"[*] Scanning {len(hosts)} hosts with {max_workers} threads{Style.RESET_ALL}\n")

    start_time = datetime.now()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(ping_host, str(ip), timeout): ip for ip in hosts}

        for future in as_completed(futures):
            ip, alive = future.result()
            if alive:
                active_hosts.append(ip)
                print(f"  {Fore.GREEN}[+] {ip} is UP{Style.RESET_ALL}")

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\n{Fore.CYAN}[*] Scan complete in {elapsed:.2f}s")
    print(f"[*] Found {len(active_hosts)}/{len(hosts)} active hosts{Style.RESET_ALL}\n")

    return sorted(active_hosts)


def main():
    parser = argparse.ArgumentParser(
        description="Ping sweep scanner for subnet discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ping_sweep.py 192.168.1.0/24
  python ping_sweep.py 10.0.0.0/16 --timeout 2 --workers 100
  python ping_sweep.py 172.16.0.0/24 --output results.txt
        """
    )
    parser.add_argument("subnet", help="Target subnet in CIDR notation")
    parser.add_argument("--timeout", type=int, default=1, help="Ping timeout seconds (default: 1)")
    parser.add_argument("--workers", type=int, default=50, help="Concurrent threads (default: 50)")
    parser.add_argument("--output", help="Save results to file")

    args = parser.parse_args()

    active = ping_sweep(args.subnet, args.timeout, args.workers)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Ping sweep results for {args.subnet}\n")
            f.write(f"# Scanned at {datetime.now().isoformat()}\n\n")
            for ip in active:
                f.write(f"{ip}\n")
        print(f"{Fore.YELLOW}[*] Results saved to {args.output}{Style.RESET_ALL}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
