import can 

bus = can.interface.Bus(channel="vcan0", bustype="socketcan")

def fab_message():
    id = 0x188 #left arrow id
    data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    return can.Message(arbitration_id = id, data = data, is_extended_id = False)

try:
    while True:
        msg = fab_message()
        bus.send(msg)
        print(f"Fab msg: {msg}")
        # time.sleep(0.001)
except KeyboardInterrupt:
    print("Stacca Stacca")
except can.CanError as e:
    print(f"CAN error: {e}")