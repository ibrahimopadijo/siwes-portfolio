
import argparse
import csv
from datetime import datetime

from snapshot_reader_v2 import read_snapshot


def classify_change(before, after):

    if before not in ("OPEN", "CLOSED") or after not in ("OPEN", "CLOSED"):
        return "INCONCLUSIVE"

    if before == after:
        return "UNCHANGED"

    if before == "OPEN" and after == "CLOSED":
        return "BECAME_UNAVAILABLE"

    return "BECAME_REACHABLE"


def compare_snapshots(baseline_filename, current_filename, report_filename):

    baseline = read_snapshot(baseline_filename)
    current = read_snapshot(current_filename)

    old_results = baseline["results"]
    new_results = current["results"]

    old_ports = set(old_results)
    new_ports = set(new_results)

    if old_ports != new_ports:
        missing = sorted(old_ports - new_ports)
        added = sorted(new_ports - old_ports)

        raise ValueError(
            f"Different monitored port sets: missing={missing}, added={added}"
        )

    baseline_time = datetime.fromisoformat(
        baseline["scan_started_at_utc"]
    )

    current_time = datetime.fromisoformat(
        current["scan_started_at_utc"]
    )

    if current_time < baseline_time:
        raise ValueError("Current snapshot predates the baseline")

    fieldnames = [
        "port",
        "baseline_status",
        "current_status",
        "assessment",
        "baseline_scan_completed_at_utc",
        "current_scan_completed_at_utc"
    ]

    rows = []

    for port in sorted(old_results):

        previous_status = old_results[port]
        current_status = new_results[port]

        assessment = classify_change(
            previous_status,
            current_status
        )

        rows.append({
            "port": port,
            "baseline_status": previous_status,
            "current_status": current_status,
            "assessment": assessment,
            "baseline_scan_completed_at_utc":
                baseline["scan_completed_at_utc"],
            "current_scan_completed_at_utc":
                current["scan_completed_at_utc"]
        })

    with open(report_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Compare ServiceDrift baseline and current snapshots"
    )

    parser.add_argument("--baseline", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--report", default="change_report.csv")

    args = parser.parse_args()

    try:
        changes = compare_snapshots(
            args.baseline,
            args.current,
            args.report
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    for row in changes:
        print(
            f"Port {row['port']}: "
            f"{row['baseline_status']} -> {row['current_status']} "
            f"[{row['assessment']}]"
        )

    print(f"Compared {len(changes)} monitored ports.")
    print(f"CSV report saved: {args.report}")

