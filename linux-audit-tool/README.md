# Linux Permission & Privilege Audit Tool

A defensive SOC automation script designed to hunt for privilege escalation vectors on a Linux filesystem. Built with strict defensive execution flags (`set -e`, `set -u`, `set -o pipefail`).

## Key Capabilities
* **Rogue Admin Hunting:** Parses `/etc/passwd` to identify unauthorized accounts holding UID 0 (root) privileges.
* **SUID/SGID Scanning:** Evaluates octal permissions (`/6000`) to find binaries that could be exploited.
* **Vulnerability Flagging:** Scans for world-writable files (`-0002`), filtering out virtual filesystems.
* **Environment Aware:** Includes `-prune` parameters to safely execute in WSL environments.

## Usage
```bash
bash permission_audit.sh
