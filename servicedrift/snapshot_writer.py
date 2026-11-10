import argparse
import csv
import struct
from datetime import datetime, timedelta, timezone

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

MAGIC = b"LSNP"
VERSION = 2

HEADER_FORMAT = "!4sBQQH"
RECORD_FORMAT = "!HB"

MAX_RECORDS = 1000

STATUS_CODES = {
        "CLOSED": 0,
        "OPEN": 1,
        "TIMEOUT": 2,
        "ERROR": 3,
        "UNKNOWN": 4
}

def timestamp_to_microseconds(text):
    moment = datetime.fromisoformat(text)

    if moment.tzinfo is None:
        raise ValueError("Timestamp must include timezone information")
    if moment.utcoffset() != timedelta(0):
        raise ValueError("Timestamp must be in UTC")

    elapsed = moment - EPOCH

    if elapsed.days < 0:
        raise ValueError("Timestamp before Unix epoch")


    return((elapsed.days * 86400 + elapsed.seconds) * 1_000_000 + elapsed.microseconds)

def load_scan_csv(filename):
    results = {}
    scan_times = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
                "port",
                "status",
                "scan_started_at_utc",
                "scan_completed_at_utc"
        }

        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError("Missing required CSV columns")

        for line_number, row in enumerate(reader, start=2):
            try:
                port = int(row["port"])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid port on the line {line_number}")

            if not 1 <= port <= 65535:
                raise ValueError(f"Port outside range on line {line_number}")

            if port in results:
                raise ValueError(f"Duplicate port: {port}")

            status = row["status"]

            if status is None:
                raise ValueError(f"Missing status on line {line_number}")

            if status.startswith("ERROR:"):
                status = "ERROR"

            if status not in STATUS_CODES:
                raise ValueError(f"Invalid status: {status}")

            start_us = timestamp_to_microseconds(row["scan_started_at_utc"])
            end_us = timestamp_to_microseconds(row["scan_completed_at_utc"])

            if end_us < start_us:
                raise ValueError("Completion time precedes start time")

            if scan_times is None:
                scan_times = (start_us, end_us)
            elif scan_times != (start_us, end_us):
                raise ValueError("Inconsistent scan timestamps")

            results[port] = status

            if len(results) > MAX_RECORDS:
                raise ValueError("Too many records")
    if not results:
        raise ValueError("CSV contains no records")

    return results, scan_times[0], scan_times[1]

def write_snapshot(input_filename, output_filename):

    results, started_us, completed_us = load_scan_csv(input_filename)
    header = struct.pack(
            HEADER_FORMAT,
            MAGIC,
            VERSION,
            started_us,
            completed_us,
            len(results)
    )

    with open(output_filename, "wb") as file:
        file.write(header)

        for port in sorted(results):
            status = results[port]
            status_code = STATUS_CODES[status]

            record = struct.pack(
                    RECORD_FORMAT,
                    port,
                    status_code
            )

            file.write(record)
    return len(results)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Created a timestamped ServiceDrift snapshot")

    parser.add_argument("--input", required=True,)

    parser.add_argument("--output", default="baseline_v2.lsnp",)

    args = parser.parse_args()

    try:
        count = write_snapshot(args.input, args.output)
    except (OSError, ValueError, struct.error, OverflowError) as error:
        parser.error(str(error))


    print("Binary snapshot created successfully!")
    print(f"Records written: {count}")
    print(f"Snapshot saved to: {args.output}")
