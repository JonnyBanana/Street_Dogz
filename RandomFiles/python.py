#!/usr/bin/python

from passlib.utils.pbkdf2 import pbkdf2
from base64 import b64decode
from datetime import datetime
from plistlib import readPlist
from time import time
import argparse
import os.path
import os

# Color Class


class color:
    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    LOGGING = '\33[34m'


def disableColor():
    color.HEADER = ''
    color.IMPORTANT = ''
    color.NOTICE = ''
    color.OKBLUE = ''
    color.OKGREEN = ''
    color.WARNING = ''
    color.FAIL = ''
    color.END = ''
    color.UNDERLINE = ''
    color.LOGGING = ''


if "nt" in os.name:
    disableColor()
    BACKUP_PATHS = os.path.join(
        os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Apple Computer', 'MobileSync', 'Backup\\')
else:
    BACKUP_PATHS = os.path.join(
        os.environ['HOME'], 'Library', 'Application Support', 'MobileSync', 'Backup/')

# iDevice Object

class idevice():
    def __init__(self, path):
        if os.path.isdir(path):
            self.path = path
        else:
            raise ValueError("%s is not a valid directory" % path)
        INFOPATH = path + "/Info.plist"
        if os.path.isfile(INFOPATH):
            self.info = readPlist(INFOPATH)
            self.name = self.info['Display Name']
            self.lastBackupDate = self.info['Last Backup Date']
            self.model = self.info['Product Type']
            self.UDID = self.info['Unique Identifier'].lower()
            self.iOS = self.info['Product Version']
            self.targetType = self.info['Target Type']
            self.findSecretKeySalt()
        else:
            raise ValueError("%s does not appear to contain a backup" % path)

    def findSecretKeySalt(self):
        restrictionsFile = "/398bc9c2aeeab4cb0c12ada0f52eea12cf14f40b"
        try:
            passfile = open(self.path + restrictionsFile, "r")
            line_list = passfile.readlines()
            self.secret64 = line_list[6][1:29]
            self.salt64 = line_list[10][1:9]
        except IOError:
            try:
                passfile = open(self.path + "/39" + restrictionsFile, "r")
                line_list = passfile.readlines()
                self.secret64 = line_list[6][1:29]
                self.salt64 = line_list[10][1:9]
            except IOError:
                raise ValueError(
                    "%s does not have a restrictions file or backup encrypted" % self.path)

    def crack(self):
        self.pin = crack(self.secret64, self.salt64)
        if args.webserver:
            from flask import session
            session[self.UDID] = self.pin
        return self.pin


def flask_setup():
    import webbrowser
    from flask import Flask, render_template, url_for, session, request, flash, redirect
    from wtforms import Form, StringField, TextAreaField, validators, ValidationError
    # Flask Classes, Definitions, and Routes
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.ico'))

    @app.route('/')
    def itunes():
        path = BACKUP_PATHS
        devices = findHashes(path)
        return render_template('itunes.html', devices=devices, numDevices=len(devices))

    @app.route('/crack')
    def iTunesCrack():
        devices = findHashes(BACKUP_PATHS)
        crackHashes(devices)
        return render_template('results.html', devices=devices, numDevices=len(devices))

    @app.route('/<string:UDID>')
    def deviceInfo(UDID):
        try:
            pin = session[UDID]
            device = idevice(BACKUP_PATHS + UDID.lower())
            return render_template('results.html', device=device)
        except:
            device = idevice(BACKUP_PATHS + UDID.lower())
            device.crack()
            return render_template('results.html', device=device)

    class crackForm(Form):
        restrictionsPasswordKey = StringField(
            'Restrictions Key', [validators.Length(min=26, max=32)], default="r3JS9BgcHea1hxFIeAAR7z0Il2w=")
        restrictionsPasswordSalt = StringField(
            'Restrictions Salt', [validators.Length(min=6, max=10)], default="osz+8g==")

    @app.route('/input', methods=['GET', 'POST'])
    def input():
        form = crackForm(request.form)

        if request.method == 'POST' and form.validate():
            restrictionsPasswordKey = str(form.restrictionsPasswordKey.data)
            restrictionsPasswordSalt = str(form.restrictionsPasswordSalt.data)
            pin = crack(restrictionsPasswordKey, restrictionsPasswordSalt)
            if pin:
                return render_template('results.html', pin=pin)
            else:
                flash("Invalid Key/Salt", 'danger')
                return redirect(url_for('index'))
        else:
            return render_template('form.html', form=form)

    webbrowser.open('http://127.0.0.1:8080/')
    app.run(port=8080, debug=True, use_reloader=False)

# Argparse Resources
def is_folder(parser, path):
    if not os.path.isdir(path):
        parser.error("The folder %s does not exist!" % path)
    else:
        if path.endswith('/'):
            return path
        else:
            return path + '/'

parser = argparse.ArgumentParser(prog="iOSCrack.py",
                                 description="a script which is used to crack the restriction passcode of an iPhone/iPad through a flaw in unencrypted backups allowing the hash and salt to be discovered")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-a", "--automatically", help="automatically finds and cracks hashes",
                    action="store_true")
parser.add_argument("-c", "--cli", help="prompts user for input",
                    action="store_true")
parser.add_argument("-w", "--webserver", help="creates webserver running flask",
                    action="store_true")
parser.add_argument("-b", "--backup", help="where backups are located", metavar="folder",
                    type=lambda x: is_folder(parser, x))

args = parser.parse_args()

# Logo
def logo():
    print("%s\n iOSRestrictionBruteForce" % color.HEADER)
    print(" Written by thehappydinoa %s\n" % color.END)

def check(secret64, salt64, key):
    secret = b64decode(secret64)
    salt = b64decode(salt64)
    out = pbkdf2(key, salt, 1000)
    return (out == secret)


def crack(secret64, salt64):
    COMMON_KEYS = [000000, 111111, 222222, 333333, 444444, 555555, 666666, 777777, 8888888, 9999999, 
                   123456, 123123, 121212, 123321, 654321, 696969, 112233, 159753, 292513, 131313,
                   123654, 789456, 101010, 100100, ]
    start_t = time()
    # Top 20 common pins
    for i in COMMON_KEYS:
        print("%sTrying: %s \r" % (color.NOTICE, i)),
        key = "%06d" % (i)
        if check(secret64, salt64, key):
            duration = round(time() - start_t, 2)
            print("Passcode is %s (top 20 most common passcode) %s\n" %
                  (key, color.END))
            return key

    # Common birth dates
    for x in range (0,31):
        if(x < 10):
            x_string = "0" + str(x)
        else:
            x_string = str(x)

        for i in range(1900, 2019):
            key_string = x_string + str(i)
            print("%sTrying: %s \r" % (color.NOTICE, i)),
            key = "%06d" % (int(key_string))
            if check(secret64, salt64, key):
                duration = round(time() - start_t, 2)
                print("Passcode is %s (common year) it took %s secconds %s\n" %
                      (key, duration, color.END))
                return key

            key_string = str(i) + x_string
            key = "%06d" % (int(key_string))
            if check(secret64, salt64, key):
                duration = round(time() - start_t, 2)
                print("Passcode is %s (common year) it took %s secconds %s\n" %
                      (key, duration, color.END))
                return key
            
    # Brute force all pins
    for i in range(1000000):
        key = "%04d" % (i)
        print("%sTrying: %s \r" % (color.NOTICE, key)),
        if check(secret64, salt64, key):
            duration = round(time() - start_t, 2)
            print("Passcode is %s it took %s secconds %s\n" %
                  (key, duration, color.END))
            return key
    print("%sInvalid Key and/or Salt %s" %
          (color.FAIL, color.END))


def prompt():
    secret64 = raw_input("\nEnter Secret Key: ")
    if secret64 < 3 or secret64 == "":
        print("%sInvalid Key %s" %
              (color.FAIL, color.END))
        exit()
    salt64 = raw_input("Enter Salt: ")
    if salt64 < 10 or salt64 == "":
        print("%sInvalid Salt %s" %
              (color.FAIL, color.END))
        exit()
    crack(secret64, salt64)


def crackHashes(devices):
    for device in devices:
        if args.verbose:
            print("%sUDID: %s \n%s: %s running iOS %s %s" %
                  (color.OKGREEN, device.UDID, device.targetType, device.model, device.iOS, color.END))
        print("%sCracking restrictions passcode for %s... %s" %
              (color.OKBLUE, device.name, color.END))
        try:
            pin = session[device.UDID]
        except:
            device.crack()


def findHashes(path):
    devices = []
    print("\n%sLooking for backups in %s..." % (color.OKBLUE, path)),
    if not path.endswith('/'):
        path = path + '/'
    try:
        backup_dir = os.listdir(path)

    print("prova %s" % backup_dir)
        
        if len(backup_dir) > 0:
            print("%sDirectory Found %s" % (color.OKGREEN, color.END))
            for bkup_dir in backup_dir:
                try:
                    device = idevice(path + bkup_dir)
                    
                    device.crack()
                    devices.append(device)
                    crackHashes(devices)
                except ValueError as e:
                    print(str(e))
            return devices
        else:
            print(
                "Unable to find backups in %s" % bkup_dir)
    except OSError as e:
        print("%sDirectory Not Found%s" % (color.FAIL, color.END))


def main():
    try:
        logo()
        if args.automatically and not args.cli:
            crackHashes(findHashes(BACKUP_PATHS))
        if args.cli:
            prompt()
        if args.backup:
            findHashes(args.backup)
        if args.webserver:
            flask_setup()
        if not args.verbose and not args.automatically and not args.cli and not args.backup:
            crackHashes(findHashes(BACKUP_PATHS))
    except KeyboardInterrupt:
        print("Exiting...\r"),
        pass


if __name__ == "__main__":
    main()
