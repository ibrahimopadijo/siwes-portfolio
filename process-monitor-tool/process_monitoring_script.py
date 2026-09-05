import subprocess
print("PROCESS MONITORING")
print("Scanning for high-memory processes...\n")

process_call = subprocess.run(
	['ps', '-eo', 'pid,user,%cpu,%mem,command'],
	capture_output=True,
	text=True
)

raw_text = process_call.stdout
lines = raw_text.split('\n')
for line in lines:
	if line == "":
		continue
	columns = line.split(None, 4)
	if len(columns) < 5:
		continue

	pid = columns[0]
	user = columns[1]
	cpu_text = columns[2]
	mem_text = columns[3]
	command = columns[4]

	try:
		cpu_number = float(cpu_text)
		mem_number = float(mem_text)
	except ValueError:
		continue
	if mem_number > 10.0:
		print(f"[WARNING] High Memory Found!")
		print(f" -> PID: {pid} | User: {user} | Memory: {mem_number}% | Command: {command}")
		print("-" * 40)
print("\nScan Complete.")
