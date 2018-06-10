'''
    Automates the task of rebooting a Sonos music player
'''
import subprocess
import mechanicalsoup

def build_arp_cache():
    '''
        This function uses the arp-scan tool (which needs to be run as root) to scan the local
        network and identify the mac and ip addresses of neighbors. arp-scan was used in place of
        an nmap scan because it is much faster in building the table. It takes no arguments and
        returns nothing. Updates system wide arp table.
    '''

    cmd = "sudo arp-scan --interface=wlp5s0 --localnet"
    subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def get_target_device_ip(target_mac):

    build_arp_cmd = "sudo arp-scan --interface=wlp5s0 --localnet >/dev/null && "
    filter_cmd = "arp -an | grep " + target_mac + " | awk '{print $2}' | sed 's/[()]//g'"
    cmd = build_arp_cmd + filter_cmd
    print(cmd)
    output, error = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if not output:
        raise ValueError("Device not found on this network")
    return output.decode('utf-8').strip()

def reboot(ip_address):
    url = 'http://' + ip_address + ':1400/reboot'
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(url)
    browser.select_form('form[action="/reboot"]')
    browser.submit_selected()

def main():

    file_pointer = open('target_address.txt', 'r')
    target_mac = file_pointer.read().strip()
    file_pointer.close()

    target_ip = get_target_device_ip(target_mac)
    if not target_ip:

        print("[+] IP not found in arp cache, updating cache...")
        build_arp_cache()
        try:
            target_ip = get_target_device_ip(target_mac)
        except ValueError as error:
            print("ERROR HERE")
            #print(error)

    print("Rebooting...")
    reboot(target_ip)

if __name__ == '__main__':
    main()
