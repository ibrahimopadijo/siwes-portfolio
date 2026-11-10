# ServiceDrift — Technical Design

## Architecture

The project consists of four primary programs:

- `threaded_checker_timed.py`: Performs concurrent TCP connection checks and generates UTC timestamped CSV reports.
- `snapshot_writer.py`: Validates a scan report and serializes its observations into a binary snapshot.
- `snapshot_reader_v2.py`: Validates and decodes a version-2 binary snapshot.
- `baseline_compare.py`: Compares two snapshots and produces a change report.

## TCP Checking

The checker uses Python TCP sockets to test selected ports on `127.0.0.1`.

A shared task queue distributes ports among worker threads. A thread lock protects updates to the shared results dictionary.

## Binary Snapshot Format

The custom LSNP version-2 format uses network byte order.

**Header:** `!4sBQQH` — 23 bytes.

- Four-byte magic identifier: `LSNP`
- One-byte format version: `2`
- Eight-byte scan-start UTC timestamp
- Eight-byte scan-completion UTC timestamp
- Two-byte record count

Timestamps represent microseconds elapsed since the Unix epoch.

**Record:** `!HB` — three bytes.

- Two-byte TCP port
- One-byte status code

Status codes:

| Value | Status |
|---|---|
| 0 | CLOSED |
| 1 | OPEN |
| 2 | TIMEOUT |
| 3 | ERROR |
| 4 | UNKNOWN |

The reader validates record counts, expected file length, port values, duplicate records, status codes and relevant snapshot metadata.

## Baseline Comparison

The comparison engine requires matching monitored port sets.

The results are interpreted as follows:

| Baseline | Current | Assessment |
|---|---|---|
| OPEN | CLOSED | BECAME_UNAVAILABLE |
| CLOSED | OPEN | BECAME_REACHABLE |
| OPEN | OPEN | UNCHANGED |
| CLOSED | CLOSED | UNCHANGED |
| Any uncertain observation | Any state | INCONCLUSIVE |

The result represents a change in TCP connectivity, not proof of a particular application failure or security incident.

## Scope

ServiceDrift V1 is a localhost-focused availability and baseline-comparison tool. Network-wide discovery, web application vulnerability testing, authenticated monitoring and real-time alerting are outside this version's scope.
