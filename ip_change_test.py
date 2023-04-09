import subprocess
import undetected_chromedriver as uc
import time
import requests
import os

def main():

    class The_time:

            def __init__(self) -> None:
                self.the_time = time.strftime("%H:%M:%S", time.localtime())

            def __repr__(self) -> str:
                return self.the_time

    def internet_ip_check():
            url = "https://api.ipify.org"
            timeout = 5
            while True:
                try:
                    ip = requests.get(url, timeout=timeout)
                    return ip.text
                except (requests.ConnectionError, requests.Timeout):
                    pass

    def turn_on_airplane_mode():
        print(f'[{The_time()}] - Turning on Airplane Mode...')
        cmd_one = "adb shell settings put global airplane_mode_on 1"
        subprocess.call(cmd_one, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(0.5)
        cmd_one = "adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
        subprocess.call(cmd_one, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def turn_off_aiplane_mode():

        print(f'[{The_time()}] - Turning off Airplane Mode...')

        cmd_two = "adb shell settings put global airplane_mode_on 0"
        subprocess.call(cmd_two, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(0.5)
        cmd_two = "adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
        subprocess.call(cmd_two, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def connect_to_wifi():
        
        name_of_router = "UlaKoszula"
    
        os.system(f'''cmd /c "netsh wlan connect name={name_of_router}"''')

    def disconnect_to_wifi():
    
        os.system(f'''cmd /c "netsh wlan disconnect"''')

    

    ip_before = internet_ip_check()

    print(ip_before)

    connect_to_wifi()

    connect_to_wifi()

    turn_on_airplane_mode()

    while True:
        try:
            driver = uc.Chrome()
            break
        except Exception as e:
            print(e)
            pass

    turn_off_aiplane_mode()

    disconnect_to_wifi()

    disconnect_to_wifi()

    ip_after = internet_ip_check()

    print(ip_after)

    if ip_before != ip_after:
        print(f'[{The_time()}] - Successfully prepared new IP Adress!')

if __name__ == '__main__':
    main()