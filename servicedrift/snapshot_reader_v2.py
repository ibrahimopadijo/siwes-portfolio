import argparse
import struct
from datetime import datetime, timedelta, timezone

MAGIC = b"LSNP"
VERSION = 2

HEADER_FORMAT = "!4sBQQH"
RECORD_FORMAT = "!HB"

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

MAX_RECORDS = 1000

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

STATUS_NAMES = {
        0: "CLOSED",
        1: "OPEN",
        2: "TIMEOUT",
        3: "ERROR",
        4: "UNKNOWN"
}

def read_snapshot(filename):
    maximum_size = HEADER_SIZE + MAX_RECORDS * RECORD_SIZE

    with open(filename, "rb") as file:
        data = file.read(maximum_size + 1)
    if len(data) > maximum_size:
        raise ValueError("Snapshot exceeds the size limit")
    if len(data) < HEADER_SIZE:
        raise ValueError("Incomplete snapshot header")

    magic, version, started_us, completed_us, count = struct.unpack_from(HEADER_FORMAT, data, 0)

    if magic != MAGIC:
        raise ValueError("Invalid LSNP magic identifier")
    if version != VERSION:
        raise ValueError(f"Unsupported snapshot version: {version}")
    if not 1 <= count <= MAX_RECORDS:
        raise ValueError(f"Invalid record count: {count}")
    if completed_us < started_us:
        raise ValueError("scan completion precedes scan start")

    expected_size = HEADER_SIZE + count * RECORD_SIZE

    if len(data) != expected_size:
        raise ValueError(f"Snapshot length is {len(data)} bytes; expected {expected_size}")
    try:
        started = EPOCH + timedelta(microseconds=started_us)
        completed = EPOCH + timedelta(microseconds=completed_us)
    except OverflowError as error:
        raise ValueError("Invalid timestamp range") from error

    results = {}

    records_data = memoryview(data)[HEADER_SIZE:]

    for port, code in struct.iter_unpack(RECORD_FORMAT, records_data):
        
        if not 1 <= port <= 65535:
            raise ValueError(f"Invalid stored port: {port}")
        if code not in STATUS_NAMES:
            raise ValueError(f"Unknown status code: {code}")
        if port in results:
            raise ValueError(f"Duplicate stored port: {port}")

        results[port] = STATUS_NAMES[code]
    return{
            "scan_started_at_utc": started.isoformat(timespec="microseconds"),
            "scan_completed_at_utc": completed.isoformat(timespec="microseconds"),
            "results": results
    }

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Read a ServiceDrift V2 binary snapshot")

    parser.add_argument("snapshot", help="Binary snapshot filename")

    args = parser.parse_args()

    try:
        snapshot = read_snapshot(args.snapshot)
    except (OSError, ValueError, struct.error) as error:
        parser.error(str(error))

    print("Scan started (UTC):", snapshot["scan_started_at_utc"])
    print("Scan completed (UTC):", snapshot["scan_completed_at_utc"])

    for port in sorted(snapshot["results"]):
        print(f"Port {port}: {snapshot['results'][port]}")

