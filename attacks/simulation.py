import subprocess
import time
import os
import signal

scriptPeriodicECU = "./periodicECU.py"
scriptAttack = "./suspensionAttack.py"
output_file = "../dump/dump_susp20sec.log"

def run_scripts():
    try:
        periodicECU = subprocess.Popen(["python3", scriptPeriodicECU])
        print("periodic ECU started to send periodic messages")

        cmd_command = f"candump -f {output_file} vcan0"
        candump_process = subprocess.Popen(cmd_command, shell=True)
        print("Dump started")

        time.sleep(20)
        # the attack will start after 20 seconds
        attack = subprocess.Popen(["python3", scriptAttack])
        print("Attack started")

        time.sleep(40)


        periodicECU.terminate()
        attack.terminate()

        os.kill(candump_process.pid, signal.SIGINT)
        print("Candump stopped")
        candump_process.wait()

        print("sending and attack terminated")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_scripts()


