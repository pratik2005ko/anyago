import subprocess

def launch_rofi():
    # check karo ki rofi already chal raha hai
    result = subprocess.run(["pgrep", "-f", "rofi"], capture_output=True)
    
    if result.returncode == 0:
        # rofi chal raha hai — kill karo
        subprocess.run(["pkill", "-f", "rofi"])
    else:
        # rofi nahi chal raha — launch karo
        subprocess.run(["rofi", "-show", "drun"])

launch_rofi()