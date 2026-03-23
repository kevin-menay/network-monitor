#!/usr/bin/env python3
"""
Bandwidth Monitor - Track network interface throughput with logging
"""
import psutil
import time
import argparse
import sys
import csv
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)


def get_bytes(interface: str = None) -> tuple[int, int]:
    """Get current bytes sent/received for interface or all interfaces."""
    counters = psutil.net_io_counters(pernic=True)

    if interface:
        if interface not in counters:
            raise ValueError(f"Interface '{interface}' not found. Available: {list(counters.keys())}")
        c = counters[interface]
    else:
        # Sum all interfaces
        sent = sum(c.bytes_sent for c in counters.values())
        recv = sum(c.bytes_recv for c in counters.values())
        return sent, recv

    return c.bytes_sent, c.bytes_recv


def format_speed(bytes_per_sec: float) -> str:
    """Format bytes/sec to human readable string."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 ** 2:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 ** 3:
        return f"{bytes_per_sec / 1024 ** 2:.1f} MB/s"
    else:
        return f"{bytes_per_sec / 1024 ** 3:.1f} GB/s"


def list_interfaces():
    """Print available network interfaces."""
    counters = psutil.net_io_counters(pernic=True)
    print(f"\n{Fore.CYAN}Available network interfaces:{Style.RESET_ALL}")
    for iface, stats in counters.items():
        print(f"  {Fore.YELLOW}{iface:<20}{Style.RESET_ALL} "
              f"↓ {format_speed(stats.bytes_recv):>12}  "
              f"↑ {format_speed(stats.bytes_sent):>12}")


def monitor(interface: str = None, interval: float = 1.0,
            duration: int = None, log_file: str = None):
    """
    Monitor bandwidth in real-time.
    
    Args:
        interface: Network interface name (None = all)
        interval: Sample interval in seconds
        duration: Total monitoring duration (None = indefinite)
        log_file: CSV file to write samples
    """
    iface_label = interface or "all interfaces"
    print(f"\n{Fore.CYAN}[*] Monitoring bandwidth on {iface_label}")
    print(f"[*] Interval: {interval}s | Press Ctrl+C to stop{Style.RESET_ALL}\n")

    csv_writer = None
    csv_file = None

    if log_file:
        csv_file = open(log_file, "w", newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["timestamp", "interface", "download_bps", "upload_bps",
                              "download_human", "upload_human"])

    try:
        prev_sent, prev_recv = get_bytes(interface)
        start_time = time.time()
        samples = []

        while True:
            time.sleep(interval)
            curr_sent, curr_recv = get_bytes(interface)

            dl_speed = (curr_recv - prev_recv) / interval
            ul_speed = (curr_sent - prev_sent) / interval

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dl_human = format_speed(dl_speed)
            ul_human = format_speed(ul_speed)

            samples.append((dl_speed, ul_speed))

            print(f"  [{timestamp}]  "
                  f"{Fore.GREEN}↓ {dl_human:>12}{Style.RESET_ALL}  "
                  f"{Fore.BLUE}↑ {ul_human:>12}{Style.RESET_ALL}")

            if csv_writer:
                csv_writer.writerow([timestamp, iface_label,
                                     f"{dl_speed:.0f}", f"{ul_speed:.0f}",
                                     dl_human, ul_human])
                csv_file.flush()

            prev_sent, prev_recv = curr_sent, curr_recv

            if duration and (time.time() - start_time) >= duration:
                break

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Monitoring stopped by user{Style.RESET_ALL}")
    finally:
        if csv_file:
            csv_file.close()

    if samples:
        avg_dl = sum(s[0] for s in samples) / len(samples)
        avg_ul = sum(s[1] for s in samples) / len(samples)
        print(f"\n{Fore.CYAN}[*] Summary ({len(samples)} samples):")
        print(f"    Avg Download: {format_speed(avg_dl)}")
        print(f"    Avg Upload:   {format_speed(avg_ul)}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Real-time bandwidth monitor with logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bandwidth_monitor.py
  python bandwidth_monitor.py --interface eth0 --interval 2
  python bandwidth_monitor.py --duration 60 --log bandwidth.csv
  python bandwidth_monitor.py --list
        """
    )
    parser.add_argument("--interface", "-i", help="Network interface to monitor")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Sample interval in seconds (default: 1.0)")
    parser.add_argument("--duration", type=int, help="Total monitoring duration in seconds")
    parser.add_argument("--log", help="CSV log file path")
    parser.add_argument("--list", action="store_true", help="List available interfaces")

    args = parser.parse_args()

    if args.list:
        list_interfaces()
        return 0

    monitor(args.interface, args.interval, args.duration, args.log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
