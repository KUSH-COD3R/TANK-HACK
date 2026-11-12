#!/usr/bin/env python3
"""
  ████████╗ █████╗ ███╗   ██╗██╗  ██╗
  ╚══██╔══╝██╔══██╗████╗  ██║██║ ██╔╝
     ██║   ███████║██╔██╗ ██║█████╔╝
     ██║   ██╔══██║██║╚██╗██║██╔═██╗
     ██║   ██║  ██║██║ ╚████║██║  ██╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝

  ██╗  ██╗ █████╗  ██████╗██╗  ██╗
  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝
  ███████║███████║██║     █████╔╝
  ██╔══██║██╔══██║██║     ██╔═██╗
  ██║  ██║██║  ██║╚██████╗██║  ██╗
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

  TANK HACK — Lightweight Network Recon Tool
  [ ARMORED RECONNAISSANCE FRAMEWORK ]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Sequence, TextIO

__version__ = "2.1.0"

# ── ASCII TANK ──────────────────────────────────────────────────────────

TANK_ART = r"""
                    ████████████
                  ██  ╔══════╗  ██
                ██   ║  ██╔══╝   ██
              ██     ║  ██║       ██
              ██     ║  ██║       ██
              ██     ╚══╦═╝   ██  ██
        ███████████████╔╝ ████████████
      ██ ┌╦══════════╦═╩═╦══════════╦┐ ██
    ██   ║║  ████████║   ║████████  ║║   ██
  ██     ║║  ██    ██║   ║██    ██  ║║     ██
  ██     ║║  ████████║   ║████████  ║║     ██
  ██     ║║          ║   ║          ║║     ██
  ██     ╚╩══════════╝   ╚══════════╩╝     ██
  ██   ██         ██     ██         ██   ██
  ██████████████████     ██████████████████
"""

BANNER = r"""
  ████████╗ █████╗ ███╗   ██╗██╗  ██╗    ██╗  ██╗ █████╗  ██████╗██╗  ██╗
  ╚══██╔══╝██╔══██╗████╗  ██║██║ ██╔╝    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝
     ██║   ███████║██╔██╗ ██║█████╔╝     ███████║███████║██║     █████╔╝
     ██║   ██╔══██║██║╚██╗██║██╔═██╗     ██╔══██║██╔══██║██║     ██╔═██╗
     ██║   ██║  ██║██║ ╚████║██║  ██╗    ██║  ██║██║  ██║╚██████╗██║  ██╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
"""


# ── Utilities ──────────────────────────────────────────────────────────

def _width() -> int:
    return max(40, shutil.get_terminal_size((80, 24)).columns)


def paint(text: str, code: str, *, enabled: bool = True, stream: TextIO | None = None) -> str:
    target = stream or sys.stdout
    if enabled and "NO_COLOR" not in os.environ and getattr(target, "isatty", lambda: False)():
        return f"\033[{code}m{text}\033[0m"
    return text


def green(text: str, **kw) -> str:
    return paint(text, "32", **kw)


def red(text: str, **kw) -> str:
    return paint(text, "31", **kw)


def yellow(text: str, **kw) -> str:
    return paint(text, "33", **kw)


def cyan(text: str, **kw) -> str:
    return paint(text, "36", **kw)


def magenta(text: str, **kw) -> str:
    return paint(text, "35", **kw)


def bold(text: str, **kw) -> str:
    return paint(text, "1", **kw)


# ── Show banner ────────────────────────────────────────────────────────

def show_banner(color: bool = True, stream: TextIO | None = None) -> str:
    w = min(_width(), 80)
    lines = [
        magenta(BANNER, enabled=color, stream=stream),
        green(TANK_ART, enabled=color, stream=stream),
        yellow("  ╔" + "═" * (w - 4) + "╗", enabled=color, stream=stream),
        yellow(f"  ║  ARMORED RECONNAISSANCE FRAMEWORK v{__version__}{' ' * (w - 48)}║", enabled=color, stream=stream),
        yellow(f"  ║  [ TANK-HACK — Lightweight Network Recon Tool ]{' ' * (w - 54)}║", enabled=color, stream=stream),
        yellow("  ╚" + "═" * (w - 4) + "╝", enabled=color, stream=stream),
        "",
    ]
    return "\n".join(lines)


# ── Port Scanner ───────────────────────────────────────────────────────

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 2049: "NFS",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    27017: "MongoDB",
}


def scan_port(host: str, port: int, timeout: float = 2.0) -> tuple[int, str, bool]:
    """Scan a single port on a host."""
    try:
        family = socket.AF_INET6 if ":" in host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                return port, service, True
    except (socket.gaierror, socket.timeout, ConnectionRefusedError, OSError):
        pass
    return port, "Unknown", False


def scan_ports(
    host: str,
    ports: list[int],
    timeout: float = 2.0,
    max_workers: int = 50,
    progress: bool = True,
    stream: TextIO | None = None,
) -> list[tuple[int, str]]:
    """Scan multiple ports using threads."""
    open_ports: list[tuple[int, str]] = []
    total = len(ports)
    done = 0
    stream = stream or sys.stdout

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, host, p, timeout): p for p in ports}
        for future in as_completed(futures):
            done += 1
            port, service, is_open = future.result()
            if is_open:
                open_ports.append((port, service))
                sig = f"  ▸ PORT {port:>5} ({service}) → {green('OPEN', stream=stream)}"
                stream.write(f"{sig}\n")
            if progress and total > 10 and done % 10 == 0:
                pct = int(done / total * 100)
                bar = "█" * (pct // 4) + "░" * (25 - pct // 4)
                stream.write(f"\r  ║ {bar} ║ {done}/{total} scanned\r")
                stream.flush()

    if progress and total > 10:
        stream.write(f"\r{' ' * (_width())}\r")
        stream.flush()

    return sorted(open_ports, key=lambda x: x[0])


# ── DNS Lookup ─────────────────────────────────────────────────────────

def dns_lookup(target: str) -> dict:
    """Resolve a domain to IPv4 and IPv6 addresses."""
    result: dict[str, list[str]] = {"ipv4": [], "ipv6": [], "hostname": target}
    try:
        info = socket.getaddrinfo(target, None)
        seen = set()
        for entry in info:
            addr = entry[4][0]
            if addr not in seen:
                seen.add(addr)
                if entry[0] == socket.AF_INET:
                    result["ipv4"].append(addr)
                elif entry[0] == socket.AF_INET6:
                    result["ipv6"].append(addr)
    except socket.gaierror:
        pass
    return result


def reverse_dns(ip: str) -> str | None:
    """Reverse DNS lookup."""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except (socket.herror, socket.gaierror):
        return None


# ── Ping / ICMP check ──────────────────────────────────────────────────

def ping_check(host: str, count: int = 4) -> tuple[bool, float]:
    """Ping a host and return (reachable, avg_ms)."""
    try:
        flag = "-n" if sys.platform == "win32" else "-c"
        start = time.time()
        subprocess.run(
            ["ping", flag, str(count), host],
            capture_output=True,
            timeout=10,
        )
        elapsed = (time.time() - start) / count * 1000
        return True, round(elapsed, 1)
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return False, 0.0


# ── Banner grab ────────────────────────────────────────────────────────

def grab_banner(host: str, port: int, timeout: float = 3.0) -> str | None:
    """Grab a service banner from an open port."""
    try:
        family = socket.AF_INET6 if ":" in host else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(b"\r\n")
            data = sock.recv(1024)
            banner = data.decode("utf-8", errors="ignore").strip()
            return banner if banner else None
    except (socket.timeout, ConnectionRefusedError, OSError, UnicodeDecodeError):
        return None


# ── Renderers ──────────────────────────────────────────────────────────

def _box(title: str, lines: list[str], color: bool = True, stream: TextIO | None = None) -> str:
    w = min(72, _width() - 2)
    inside = w - 2
    border = magenta("┌" + "─" * inside + "┐", enabled=color, stream=stream)
    heading = "│" + bold(cyan(title.center(inside), enabled=color, stream=stream), enabled=color, stream=stream) + "│"
    sep = magenta("├" + "─" * inside + "┤", enabled=color, stream=stream)
    rows = [border, heading, sep]
    for line in lines:
        wrapped = textwrap.fill(str(line), width=inside - 2)
        for part in wrapped.split("\n"):
            rows.append("│ " + part.ljust(inside - 2) + " │")
    rows.append(magenta("└" + "─" * inside + "┘", enabled=color, stream=stream))
    return "\n".join(rows)


def render_scan_results(
    host: str,
    open_ports: list[tuple[int, str]],
    banners: dict[int, str | None],
    color: bool = True,
    stream: TextIO | None = None,
) -> str:
    if not open_ports:
        return _box(f"SCAN REPORT — {host}", [yellow("No open ports found.", enabled=color, stream=stream)], color, stream)
    lines = [f"Target: {cyan(host, enabled=color, stream=stream)}  |  Open: {green(str(len(open_ports)), enabled=color, stream=stream)}"]
    lines.append("")
    for port, service in open_ports:
        srv = f"{service} ({port})"
        banner = banners.get(port)
        if banner:
            lines.append(f"  ▸ {green(srv, enabled=color, stream=stream)} → {yellow(banner[:60], enabled=color, stream=stream)}")
        else:
            lines.append(f"  ▸ {green(srv, enabled=color, stream=stream)}")
    return _box(f"SCAN REPORT — {host}", lines, color, stream)


def render_dns_results(info: dict, color: bool = True, stream: TextIO | None = None) -> str:
    lines = [f"Hostname: {cyan(info['hostname'], enabled=color, stream=stream)}"]
    if info["ipv4"]:
        lines.append("")
        lines.append(green("IPv4 Addresses:", enabled=color, stream=stream))
        for ip in info["ipv4"]:
            ptr = reverse_dns(ip)
            extra = f" → {yellow(ptr, enabled=color, stream=stream)}" if ptr else ""
            lines.append(f"  ▸ {ip}{extra}")
    if info["ipv6"]:
        lines.append("")
        lines.append(cyan("IPv6 Addresses:", enabled=color, stream=stream))
        for ip in info["ipv6"]:
            lines.append(f"  ▸ {ip}")
    return _box("DNS LOOKUP", lines, color, stream)


# ── Main CLI ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tankhack",
        description="TANK-HACK — Armored Reconnaissance Framework",
        epilog="Example: tankhack scan example.com -p 22,80,443 -T 100",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Global options
    p.add_argument("--no-color", action="store_true", help="Disable colors")
    p.add_argument("-o", "--output", help="Write results to file")
    p.add_argument("--version", action="version", version=f"TANK-HACK v{__version__}")

    sub = p.add_subparsers(dest="command", required=True)

    # scan
    scan = sub.add_parser("scan", help="Port scan a target")
    scan.add_argument("target", help="Hostname or IP address")
    scan.add_argument("-p", "--ports", help="Port range (e.g. 22,80,443 or 1-1000)")
    scan.add_argument("-T", "--timeout", type=float, default=2.0, help="Timeout per port (default: 2.0s)")
    scan.add_argument("-t", "--threads", type=int, default=50, help="Max threads (default: 50)")
    scan.add_argument("--top", type=int, default=0, help="Scan top N common ports")
    scan.add_argument("-b", "--banners", action="store_true", help="Grab service banners")
    scan.add_argument("-f", "--format", choices=("terminal", "json", "text"), default="terminal")

    # dns
    dns = sub.add_parser("dns", help="DNS lookup")
    dns.add_argument("target", help="Hostname or IP address")

    # ping
    ping = sub.add_parser("ping", help="Ping a host")
    ping.add_argument("target", help="Hostname or IP address")
    ping.add_argument("-c", "--count", type=int, default=4, help="Ping count (default: 4)")

    # quick
    quick = sub.add_parser("quick", help="Quick scan (top 20 ports + DNS + ping)")
    quick.add_argument("target", help="Hostname or IP address")

    return p


def parse_ports(raw: str) -> list[int]:
    ports: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            ports.update(range(int(lo.strip()), int(hi.strip()) + 1))
        else:
            ports.add(int(part))
    return sorted(ports)


TOP_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]


def main(argv: Sequence[str] | None = None, *, stdin: TextIO | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    color = not args.no_color

    # Show banner
    stdout.write(show_banner(color=color, stream=stdout))

    result_str = ""
    exit_code = 0

    try:
        if args.command == "scan":
            target = args.target.strip()
            # Resolve target
            stdout.write(f"  {bold('Target:', enabled=color, stream=stdout)} {cyan(target, enabled=color, stream=stdout)}\n")
            info = dns_lookup(target)
            if info["ipv4"]:
                target_ip = info["ipv4"][0]
                stdout.write(f"  {bold('Resolved:', enabled=color, stream=stdout)} {yellow(target_ip, enabled=color, stream=stdout)}\n\n")
            elif info["ipv6"]:
                target_ip = info["ipv6"][0]
                stdout.write(f"  {bold('Resolved (IPv6):', enabled=color, stream=stdout)} {yellow(target_ip, enabled=color, stream=stdout)}\n\n")
            else:
                target_ip = target

            # Determine ports
            if args.ports:
                ports = parse_ports(args.ports)
            elif args.top > 0:
                ports = TOP_PORTS[:args.top]
            else:
                ports = TOP_PORTS[:20]

            stdout.write(f"  {bold('Scanning:', enabled=color, stream=stdout)} {len(ports)} ports\n")
            stdout.write(f"  {bold('Threads:', enabled=color, stream=stdout)} {args.threads}\n\n")

            start = time.time()
            open_ports = scan_ports(target_ip, ports, args.timeout, args.threads, stream=stdout)
            elapsed = time.time() - start

            # Banner grab
            banners: dict[int, str | None] = {}
            if args.banners and open_ports:
                stdout.write(f"\n  {bold('Grabbing banners...', enabled=color, stream=stdout)}\n")
                for port, _ in open_ports:
                    banner = grab_banner(target_ip, port)
                    banners[port] = banner
                    if banner:
                        stdout.write(f"  ▸ Port {port}: {yellow(banner[:60], enabled=color, stream=stdout)}\n")

            result_str = render_scan_results(target, open_ports, banners, color, stream=stdout)
            result_str += f"\n\n  {bold('Completed:', enabled=color, stream=stdout)} {len(open_ports)} open ports in {elapsed:.1f}s\n"
            stdout.write(result_str)

        elif args.command == "dns":
            target = args.target.strip()
            info = dns_lookup(target)
            if not info["ipv4"] and not info["ipv6"]:
                stdout.write(yellow(f"  ✗ Could not resolve: {target}\n", enabled=color, stream=stdout))
                exit_code = 1
            else:
                result_str = render_dns_results(info, color, stream=stdout)
                stdout.write(result_str)

        elif args.command == "ping":
            target = args.target.strip()
            stdout.write(f"  {bold('Pinging:', enabled=color, stream=stdout)} {cyan(target, enabled=color, stream=stdout)} ({args.count} packets)\n\n")
            ok, ms = ping_check(target, args.count)
            if ok:
                stdout.write(green(f"  ✓ Host is reachable — avg {ms}ms\n", enabled=color, stream=stdout))
            else:
                stdout.write(yellow(f"  ✗ Host unreachable or ping not allowed\n", enabled=color, stream=stdout))
                exit_code = 1

        elif args.command == "quick":
            target = args.target.strip()
            info = dns_lookup(target)
            target_ip = info["ipv4"][0] if info["ipv4"] else target
            stdout.write(f"  {bold('QUICK RECON:', enabled=color, stream=stdout)} {cyan(target, enabled=color, stream=stdout)}\n\n")

            # Ping
            stdout.write(f"  {bold('▸ Ping check...', enabled=color, stream=stdout)}\n")
            ok, ms = ping_check(target)
            stdout.write(f"    {'✓ Online' if ok else '✗ Offline/blocked'} ({ms}ms)\n\n")

            # DNS
            stdout.write(f"  {bold('▸ DNS resolution...', enabled=color, stream=stdout)}\n")
            if info["ipv4"]:
                for ip in info["ipv4"]:
                    stdout.write(f"    {ip}\n")
            stdout.write("\n")

            # Port scan (top 20)
            stdout.write(f"  {bold('▸ Scanning top 20 ports...', enabled=color, stream=stdout)}\n")
            open_ports = scan_ports(target_ip, TOP_PORTS[:20], progress=False, stream=stdout)
            stdout.write(f"\n  {bold(f'  → {len(open_ports)} open ports found', enabled=color, stream=stdout)}\n")
            for port, svc in open_ports:
                stdout.write(f"    ▸ {svc} ({port})\n")

            result_str = f"Quick recon of {target} complete."

        # Write output file
        if args.output and result_str:
            Path(args.output).write_text(result_str, encoding="utf-8")

    except (OSError, ValueError, KeyboardInterrupt) as exc:
        print(red(f"\n  ✗ Error: {exc}", enabled=color, stream=stderr), file=stderr)
        return 2

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
