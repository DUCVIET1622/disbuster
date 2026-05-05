#!/usr/bin/env python3
import socket
import ssl
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# ==============================
# Fix màu Windows
# ==============================
try:
    from colorama import init
    init()
except:
    pass

# ==============================
# Colors
# ==============================
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

# ==============================
# Banner
# ==============================
def banner():
    print(CYAN + r"""
   ____  _     ____            _            
  |  _ \(_)___| __ ) _   _ ___| |_ ___ _ __ 
  | | | | / __|  _ \| | | / __| __/ _ \ '__|
  | |_| | \__ \ |_) | |_| \__ \ ||  __/ |   
  |____/|_|___/____/ \__,_|___/\__\___|_|   

""" + RESET)
    print(YELLOW + "  DirBuster PRO - Mini Web Scanner" + RESET)
    print(RED + "  Author: DUCVIET1622\n" + RESET) 
    print(RED + "  github:https://github.com/DUCVIET1622" + RESET)    
  

# ==============================
def build_request(host, path):
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: Mozilla/5.0\r\n"
        f"Connection: close\r\n\r\n"
    )

# ==============================
def check_path(host, port, path, use_https):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)

        if use_https:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.connect((host, port))
        sock.send(build_request(host, path).encode())

        resp = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            resp += chunk

        sock.close()

        if not resp:
            return "", path

        resp = resp.decode(errors="ignore")
        status_line = resp.split("\r\n")[0]
        parts = status_line.split()

        if len(parts) < 2:
            return "", path

        return parts[1], path

    except Exception as e:
        print(RED + f"[ERROR] {path} -> {e}" + RESET)
        return "", path

# ==============================
def scan(target, port, paths, threads, use_https):
    print(CYAN + f"\n[*] Target  : {target}" + RESET)
    print(CYAN + f"[*] Port    : {port}" + RESET)
    print(CYAN + f"[*] Threads : {threads}" + RESET)
    print(CYAN + f"[*] HTTPS   : {use_https}" + RESET)
    print(CYAN + f"[*] Paths   : {len(paths)}\n" + RESET)

    found = []
    total = len(paths)
    checked = 0
    lock = Lock()

    def worker(path):
        nonlocal checked

        if not path.startswith("/"):
            path = "/" + path

        code, path = check_path(target, port, path, use_https)

        with lock:
            checked += 1
            print(YELLOW + f"[{checked}/{total}]" + RESET, end="\r")

        if code in ["200", "301", "302", "403", "401"]:
            print(GREEN + f"[+] {code} {path}" + RESET)
            found.append((code, path))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(worker, paths)

    print("\n" + "=" * 50)
    print(GREEN + f"[✓] Found {len(found)} paths:\n" + RESET)

    for code, path in found:
        print(WHITE + f"  [{code}] {path}" + RESET)

# ==============================
def default_paths():
    return [
        "admin", "login", "dashboard", "robots.txt",
        ".env", ".git", "backup", "config",
        "wp-admin", "admin.php", "login.php"
    ]

# ==============================
# MAIN (interactive)
# ==============================
def main():
    banner()

    try:
        target = input(" Enter target (vd: example.com): ").strip()
        if not target:
            print(RED + "[-] cannot be left blank!" + RESET)
            input("Enter to exit...")
            return

        port_input = input(" Port (Enter = 80): ").strip()
        port = int(port_input) if port_input else 80

        https_input = input(" use HTTPS? (y/n): ").lower()
        use_https = https_input == "y"

        thread_input = input(" Threads (Enter = 10): ").strip()
        threads = int(thread_input) if thread_input else 10

        custom = input(" enter paths (separated by commas) or Enter to use default: ").strip()
        if custom:
            paths = custom.split(",")
        else:
            paths = default_paths()

        scan(target, port, paths, threads, use_https)

    except Exception as e:
        print(RED + f"[FATAL ERROR] {e}" + RESET)

    input("\nPress Enter to exit...")

# ==============================
if __name__ == "__main__":
    main()