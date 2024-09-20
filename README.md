<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/pipboy-pi5_logo.png" width="50%">

# Credits
The original source code from [ZapWizard](https://github.com/zapwizard/pypboy). Their project is insane, and you should check them out!

The original [Adafruit project by the Ruiz Brothers](https://learn.adafruit.com/raspberry-pi-pipboy-3000/overview) that I adapted for 2024.

The 3d Printer who got me the extra knob [3DPrintsByKai](https://www.instagram.com/3dprintsbykai), check out all their cool 3D prints! 

# Parts List

- [Raspberry Pi-5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Pi-5 Heatsinks](https://category.yahboom.net/products/pi5-heatsink)
- [3.5 Inch 480x320 TFT Resistive Touchscreen](https://www.sunfounder.com/products/3-5-inch-touchscreen)
- [Pip-Boy Housing](https://www.etsy.com/listing/1716535063/functional-3000-mkiv-for-use-with-a)
- [Extra 3D Knob](https://www.etsy.com/shop/3dprintsbykai)
- [Anker PowerCore 5,000mAh Portable Charger](https://www.amazon.com/Anker-PowerCore-Ultra-Compact-High-Speed-Technology/dp/B01CU1EC6Y)
- [USB Mini Speaker Computer Speaker](https://www.walmart.com/ip/HONKYOB-USB-Mini-Speaker-Computer-Speaker-Powered-Stereo-Multimedia-Speaker-for-Notebook-Laptop-PC-Black/182421233)
- [Rotary Encoder Knob](https://www.adafruit.com/product/377)
- [Rotary Switch - 10 Position](https://www.sparkfun.com/products/13253)
- [Neodymium Disc Magnets](https://www.kjmagnetics.com/proddetail.asp?prod=D42-N52)
- [Female to Female Header Jumper Wire](https://www.amazon.com/Solderless-Multicolored-Electronic-Breadboard-Protoboard/dp/B09FP2QC95/ref=sr_1_2)
- [Super Bright LED](https://www.adafruit.com/product/2700)
- [USB 2.0 Cable Male To Male Angle](https://www.ebay.com/itm/225873817359?chn=ps&mkevt=1&mkcid=28&var=524965204247&srsltid=AfmBOopzlNYnD836KYvnsTjsLpLBUJnghjdXJmBqm5temdgq9WCXy-A1ZVQ)
- [165.1-mm Silver Cabinet Latchh](https://www.lowes.com/pd/Gatehouse-2-Pack-Zinc-Plated-Silver-Touch-Catch/1000390351)
- [3/4-in H Silver Mortise Interior Door Hinge](https://www.lowes.com/pd/Gatehouse-3-4-in-Satin-Nickel-Mortise-Door-Hinge-4-Pack/50056451)
- [Brown Faux Leather Fabric](https://www.joann.com/brown-faux-leather-fabric/19451053.html)
- [Foam Padding](Link Coming Soon)


# Raspberry Pi Setup

## Initial Setup
- Use Raspberry Pi Imager to burn [MPI3501-3.5inch--2023-12-05-raspios-bookworm-armhf](https://mega.nz/folder/ixQiTa7R#EM2uFGwMC8QSU6D4untoGA) to an SD card.
- Insert the SD card into the Pi.
- Plug in Ethernet.
- Attach the screen.
- Plug the Pi into the external charger to boot.


## Download the PipBoy Folder from the GitHub Repository Using PowerShell

1. **Open PowerShell** on your machine.

2. **Navigate to the directory** where you want to download the folder. Replace the path in the command with your desired location:
```powershell
cd C:\Path\To\Your\Desired\Directory
```

3. **Download the `PipBoy` folder** as a `.zip` file from GitHub:
```powershell
Invoke-WebRequest -Uri https://github.com/SurvivorGrim/PipBoy-Pi5/archive/refs/heads/main.zip -OutFile PipBoy-Pi5.zip
```

4. **Extract the downloaded ZIP file**:
```powershell
Expand-Archive -Path .\PipBoy-Pi5.zip -DestinationPath .\PipBoy-Pi5
```

5. **Navigate into the `PipBoy` folder** within the extracted content:
 ```powershell
cd .\PipBoy-Pi5-main\PipBoy\
 ```
   
## Copy PipBoy Files to Pi

```powershell
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

Update and set the boot to desktop GUI:
- Update
- System Options > Boot / Auto Login > B4 Desktop AutoLogin Desktop GUI
- Finish


Edit `config.txt`:

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

1. **Speaker Disassembly**
    - Carefully open the speaker case. This may require breaking the plastic, so proceed with caution to avoid damaging the internal circuit and speaker components.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/001.jpg" width="20%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/002.jpg" width="30%">

2. **Raspberry Pi Preparation**
    - Attach heat sinks to the Raspberry Pi to ensure proper thermal management.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/Heatsinks.jpg" width="30%">

3. **Modifying the Pip-Boy Housing**
    - Remove the pegs and mounts from the inside of the Pip-Boy, ensuring to leave the four mounts designated for the Raspberry Pi intact.
    - Using a carving tool, create a square cutout as illustrated in the accompanying diagram to accommodate the encoder knob. Ensure that the drilled hole fits the knob securely.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/003.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/004.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/005.jpg" width="30%">

4. **Wiring Connections**
    - Separate the wires from the main strand.
    - Trim one end of the wires and strip them for soldering.
    - Solder the wires to the encoder switch as depicted in the reference image, then apply heat shrink tubing to prevent short circuits.
    - Repeat this process for the 10-point knob.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/006.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/007.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/008.jpg" width="30%">

5. **Audio USB Cable**
    - Cut the end off the USB cable connected to the audio circuit, noting the wire colors and soldering points.
    - For the angled USB cable, cut one end ensuring the correct angle faces right. Remove the shielding, strip the wires, and solder them according to the original color layout.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/009.jpg" width="20%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/011.jpg" width="30%">

6. **LED USB Cable**
    - Cut and strip another USB cable, removing the green and white wires while stripping the red and black.
    - Connect this USB cable to the LED, then apply heat shrink tubing as shown in the accompanying image.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/012.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/013.jpg" width="30%">

7. **10 Pin Knob Assembly**
    - Modify the bracket to accommodate the knob cables. A soldering iron can be used to carefully enlarge the holes. Place the knob in the enclosure and attach the 3D printed knob.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/015.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/016.jpg" width="30%">

8. **Mounting the Pi and Encoder Knob**
    - Mount the encoder knob. Trim the USB-C connector to fit through the designated hole. Plug the USB-C connector into the Raspberry Pi and secure it in place.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/014.jpg" width="30%">

9. **GPIO Pins**
    - Connect the female ends of both knobs to the GPIO pins as follows:

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/GPIO.jpg" width="60%">

10 Pin Knob Connections:
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


10. **Securing Audio Circuitry**
    - Use super glue to attach the audio circuit and speakers, potentially removing foam from the back of the speakers for better fit.
    - Mount the LCD screen, consider using spacers or cardboard glued to the top of the I/O to ensure it sits flush, accounting for spacing of the female GPIO cable connections.
  
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/021.jpg" width="30%">

11. **Face Plate Modifications**
    - Drill additional holes in the faceplate for screws and the second encoder switch.
    - Bend the pins on the second encoder switch and glue it to the underside of the faceplate, followed by attaching the 3D-printed knob.
    - Affix the LED light cover and screen cover to the faceplate.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/017.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/018.jpg" width="20%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/019.jpg" width="30%"> 

12. **Face Plate Assembly**
    - Connect the USB cables and run the LED into the faceplate, then secure the faceplate using machine screws. Glue the 10 pin knob enclosure to the side of the Pipboy housing.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/020.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/022.jpg" width="30%">

13. **Wrist Magnets Mounting**
    - Attach magnets to the designated mounting points on the wrist mounts, ensuring that opposite ends attract.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/023.jpg" width="30%"> 
    
14. **Padding Assembly**
    - Cut two foam pieces to fit inside the wrist mount. Fold and hot glue vinyl to the foam for added comfort, then secure the padding inside the wrist mounts.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/024.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/025.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/026.jpg" width="20%">

15. **Hinge and Latch Assembly**
    - Drill and screw hinges onto the back and attach the latch on the front, adjusting it as necessary and securing with super glue.

<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/027.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/028.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/029.jpg" width="30%">

16. **Power Tube Assembly**
    - Glue the power tube mounts as indicated in the reference image and attach the cap onto the power tube.
    - Use a small piece of gray Velcro to the back of the PipBoy to enhance stability.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/030.jpg" width="30%"> <img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/031.jpg" width="30%">

17. **Power on!**
    - Finally, connect the USB to the power tube's connector. Note that this may be challenging; future builds may include an improved method. The external battery pack utilized here is recommended for managing the overall amp draw without glitches.
   
<img src="https://github.com/SurvivorGrim/PipBoy-Pi5/blob/main/images/032.jpg" width="50%">
