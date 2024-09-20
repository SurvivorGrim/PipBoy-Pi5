<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/pipboy-pi5_logo.jpg" width="50%">

# Credits
The original source code from [ZapWizard](https://github.com/zapwizard/pypboy). Their project is insane, and you should check them out!

The Original [Adafruit project by the Ruiz Brothers](https://learn.adafruit.com/raspberry-pi-pipboy-3000/overview) that I adapted for 2024.

# Parts List
Coming Soon!

# Raspberry Pi Setup

## Initial Setup
- Use Raspberry Pi Imager to burn `MPI3501-3.5inch--2023-12-05-raspios-bookworm-armhf` to an SD card.
- Insert the SD card into the Pi.
- Plug in Ethernet.
- Attach the screen.
- Plug the Pi into the external charger to boot.

## Copy PipBoy Files
- Download PipBoy files to the desktop.
- Open PowerShell:

```bash
cd desktop
sftp pi@<pi_ip_address>

mkdir PipBoy
cd PipBoy
put -r PipBoy
exit
```

## Setup Pi
- SSH into the Pi:

```bash
ssh pi@<pi_ip_address>

sudo raspi-config
```

- Update and set the boot to desktop GUI:
> Update
> System Options > Boot / Auto Login > B4 Desktop AutoLogin Desktop GUI
<Finish>


- Edit `config.txt`:

```bash
sudo nano /boot/firmware/config.txt
```

Add the following lines:

```bash
dtoverlay=piscreen,speed=16000000,rotate=270
framebuffer_width=480
framebuffer_height=320
gpu_mem=2048
```

Reboot the Pi:

```bash
sudo reboot
```

- Install dependencies:

```bash
sudo apt install python3-cairosvg -y
sudo apt install python3-mutagen -y
sudo apt install python3-xmltodict -y
sudo apt install python3-pynput -y
sudo apt install python3-gpiozero -y
```

## Make a Shortcut
- Create autostart directory and add a desktop entry:

```bash
mkdir -p /home/pi/.config/autostart
nano /home/pi/.config/autostart/pipboy.desktop
```

Add the following content:

```bash
[Desktop Entry]
Name=PipBoy
Comment=Run PipBoy Python Script
Exec=sh -c 'cd /home/pi/PipBoy && python3 main.py'
Icon=python
Terminal=false
Type=Application
```

Make the desktop entry executable:

```bash
chmod +x /home/pi/.config/autostart/pipboy.desktop
```

## Turn Off Notifications
- Create the necessary directory and update autostart:

```bash
mkdir -p /home/pi/.config/lxsession/LXDE-pi
nano /home/pi/.config/lxsession/LXDE-pi/autostart
```

Add the following line:

```bash
@lxpanel --profile LXDE-pi --plugin=networkmanager --hide
```

## Turn Off Auto Updates
- Edit the `99-disable-updates` configuration:

```bash
sudo nano /etc/apt/apt.conf.d/99-disable-updates
```

Add the following lines:

```bash
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
```

## Set Volume
- Set the volume to 90%:

```bash
amixer -D pulse sset Master 90%
```

# Instructions for Building a Functional Pip-Boy with Raspberry Pi 5

1. **Speaker Assembly**
    - Carefully open the speaker case. This may require breaking the plastic, so proceed with caution to avoid damaging the internal circuit and speaker components.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/001.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/002.jpg" width="30%">

2. **Raspberry Pi Preparation**
    - Attach heat sinks to the Raspberry Pi to ensure proper thermal management.

3. **Modifying the Pip-Boy Housing**
    - Remove the pegs and mounts from the inside of the Pip-Boy, ensuring to leave the four mounts designated for the Raspberry Pi intact.
    - Using a carving tool, create a square cutout as illustrated in the accompanying diagram to accommodate the encoder knob. Ensure that the drilled hole fits the knob securely.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/003.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/004.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/005.jpg" width="30%">

4. **Wiring Connections**
    - Separate the wires from the main strand.
    - Trim the ends of the wires and strip them for soldering.
    - Solder the wires to the encoder switch as depicted in the reference image, then apply heat shrink tubing to prevent short circuits.
    - Repeat this process for the 10-point knob.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/006.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/007.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/008.jpg" width="30%">

5. **Audio USB Cable**
    - Cut the end off the USB cable connected to the audio circuit, noting the wire colors and soldering points.
    - For the angled USB cable, cut one end ensuring the correct angle faces right. Remove the shielding, strip the wires, and solder them according to the original color layout.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/009.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/011.jpg" width="30%">

6. **LED USB Cable**
    - Cut and strip another USB cable, removing the green and white wires while stripping the red and black.
    - Connect this USB cable to the LED, then apply heat shrink tubing as shown in the accompanying image.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/012.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/013.jpg" width="30%">

7. **Bracket Expansion**
    - Modify the bracket to accommodate the knob cables. A soldering iron can be used to carefully enlarge the holes.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/015.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/016.jpg" width="30%">

8. **Final Assembly Steps**
    - Mount the encoder knob. Trim the USB-C connector to fit through the designated hole. Plug the USB-C connector into the Raspberry Pi and secure it in place.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/014.jpg" width="30%">

8. **GPIO Pins**
    - Connect the female ends of both knobs to the GPIO pins as follows:

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/GPIO.jpg" width="60%">

10-Point Knob Connections:
```bash
- Pin 29 (Purple) - GPIO 5
- Pin 31 (Gray) - GPIO 6
- Pin 33 (Brown) - GPIO 13
- Pin 35 (Red) - GPIO 19
- Pin 37 (White) - GPIO 26
- Pin 39 (Black) - GND
```

Encoder Knob Connections:
```bash
- Pin 30 (Blue) - GND
- Pin 32 (Red) - GPIO 12
- Pin 34 (Orange) - GND
- Pin 36 (Yellow) - GPIO 16
- Pin 38 (Green) - GPIO 20
```


9. **Securing Audio Circuitry**
    - Use super glue to attach the audio circuit and speakers, potentially removing foam from the back of the speakers for better fit.
    - Mount the LCD screen, consider using spacers or cardboard glued to the top of the I/O to ensure it sits flush, accounting for spacing of the female GPIO cable connections.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/021.jpg" width="30%">

10. **Face Plate Modifications**
    - Drill additional holes in the faceplate for screws and the second encoder switch.
    - Bend the pins on the second encoder switch and glue it to the underside of the faceplate, followed by attaching the 3D-printed knob.
    - Affix the LED light cover and screen cover to the faceplate.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/017.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/018.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/019.jpg" width="30%"> 

11. **Face Plate Assembly**
    - Connect the USB cables and run the LED into the faceplate, then secure the faceplate using machine screws.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/020.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/022.jpg" width="30%">

12. **Magnets on Wrist Mount**
    - Attach magnets to the designated mounting points on the wrist mounts, ensuring that opposite ends attract.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/023.jpg" width="30%"> 
    
13. **Padding and Mount Assembly**
    - Cut two foam pieces to fit inside the wrist mount. Fold and hot glue vinyl to the foam for added comfort, then secure the padding inside the wrist mounts.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/024.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/025.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/026.jpg" width="30%">

13. **Hinge and Latch Assembly**
    - Drill and screw hinges onto the back and attach the latch on the front, adjusting it as necessary and securing with super glue.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/027.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/028.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/029.jpg" width="30%">

14. **Power Tube Assembly**
    - Glue the power tube mounts as indicated in the reference image and attach the cap onto the power tube.
    - Use a small piece of gray Velcro to the back of the PipBoy to enhance stability.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/030.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/031.jpg" width="30%">

14. **Power on!**
    - Finally, connect the USB to the power tube's connector. Note that this may be challenging; future builds may include an improved method. The external battery pack utilized here is recommended for managing the overall amp draw without glitches.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/032.jpg" width="50%">
