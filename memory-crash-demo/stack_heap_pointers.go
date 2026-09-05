package main
import "fmt"
func main() {
	stackVar := 42  // 1. Stack Allocation

	heapPtr := new(int)  // 2. Heap Allocation
	*heapPtr = 100

	fmt.Println(" MEMORY ADDRESSES ") // 3. Pointers
	fmt.Printf("Stack Address: %p\n", &stackVar)
	fmt.Printf("Heap Address: %p\n", heapPtr)

	fmt.Println("\n TRIGERRING MEMORY ERROR ") // 4. To trigger memory error
	fmt.Println("Attempting to write to a 'nil' pointer")

	var dangerousPtr *int = nil
	*dangerousPtr = 99 
}
