import socket
import argparse
import sys
import threading
from colorama import init, Fore

init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX
RED = Fore.RED

closed_ports = []


def is_port_open(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((host, port))
            if result == 0:
                return port
            else:
                closed_ports.append(port)
            return None
    except (socket.timeout, ConnectionRefusedError):
        return None



def scan_ports(target_host, ports, open_ports):
    for port in ports:
        port_result = is_port_open(target_host, port)
        open_ports.append(port_result)
       

def main():
    parser = argparse.ArgumentParser(description="Shitty port scanner that kinda works sometimes maybe")
    parser.add_argument("--target", "-t", dest="host", help="target host to scan.")
    parser.add_argument("--ports", "-p", dest="port_range", default="1-65535",
                        help="specify port range to scan (e.g. 2000-3000). Default is 1-65535 (all ports).")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        print("No arguments provided. Exiting.")
        sys.exit(1)  # You can provide an exit status (usually an integer)

    host = args.host
    port_range = args.port_range
    if "-" in port_range:
        start_port, end_port = map(int, port_range.split("-"))
        ports = [p for p in range(start_port, end_port + 1)]
    else:
        ports = [int(port_range)]

    print(f"{GRAY}[DEBUG] scanning ports for {host}...{RESET}")

    num_threads = 10
    ports_per_thread = len(ports) // num_threads

    threads = []
    open_ports = []

    for i in range(num_threads):
        start_idx = i * ports_per_thread
        end_idx = (i + 1) * ports_per_thread
        t = threading.Thread(target=scan_ports, args=(host, ports[start_idx:end_idx], open_ports))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    open_ports = [port for port in open_ports if port is not None]
    open_ports.sort()
    closed_port_count = len(closed_ports)
    for port in open_ports:
        print(f"{GREEN}[+] Port {port} is open{RESET}")
    print(f"{RED}[-] There are {closed_port_count} closed ports")


if True:
    main()
