<p align="center">
  <img src="https://img.shields.io/badge/TANK--HACK-v2.1.0-red?style=for-the-badge&labelColor=black">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&labelColor=black">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge&labelColor=black">
</p>

<pre align="center">
  ████████╗ █████╗ ███╗   ██╗██╗  ██╗    ██╗  ██╗ █████╗  ██████╗██╗  ██╗
  ╚══██╔══╝██╔══██╗████╗  ██║██║ ██╔╝    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝
     ██║   ███████║██╔██╗ ██║█████╔╝     ███████║███████║██║     █████╔╝ 
     ██║   ██╔══██║██║╚██╗██║██╔═██╗     ██╔══██║██╔══██║██║     ██╔═██╗ 
     ██║   ██║  ██║██║ ╚████║██║  ██╗    ██║  ██║██║  ██║╚██████╗██║  ██╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
</pre>

<p align="center">
  <strong>ARMORED RECONNAISSANCE FRAMEWORK</strong><br>
  <em>Lightweight Network Recon Tool — because real hackers drive tanks.</em>
</p>

---

## ⚙️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/TANK-HACK.git
cd TANK-HACK
chmod +x tankhack.py
```

No external dependencies — uses only Python standard library.

## 🎯 Commands

### `scan` — Port Scanner

```bash
python3 tankhack.py scan example.com
python3 tankhack.py scan 192.168.1.1 -p 22,80,443,3306
python3 tankhack.py scan 192.168.1.1 -p 1-1000 -T 1.5 -t 100
python3 tankhack.py scan example.com --top 50 -b
python3 tankhack.py scan example.com -f json -o results.json
```

| Flag | Description |
|------|-------------|
| `-p` | Ports: `22,80,443` or `1-1000` |
| `-T` | Timeout per port (default: 2.0s) |
| `-t` | Thread count (default: 50) |
| `--top N` | Scan top N common ports |
| `-b` | Grab service banners |
| `-f` | Output format: `terminal`, `json`, `text` |
| `-o` | Save results to file |

### `dns` — DNS Lookup

```bash
python3 tankhack.py dns example.com
```

Resolves IPv4, IPv6, and performs reverse DNS.

### `ping` — Ping Check

```bash
python3 tankhack.py ping example.com -c 4
```

### `quick` — Full Recon in One Shot

```bash
python3 tankhack.py quick example.com
```

Runs ping + DNS scan + top 20 port scan in sequence.

## 🎨 Features

- 🎯 **Threaded port scanning** — fast multi-threaded TCP connect scan
- 🐉 **Tank ASCII art** — because style matters
- 🏷️ **Service detection** — identifies common ports
- 📜 **Banner grabbing** — pull service banners from open ports
- 🌐 **DNS resolution** — IPv4, IPv6, and reverse DNS
- 📊 **Multiple output formats** — terminal, JSON, CSV-ready
- 📁 **File output** — save results for later
- 🎨 **Colorful terminal output** — with `--no-color` for scripts

## ⚠️ Disclaimer

> This tool is intended for **authorized security testing** and **educational purposes only**.
> Do not use against targets without explicit permission.
> The author is not responsible for misuse.

---

<p align="center">
  <sub>Built with ⚔️ by a tank operator</sub>
</p>
