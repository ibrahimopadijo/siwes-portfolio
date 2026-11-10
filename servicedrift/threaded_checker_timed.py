import argparse
import socket
import threading
import csv
from queue import Queue
from datetime import datetime, timezone

HOST = "127.0.0.1"

q = Queue()

results = {}
results_lock = threading.Lock()

def valid_port(value):
    try:
        port = int(value)

    except ValueError:
        raise argparse.ArgumentTypeError("Port must be a whole number")

    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")

    return port

def valid_workers(value):
    try:
        worker = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Worker should be a whole number")
    if not 1 <= worker <= 16:
        raise argparse.ArgumentTypeError("Workers should be between 1 and 16")
    return worker


def check_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((HOST, port))
            return "OPEN"
    except ConnectionRefusedError:
        return "CLOSED"
    except socket.timeout:
        return "TIMEOUT"
    except OSError as error:
        return f"ERROR: {error}"

def threader():
    while True:
        port = q.get()

        try:
            if port is None:
                break
            try:
                result = check_port(port)
            except Exception as error:
                result = f"ERROR: {type(error).__name__}: {error}"

            with results_lock:
                results[port] = result

        finally:
            q.task_done()

parser = argparse.ArgumentParser(description="Threaded localhost TCP service checker")

parser.add_argument(
        "-p",
        "--ports",
        nargs="+",
        type=valid_port,
        default=[8000, 8001, 8002],
        help="One or more local TCP ports"
)

parser.add_argument(
        "--report",
        default="tcp_results_cli.csv",
        help="Filename for the CSV report"
)

parser.add_argument(
        "--workers",
        type=valid_workers,
        default=2,
        help="Number of workers threads (1-16)"
)

args = parser.parse_args()

if len(args.ports) != len(set(args.ports)):
    parser.error("Duplicate port numbers are not allowed")

scan_started_at = datetime.now(timezone.utc)

threads = []

for number in range(args.workers):
    t = threading.Thread(
        target=threader,
        name=f"Worker-{number + 1}"
    )

    threads.append(t)
    t.start()

print(f"Worker threads created: {len(threads)}")

for port in args.ports:
    q.put(port)

q.join()

for _ in threads:
    q.put(None)

for t in threads:
    t.join()
scan_completed_at = datetime.now(timezone.utc)

started_text = scan_started_at.isoformat(timespec="microseconds")
completed_text = scan_completed_at.isoformat(timespec="microseconds")

print("\nTCP Service Check Results")
print("-------------------------")

for port in sorted(results):
    print(f"Port {port}: {results[port]}")

with open(args.report, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
            "port",
            "status",
            "scan_started_at_utc",
            "scan_completed_at_utc"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()

    for port in sorted(results):
        writer.writerow({
            "port": port,
            "status": results[port],
            "scan_started_at_utc": started_text,
            "scan_completed_at_utc": completed_text
    })

print("All checks completed")
print("CSV report saved successfully!")
print(f"Scan started (UTC): {started_text}")
print(f"Scan completed (UTC): {completed_text}")

duration = (scan_completed_at - scan_started_at).total_seconds()

print(f"Scan duration: {duration:.3f} seconds")
