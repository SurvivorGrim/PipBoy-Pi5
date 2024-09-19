
Raspberry Pi Setup

OS: MPI3501-3.5inch-2020-05-27-raspios-buster.img

Install All Needed Packages
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-cairosvg
sudo apt install python3-mutagen
sudo apt install python3-xmltodict
sudo apt install python3-pynput
sudo apt install python3-gpiozero
```

Make Shortcut
```bash
mkdir -p /home/pi/.config/autostart
nano /home/pi/.config/autostart/pipboy.desktop
```

Add the following content to pipboy.desktop:
```
[Desktop Entry]
Name=PipBoy
Comment=Run PipBoy Python Script
Exec=sh -c 'cd /home/pi/PipBoy && python3 main.py'
Icon=python
Terminal=false
Type=Application
```

Then make it executable:
```bash
chmod +x /home/pi/.config/autostart/pipboy.desktop
```

Turn Off Notification
```bash
mkdir -p /home/pi/.config/lxsession/LXDE-pi
nano /home/pi/.config/lxsession/LXDE-pi/autostart
```

Add the following line to autostart:
```
@lxpanel --profile LXDE-pi --plugin=networkmanager --hide
```

Edit 99-disable-updates file:
```bash
sudo nano /etc/apt/apt.conf.d/99-disable-updates
```

Add the following content:
```
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
```

Instructions for Building a Functional Pip-Boy with Raspberry Pi 5

1. Speaker Assembly
Carefully open the speaker case. This may require breaking the plastic, so proceed with caution to avoid damaging the internal circuit and speaker components.

2. Raspberry Pi Preparation
Attach heat sinks to the Raspberry Pi to ensure proper thermal management.

3. Modifying the Pip-Boy Housing
- Remove the pegs and mounts from the inside of the Pip-Boy, ensuring to leave the four mounts designated for the Raspberry Pi intact.
- Using a carving tool, create a square cutout as illustrated in the accompanying diagram to accommodate the encoder knob. Ensure that the drilled hole fits the knob securely.

4. Wiring Connections
- Separate the wires from the main strand.
- Trim the ends of the wires and strip them for soldering.
- Solder the wires to the encoder switch as depicted in the reference image, then apply heat shrink tubing to prevent short circuits.
- Repeat this process for the 10-point knob.

5. Assembly of Components
- Position the components within the enclosure and secure them with screws. Attach the 3D-printed knob.
- Cut the end off the USB cable connected to the audio circuit, noting the wire colors and soldering points.
- For the angled USB cable, cut one end ensuring the correct angle faces right. Remove the shielding, strip the wires, and solder them according to the original color layout.

6. Bracket Expansion
Modify the bracket to accommodate the knob cables. A soldering iron can be used to carefully enlarge the holes.

7. Additional USB Connections
- Cut and strip another USB cable, removing the green and white wires while stripping the red and black.
- Connect this USB cable to the LED, then apply heat shrink tubing as shown in the accompanying image.

8. Final Assembly Steps
- Mount the encoder knob. Trim the USB-C connector to fit through the designated hole. Plug the USB-C connector into the Raspberry Pi and secure it in place.
- Connect the female ends of both knobs to the GPIO pins as follows:

10-Point Knob Connections:
- Pin 29 (Purple) - GPIO 5
- Pin 31 (Gray) - GPIO 6
- Pin 33 (Brown) - GPIO 13
- Pin 35 (Red) - GPIO 19
- Pin 37 (White) - GPIO 26
- Pin 39 (Black) - GND

Encoder Knob Connections:
- Pin 30 (Blue) - GND
- Pin 32 (Red) - GPIO 12
- Pin 34 (Orange) - GND
- Pin 36 (Yellow) - GPIO 16
- Pin 38 (Green) - GPIO 20

9. Securing Audio Circuitry
- Use super glue to attach the audio circuit and speakers, potentially removing foam from the back of the speakers for better fit.
- Mount the LCD screen, consider using spacers or cardboard glued to the top of the I/O to ensure it sits flush, accounting for spacing of the female GPIO cable connections.

10. Face Plate Modifications
- Drill additional holes in the faceplate for screws and the second encoder switch.
- Bend the pins on the second encoder switch and glue it to the underside of the faceplate, followed by attaching the 3D-printed knob.
- Affix the LED light cover and screen cover to the faceplate.

11. Final Assembly
- Connect the USB cables and run the LED into the faceplate, then secure the faceplate using machine screws.
- Attach magnets to the designated mounting points on the wrist mounts, ensuring that opposite ends attract.

12. Padding and Mount Assembly
- Cut two foam pieces to fit inside the wrist mount. Fold and hot glue vinyl to the foam for added comfort, then secure the padding inside the wrist mounts.
- Drill and screw hinges onto the back and attach the latch on the front, adjusting it as necessary and securing with super glue.

13. Power Tube Assembly
- Glue the power tube mounts as indicated in the reference image and attach the cap onto the power tube.
- Use a small piece of gray Velcro to the back of the PipBoy to enhance stability.
- Finally, connect the USB to the power tube's connector. Note that this may be challenging; future builds may include an improved method. The external battery pack utilized here is recommended for managing the overall amp draw without glitches.
