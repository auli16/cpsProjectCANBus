import can
import time

CAN_INTERFACE = "vcan0"
ID = 0x19b  

def periodic_ecu(bus):
  
    door_open = True  
    
    try:
        while True:
            door_status = [0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00] if door_open else [0x00, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00] 
            msg = can.Message(arbitration_id=ID, data=door_status, is_extended_id=False)
            
            bus.send(msg)
            status_text = "Open" if door_open else "Closed"
            print(f"Periodic ECU: door {status_text} (ID: {ID:#X}, data: {door_status})")
            
            door_open = not door_open
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("Periodic ECU interrupted.")
    except can.CanError as e:
        print(f"Error CAN: {e}")


if __name__ == "__main__":
    with can.interface.Bus(channel="vcan0", bustype="socketcan") as bus:
        periodic_ecu(bus)

