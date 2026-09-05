#!/bin/bas
set -e
set -u
set -o pipefail
echo "      PERMISSION & PRIVILEGE AUDIT TOOL"
echo "==============================================="
echo "Starting System Scan... (This might take a min)"
echo "==="
echo "[CRITICAL] Auditing for unauthorised UID 0 (root) accounts..."
uid_zero_accounts=$(awk -F: '$3 == "0" && $1 != "root" {print $1}' /etc/passwd)
if [ -z "$uid_zero_accounts" ]; then
	echo "  -> OK: No rogue root accounts founf."
else
	echo "  -> FINDING: Rogue UID 0 accounts detected!"
fi
echo ""
echo "[WARNING] Auditing for SUID/SGID Binaries..."
find / -path /mnt -prune -o -type f -perm /6000 -printf "  -> USER: %-10u PATH: %P\N" 2>/dev/null || true # true prevents set -e from crashing the script. 
echo ""
echo "[CRITICAL] Auditing for World-Writable Files/Directories (excluding /tmp)..."
find / -path /mnt -prune -o -path /tmp -prune -o -path /proc -prune -o -path /sys -prune -o -perm -0002 -print 2>/dev/null | while read -r file; do
	echo "  -> WORLD-WRITABLE: $file"
done || true
echo ""
echo "            AUDIT COMPLETE"
