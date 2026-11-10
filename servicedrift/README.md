# ServiceDrift

**A Python-Based Local TCP Service Availability and Baseline Drift Monitor**

## Overview

ServiceDrift is a defensive monitoring tool that checks selected localhost TCP ports and identifies connectivity changes between earlier and later observations.

It combines concurrent TCP checking, UTC timestamped CSV reports, binary snapshot storage, and baseline comparison.

## Problem It Solves

A single TCP connection check tells an administrator whether a selected endpoint is reachable at a particular moment.

However, troubleshooting often requires comparing observations collected at different times.

ServiceDrift addresses this problem by storing a baseline and identifying when a previously reachable local TCP service stops accepting connections, or when a previously closed port becomes reachable.

## Features

- Multithreaded TCP connectivity checks
- Configurable port lists and worker counts
- Input validation and connection-error handling
- UTC timestamped CSV reporting
- Binary snapshot creation and validation
- Versioned snapshot format using Python's `struct` module
- Baseline-to-current comparison
- Connectivity-change classification
- Automated localhost TCP integration testing

## Technologies

Python 3 and its standard-library modules:

`socket`, `threading`, `queue`, `argparse`, `csv`, `datetime`, `struct`, and `unittest`.

No third-party Python packages are required.

## Quick Start

From the project directory:

**1. Check selected local ports**

```bash
python3 threaded_checker_timed.py --ports 8000 8001 --workers 2 --report baseline.csv
```

**2. Create a binary snapshot**

```bash
python3 snapshot_writer.py --input baseline.csv --output baseline.lsnp
```

**3. Read the snapshot**

```bash
python3 snapshot_reader_v2.py baseline.lsnp
```

After running another check on the same ports, save it as `current.csv`.

**4. Create the current snapshot**

```bash
python3 snapshot_writer.py --input current.csv --output current.lsnp
```

**5. Compare observations**

```bash
python3 baseline_compare.py --baseline baseline.lsnp --current current.lsnp --report change_report.csv
```

## Verified Demonstration

During a controlled localhost test on 10 November 2026, port 42095 was initially reachable and subsequently refused TCP connections.

ServiceDrift classified the observations as:

```text
Port 37143: CLOSED -> CLOSED [UNCHANGED]
Port 42095: OPEN -> CLOSED [BECAME_UNAVAILABLE]
Compared 2 monitored ports.
CSV report saved: change_report.csv
```

The test demonstrated both an unchanged service state and a connectivity transition.

## Automated Testing

Run the repository's tests with:

```bash
python3 -m unittest discover -s tests -v
```

The broader development environment also had eight passing tests covering the original TCP checker, status classification, and CSV processing.

## Real-World Applications

The design is relevant to routine availability checking and troubleshooting on development machines, university ICT laboratory systems, and small organizations' locally managed services.

The current implementation has been demonstrated on localhost and has not been deployed as an organization-wide monitoring service.

## Limitations

- Supports explicitly selected localhost TCP ports.
- Does not identify software vulnerabilities or service versions.
- Does not replace Nmap or a full monitoring platform.
- Cannot establish why a connection state changed.
- The custom binary snapshot format does not provide cryptographic integrity or authentication.
- Monitoring is performed through manually initiated runs rather than a continuously running monitoring agent.

## Project Status

**Version 1 — Functional localhost prototype with verified end-to-end baseline comparison.**

## Author

Developed as part of practical cybersecurity and security-tool-development training during SIWES.
