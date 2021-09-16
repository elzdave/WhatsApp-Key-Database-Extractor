# Auto Requirements installer.
import datetime
import json
import os
import socket

try:
    import packaging
    import psutil
    import termcolor
    import requests
    from tqdm import tqdm
except ImportError:
    print('\nFirst run: Auto installing python requirements.\n')
    try:
        # Trying both methods of installations
        os.system('pip3 install --upgrade packaging psutil termcolor requests tqdm')
    except:
        os.system(
            'python3 -m pip install --upgrade packaging psutil termcolor requests tqdm')


import argparse
import concurrent.futures
import platform
import re
import subprocess
import time

import helpers.adb_device_serial_id as deviceId
import helpers.tcp_device_serial_id as tcpDeviceId
from helpers.custom_ci import custom_input, custom_print
from helpers.linux_handler import linux_handler
from helpers.windows_handler import windows_handler
from view_extract import extract_ab

# Detect OS
isWindows = False
isLinux = False
if platform.system() == 'Windows':
    isWindows = True
if platform.system() == 'Linux':
    isLinux = True

# Global Variables
appURLWhatsAppCDN = 'https://www.cdn.whatsapp.net/android/2.11.431/WhatsApp.apk'
appURLWhatsCryptCDN = 'https://whatcrypt.com/WhatsApp-2.11.431.apk'


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    CheckBin()
    ShowBanner()
    global is_java_installed
    is_java_installed = check_java()
    custom_print('\n', is_get_time=False)
    try:
        custom_print('Arguments passed: ' + str(args), is_print=False)
    except:
        pass

    try:
        custom_print('System Info: ' +
                     json.dumps(GetSysInfo(), indent=2, default=str), is_print=False)
    except:
        custom_print(
            'Can\'t get system information. Continuing anyway...', 'yellow')
    custom_print('Current release date: 13/09/2021', 'cyan')
    custom_print('\n', is_get_time=False)
    readInstruction = custom_input(
        '\aPlease read above instructions carefully \u2191 . Continue? (default y): ', 'yellow') or 'Y'
    if(readInstruction.upper() == 'Y'):
        custom_print('\n', is_get_time=False)
        custom_input(
            '\aIf you haven\'t already, it is adviced to take a WhatsApp chat backup by going to \"WhatsApp settings \u2192 Chat Settings \u2192 Chat Backup". Hit \"Enter\" key to continue.', 'yellow')
        USBMode()
    else:
        Exit()


def BackupWhatsAppApk(SDKVersion, versionName, WhatsAppapkPath):
    os.system(adb + ' shell am force-stop com.whatsapp') if(SDKVersion >
                                                            11) else os.system(adb + ' shell am kill com.whatsapp')
    custom_print('Backing up WhatsApp ' + versionName +
                 ' apk, the one installed on device to \"/data/local/tmp/WhatsAppbackup.apk\" in your phone.')
    os.system(adb + ' shell cp ' + WhatsAppapkPath +
              ' /data/local/tmp/WhatsAppbackup.apk')
    custom_print('Apk backup is completed.')


def BackupWhatsAppDataasAb(SDKVersion):
    os.mkdir(tmp) if not (os.path.isdir(tmp)) else custom_print(
        'Folder ' + tmp + ' already exists.', 'yellow')
    custom_print('Backing up WhatsApp data as \"' + tmp +
                 'whatsapp.ab\". May take time, don\'t panic.')
    try:
        os.system(adb + ' backup -f ' + tmp + 'whatsapp.ab com.whatsapp') if(SDKVersion >=
                                                                             23) else os.system(adb + ' backup -f ' + tmp + 'whatsapp.ab -noapk com.whatsapp')
    except Exception as e:
        custom_print(e, 'red')
        Exit()
    custom_print('Done backing up data. Size: ' +
                 str(os.path.getsize(tmp + 'whatsapp.ab')) + ' bytes.')


def CheckBin():
    if (not os.path.isdir('bin')):
        custom_print('I can not find \"bin\" folder, check again...', 'red')
        Exit()
    else:
        pass


def check_java():
    java_version = ''
    out = subprocess.getoutput('java -version')
    if(out):
        java_version = re.findall('(?<=version ")(.*)(?=")', out)
    else:
        custom_print(
            'Could not get output of \"java -version\" in \"wa_kdbe.py\"', 'red')
        custom_print('Continuing without JAVA...', 'red')
        return False
    if(java_version):
        is_java_installed = True
    else:
        is_java_installed = False
    if is_java_installed:
        custom_print('Found Java v' + java_version[0] +
                     ' installed on system. Continuing...')
        return is_java_installed
    else:
        noJAVAContinue = custom_input(
            'It looks like you don\'t have JAVA installed on your system. Would you like to (C)ontinue with the process and \"view extract\" later? or (S)top?: ', 'red') or 'C'
        if(noJAVAContinue.upper() == 'C'):
            custom_print(
                'Continuing without JAVA, once JAVA is installed on system run \"view_extract.py\"', 'yellow')
            return is_java_installed
        else:
            Exit()


def Exit():
    custom_print('\n', is_get_time=False)
    custom_print('Exiting...')
    os.system(
        'bin\\adb.exe kill-server') if(isWindows) else os.system('adb kill-server')
    custom_input('Hit \"Enter\" key to continue....', 'cyan')
    quit()


def GetSysInfo():
    info = {}
    info['Platform'] = platform.system()
    info['Platform Release'] = platform.release()
    info['Platform Version'] = platform.version()
    info['Architecture'] = platform.machine()
    info['Hostname'] = socket.gethostname()
    info['Processor'] = platform.processor()
    info['RAM'] = str(
        round(psutil.virtual_memory().total / (1024.0 ** 3)))+" GB"
    return info


def InstallLegacy(SDKVersion):
    custom_print('Installing legacy WhatsApp V2.11.431, hold tight now.')
    if(SDKVersion >= 17):
        os.system(adb + ' install -r -d ' + helpers + 'LegacyWhatsApp.apk')
    else:
        os.system(adb + ' install -r ' + helpers + 'LegacyWhatsApp.apk')
    custom_print('Installation Complete.')


def RealDeal(SDKVersion, WhatsAppapkPath, versionName, sdPath):
    BackupWhatsAppApk(SDKVersion, versionName, WhatsAppapkPath)
    UninstallWhatsApp(SDKVersion)
    # Reboot here.
    if(isAllowReboot):
        if(not tcpIP):
            custom_print('\n', is_get_time=False)
            custom_print('Rebooting device, please wait.', 'yellow')
            os.system(adb + ' reboot')
            while(subprocess.getoutput(adb + ' get-state') != 'device'):
                custom_print('Waiting for device...')
                time.sleep(5)
            custom_input('Hit \"Enter\" key after unlocking device.', 'yellow')
        else:
            custom_print(
                'Rebooting device in TCP mode break the connection and won\'t work until explicitly turned on in device and/or in PC. Skipping...', 'yellow')

    InstallLegacy(SDKVersion)
    # Before backup run app
    os.system(adb + ' shell am start -n com.whatsapp/.Main')
    custom_input(
        '\aHit \"Enter\" key after running Legacy WhatsApp for a while. Ignore invalid date warning.', 'yellow')
    BackupWhatsAppDataasAb(SDKVersion)
    ReinstallWhatsApp()
    custom_print('\n', is_get_time=False)
    custom_print(
        '\aOur work with device has finished, it is safe to remove it now.', 'yellow')
    custom_print('\n', is_get_time=False)
    extract_ab(is_java_installed, sdcard_path=sdPath,
               adb_device_serial_id=ADBSerialId, is_tar_only=isTarOnly)


def ReinstallWhatsApp():
    custom_print('Reinstallting original WhatsApp.')
    try:
        os.system(
            adb + ' shell pm install /data/local/tmp/WhatsAppbackup.apk')
    except Exception as e:
        custom_print(e, 'red')
        custom_print('Could not install WhatsApp, install by running \"restore_whatsapp.py\" or manually installing from Play Store.\nHowever if it crashes then you have to clear storage/clear data from \"Settings \u2192 App Settings \u2192 WhatsApp\".')
        Exit()


def RunScrCpy(_isScrCpy):
    if(_isScrCpy):
        cmd = 'bin\scrcpy.exe --max-fps 15 -b 4M --always-on-top' if(
            isWindows) else 'scrcpy --max-fps 15 -b 4M --always-on-top'
        proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False)
        proc.communicate()


def ShowBanner():
    banner_content = '''
================================================================================
========                                                                ========
========  db   d8b   db  .d8b.         db   dD d8888b. d8888b. d88888b  ======== 
========  88   I8I   88 d8' `8b        88 ,8P' 88  `8D 88  `8D 88'      ======== 
========  88   I8I   88 88ooo88        88,8P   88   88 88oooY' 88ooooo  ======== 
========  Y8   I8I   88 88~~~88 C8888D 88`8b   88   88 88~~~b. 88~~~~~  ======== 
========  `8b d8'8b d8' 88   88        88 `88. 88  .8D 88   8D 88.      ======== 
========   `8b8' `8d8'  YP   YP        YP   YD Y8888D' Y8888P' Y88888P  ======== 
========                                                                ========
================================================================================'''

    intro_a = '''
============ WhatsApp Key / Database Extrator for non-rooted Android ===========\n
================================================================================
===                                                                          ==='''

    intro_b = '''===  xxxxx  PLEASE TAKE WHATSAPP CHAT BACKUP BEFORE GETTING STARTED.  xxxxx  ==='''

    intro_c = '''===                                                                          ===
===     For that go to \"WhatsApp settings \u2192 Chat Settings \u2192 Chat Backup\"     ===
===              here take a local backup. Prepare for Worst.                ===
===                                                                          ==='''

    intro_d = '''===  Also if you see a folder \"Android/media/com.whatsapp\" copy it somewhere ===
===   safe. New versions of WhatsApp are saving data here INCLUDING IMAGES   ===
===       AND VIDEOS. I try to save it while uninstalling WhatsApp but       ===
===                        YOU CAN NEVER BE TOO SAFE.                        ==='''

    intro_e = '''===                                                                          ===
===     This script can extract your WhatsApp msgstore.db (non crypt12,      ===
===   unencrypted file) and your \"key\" file from \"/data/data/com.whatsapp\"   ===
===  directory in Android 4.0+ device without root access. However you need  ===
===   to have JAVA installed on your system in order to \"view the extract\".  ===
===  If you don't have JAVA installed then you can \"view extract\" later by   ===
===   running \"view_extract.py\". The idea is to install a \"Legacy WhatsApp\"  ===
===       temporarily on your device in order to get the android backup      ===
===    permission. You should not lose any data and your current WhatsApp    ===
===   version will be installed after this process so don't panic and don't  ===
=== stop this script while it's working. However if something fails you can  ===
===    run \"restore_whatsapp.py\" and reinstall current WhatsApp or simply    ===
===                    update that from Google Play Store.                   ===
===                                                                          ===
===                      Script by: Yuvraj Raghuvanshi                       ===
===                      Github.com/YuvrajRaghuvanshiS                       ===
================================================================================
    '''
    custom_print(banner_content, 'green', ['bold'], False)
    custom_print(intro_a, 'green', ['bold'], False)
    custom_print(intro_b, 'red', ['bold'], False)
    custom_print(intro_c, 'green', ['bold'], False)
    custom_print(intro_d, 'red', ['bold'], False)
    custom_print(intro_e, 'green', ['bold'], False)


def UninstallWhatsApp(SDKVersion):
    if(SDKVersion >= 23):
        try:
            custom_print('Uninstalling WhatsApp, skipping data.')
            os.system(adb + ' shell pm uninstall -k com.whatsapp')
            custom_print('Uninstalled.')
        except Exception as e:
            custom_print('Could not uninstall WhatsApp.')
            custom_print(e, 'red')
            Exit()


def USBMode():
    if(isWindows):
        ACReturnCode, SDKVersion, WhatsAppapkPath, versionName, sdPath = windows_handler(
            adb)
        RealDeal(SDKVersion, WhatsAppapkPath, versionName,
                 sdPath) if ACReturnCode == 1 else Exit()
    else:
        ACReturnCode, SDKVersion, WhatsAppapkPath, versionName, sdPath = linux_handler(
            ADBSerialId)
        RealDeal(SDKVersion, WhatsAppapkPath, versionName,
                 sdPath) if ACReturnCode == 1 else Exit()


if __name__ == "__main__":

    custom_print('\n\n\n====== Logging start here. ====== \nFile: ' + os.path.basename(__file__) + '\nDate: ' +
                 str(datetime.datetime.now()) + '\nIf you see any password here then do let know @github.com/YuvrajRaghuvanshiS/WhatsApp-Key-Database-Extractor\n\n\n', is_get_time=False, is_print=False)

    parser = argparse.ArgumentParser()
    parser.add_argument('-ar', '--allow-reboot', action='store_true',
                        help='Allow reboot of device before installation of LegacyWhatsApp.apk to prevent some issues like [INSTALL_FAILED_VERSION_DOWNGRADE]')
    parser.add_argument('-tip', '--tcp-ip',
                        help='Connects to a remote device via TCP mode.')
    parser.add_argument('-tp', '--tcp-port',
                        help='Port number to connect to. Default: 5555')
    parser.add_argument('-s', '--scrcpy', action='store_true',
                        help='Run ScrCpy to see and control Android device.')
    parser.add_argument('-to', '--tar-only', action='store_true',
                        help='Get entire WhatsApp\'s data in \"<username>.tar\" file instead of just getting few important files.')
    args = parser.parse_args()
    #args = parser.parse_args('--tcp-ip 192.168.43.130 --scrcpy'.split())

    isAllowReboot = args.allow_reboot
    tcpIP = args.tcp_ip
    tcpPort = args.tcp_port
    isScrCpy = args.scrcpy
    isTarOnly = args.tar_only
    # TODO: Download legacy on phone(later). Backup original on phone(done). Create backup on phone. Install original from phone.
    if(tcpIP):
        if(not tcpPort):
            tcpPort = '5555'
        ADBSerialId = tcpDeviceId.init(tcpIP, tcpPort)
    else:
        ADBSerialId = deviceId.init()
    if(not ADBSerialId):
        Exit()

    # Global command line helpers
    tmp = 'tmp/'
    helpers = 'helpers/'
    if(isWindows):
        adb = 'bin\\adb.exe -s ' + ADBSerialId
    else:
        adb = 'adb -s ' + ADBSerialId

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(main)
        time.sleep(1)
        f2 = executor.submit(RunScrCpy, isScrCpy)
