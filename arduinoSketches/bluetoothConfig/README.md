# Raspberry Pi 3B+ and HC-05 Set Up and Pairing

## Intro
The initial setup took a couple of hours of fiddling around with different methods and packages. The final working version was heavily based on u/Illmatic-Herbicide's (post on reddit)[[https://www.reddit.com/r/raspberry_pi/comments/6nchaj/guide_how_to_establish_bluetooth_serial/], however a few steps and other minor additions were made which are documented below.

## Notes
* This is specifically a headless approach and it is assumed the user has SSH'd into their Pi.
* `ratom` can be replaced by `nano` or any other text editor being used.
* When running `[bluetooth]#` enter `help` at any point for a full list of commands and explanations.
* This guide will be updated if further information is found or guidance is requested.

## Instructions
Upgrade all packages and get the required packages.
```
sudo apt-get dist-upgrade
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install bluez pi-bluetooth python-bluez
```

Enter the following command for configuring Bluetooth devices (specifically on Linux).
```
bluetoothctl
```

The next 2 commands will accomplish:
1. Turn on RPi bluetooth if its not already
2. Scan for devices
```
[bluetooth]#  scan on
    ...
    98:D3:71:FD:61:63	MECE653
    ...
```
After waiting for a few seconds the device should be found. For example mine looked similar to this:
```
…
[CHG] Device 98:D3:71:FD:61:63 Name: MECE653
help
…
```
The unique address `98:D3:71:FD:61:63` is equal to <dev> below. Set <dev> to your devices address in the remaining steps if different. Again, it will be in the form of XX:XX:XX:XX:XX:XX.

Once your specific device has been found enter the remaining commands which do the following:
1. Stop scanning for devices
2. Enable agent with given capability
3. Pair with device. **You may need to enter a pin at this step!**
4. Trust the device
5. Connect to the device
6. Look at the device and ensure it is paired, trusted, and connected.
```
[bluetooth]# scan off
[bluetooth]# agent on
[bluetooth]# pair <dev>
[bluetooth]# trust <dev>
[bluetooth]# connect <dev>
[bluetooth]# info <dev>

```

Edit the file using `sudo ratom /etc/systemd/system/dbus-org.bluez.service` and add "-C" to the **ExecStart** line and **ExecStartPost=/usr/bin/sdptool add SP** below it. The file will look something like this:

```
...
ExecStart=/usr/lib/bluetooth/bluetoothd -C
ExecStartPost=/usr/bin/sdptool add SP
...
```

Then edit the following file using `sudo ratom /etc/bluetooth/rfcomm.conf` to match the following information:
```
rfcomm1 {
    # Automatically bind the device at startup
    bind yes;

    # Bluetooth address of the device
    device <dev>;

    # RFCOMM channel for the connection
    channel 1;

    # Description of the connection
    comment "My Bluetooth Connection";
}
```

Reboot RPi using `sudo reboot` and SSH back in. Try running:

```
sudo rfcomm bind /dev/rfcomm0 <dev> 1
```

If you do not get any errors and everything checks out go ahead to `main.py` and give it a try. The Bluetooth serial port will be on `/dev/rfcomm0`.

If I missed any steps or something is not working please leave a comment or issue so that the guide can be fixed. 
