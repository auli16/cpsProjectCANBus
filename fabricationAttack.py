import can 
import random 
import time 

bus = can.interface.Bus(channel="vcan0", bustype="socketcan")

def fab_message():
    # id = random.randint(0x000, 0x7FF)
    # data = [random.randint(0x00, 0xFF) for _ in range(8)]
    id = 0x188 # mettere gli id giusto per ogni tipo di comando
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