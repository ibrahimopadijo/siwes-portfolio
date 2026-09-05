# Memory Allocation & Pointer Crash Demo

A program engineered in Go to demonstrate how operating systems manage live process memory, highlighting the exact vulnerability that leads to Denial of Service (DoS) and memory corruption exploits. 

## Key Capabilities
* **Memory Allocation:** Explicitly allocates memory on the Stack (temporary) and the Heap (dynamic).
* **Hardware Addressing:** Uses pointers to expose the literal hardware addresses in RAM.
* **Intentional SegFault:** Engineers a deliberate `nil` pointer dereference to force a `SIGSEGV` kernel panic.

## Usage
```bash
go run stack_heap_pointers.go
