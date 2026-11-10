import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(("127.0.0.1", 0))

    assigned_port = server.getsockname()[1]

    server.listen(1)

    print(f"Test server listening on port {assigned_port}")

    input("Press Enter to stop the test server...")

