import can 
import time 

bus = can.interface.Bus(channel="vcan0", bustype="socketcan")

def sus_message():

    
    id = 0x100 # mettere gli id giusti per ogni tipo di comando
    data = [0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]

    return can.Message(arbitration_id = id, data = data, is_extended_id = False)

try:
    while True:
        msg = sus_message()
        bus.send(msg)
        print(f"sus msg: {msg}")
        time.sleep(0.001)
except KeyboardInterrupt:
    print("Stacca Stacca")
except can.CanError as e:
    print(f"CAN error: {e}")