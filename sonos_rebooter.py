'''
    Automates the task of rebooting a Sonos music player
'''

import subprocess
import mechanicalsoup

def build_arp_cache():
    '''
        This function uses the arp-scan tool (which needs to be run as root) to scan the local
        network and identify the mac and ip addresses of neighbors. It takes no arguments and
        returns nothing. Updates system wide arp table.
    '''

    cmd = "nmap -p 80 10.1.10.0/24 > /dev/null"
    subprocess.Popen(['/bin/bash', '-c', cmd]).communicate()

def get_target_device_ip(target_mac):
    '''
        Reads system wide arp table and extracts the corresponding ip address from input target mac
        address. Returns the ip address as a string or throws a ValueError if not found
    '''

    cmd = "arp -an | grep " + target_mac + " | awk '{print $2}' | sed 's/[()]//g'"
    output, _ = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE).communicate()

    if not output:

        raise ValueError("[+] Device not found on this network")

    return output.decode('utf-8').strip()

def reboot(ip_address):
    '''
        Goes to web server hosted on target sonos device and performs a reboot via webdriver.
        Returns nothing.
    '''
    url = 'http://' + ip_address + ':1400/reboot'
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(url)
    browser.select_form('form[action="/reboot"]')
    browser.submit_selected()

def start_process(target_mac, cache_built=False):

    try:
        target_ip = get_target_device_ip(target_mac)
        print("[+] Device found. IP Address: " + target_ip)
        print("[+] Rebooting...")
        #reboot(target_ip)

    except ValueError as error:

        if not cache_built:
            print("[+] IP not found in arp cache, updating cache...")
            build_arp_cache()
            start_process(target_mac, cache_built=True)

        else:
            print(error)


def main():
    '''
        Checks system arp cache for instance of device. If not found, a function is called to build
        arp cache and a lookup is again tried.
    '''

    file_pointer = open('target_address.txt', 'r')
    target_mac = file_pointer.read().strip()
    file_pointer.close()

    start_process(target_mac, cache_built=False)

if __name__ == '__main__':
    main()
