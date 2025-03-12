from websockets.sync.client import connect

HOST_ADDRESS = "ws://localhost:8000/logview"


def main():
    print(f"Connecting to logview of {HOST_ADDRESS}...")
    with connect(HOST_ADDRESS) as websocket:
        while True:
            message = websocket.recv()
            print(message)


if __name__ == "__main__":
    main()
