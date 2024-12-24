import subprocess
import time

scriptFakeECU = "./fakeECU.py"
scriptAttack = "./fabricationAttack.py"
output_file = "../dump/fabricationDump.txt"

def run_scripts():
    try:
        fakeECU = subprocess.Popen(["python3", scriptFakeECU])
        print("fake ECU started to send periodic messages")

        time.sleep(20)
        # the attack will start after 20 seconds
        fab_attack = subprocess.Popen(["python3", scriptAttack])
        print("Fabrication attack started")

        time.sleep(20)
        # 20 seconds to see the attack in action


        fakeECU.terminate()
        fab_attack.terminate()

        print("sending and attack terminated")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_scripts()


