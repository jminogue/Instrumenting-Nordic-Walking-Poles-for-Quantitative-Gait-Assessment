# Walking_Pole

This combination of Arduino and Python code reads data from an instrumenting walking pole via bluetooth and plots the data in real time. Following data collection, data can be exported as a csv.<br /> <br />
The instrumenting walking pole is drilled in the middle and connected to a loadcell. The loadcell is connected to a circuit using an ESP32 WROOM DA module microcontroller, an HX711 loadcell amplifier, and a 9V battery.<br /><br />
DO NOT CONNECT ANYTHING TO YOUR COMPUTER UNTIL YOU ARE INSTRUCTED TO DO SO!

## Step 1: Install Arduino IDE on your device.
An IDE is an Integrated Development Environment. This is the application where you write code. This IDE is for uploading code to Arduino microcontrollers.<br />
- Visit Arduino’s Website and download the latest version of the Arduino IDE (Figure 1).<br />
- Make sure to download the IDE corresponding with your operating system.<br /><br />
<img src= "Images/SOP_Images/SOP_1.png" width = "500"> <br />
Figure 1 – Arduino Website

## Step 2: Input Board Manager URL in Arduino IDE
This project uses a microcontroller called the ESP32-WROOM-DA Module. We have decided to use this board because of its fast processor, low cost, and its ability to stream data via Bluetooth. A quick tutorial on this board can be found here (https://randomnerdtutorials.com/esp32-bluetooth-classic-arduino-ide/). In order to use this microcontroller with the Arduino IDE, we need to first put a link in the IDE telling it where to find the “board manager” for this specific board.<br />
- In the Arduino IDE, go to File -> Preferences.<br />
 
- In the “Additional boards manager URLs” text box (Figure 2), paste in the following link:
 https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
- If there is already a link in this box, or if you would like to add more than one link, select the icon to the right of the text box, and then separate your links by line (Figure 3).<br /> <br />
<img src= "Images/SOP_Images/SOP_2.png" width = "500"> <br />
Figure 2 – Arduino IDE Preferences <br /> <br />
<img src= "Images/SOP_Images/SOP_3.png" width = "500"> <br />
Figure 3 – Adding multiple board manager URLs <br />
- Press OK when you are finished. 

## Step 3: Install Board Manager for ESP32
- Select the “tools” tab on the top toolbar of the Arduino IDE and navigate to “Board” -> “Boards Manager” (Figure 4).<br /> <br />
<img src= "Images/SOP_Images/SOP_4.png" width = "500"> <br />
Figure 4 – Navigating to “Boards Manager”<br /> 

- In the boards manager search bar, search esp32 and install the module from “Espressif Systems” (Figure 5).<br /><br /> 
<img src= "Images/SOP_Images/SOP_5.png" width = "500"> <br />
Figure 5 – Downloading the board module for the esp32<br /> 
- At this point, you should be able to navigate back to your boards and find the ESP-32-WROOM-DA Module, which you should now select (Figure 6). <br /> <br /> 
<img src= "Images/SOP_Images/SOP_6.png" width = "500"> <br />
Figure 6 – Selecting the ESP32 from Boards Manager <br /> 

## Step 4: Ensure that the Arduino IDE can find the ESP32
- You may now connect the esp32 to your computer after you read the following warning
- WARNING: Do not connect the esp32 to your computer if it is also connected to a battery! This can fatally harm your computer. Disconnect the battery from the esp32 before connecting to your computer. 
- From the sketch screen of the Arduino IDE, select the “Select Board” drop-down and select “Select other board and port…” (Figure 7)<br /><br /> 
<img src= "Images/SOP_Images/SOP_7.png" width = "500"> <br />
Figure 7 – Select Board<br /><br /> 
- Enter esp32-wroom in the search bar to find our board, then select the port that it is connected to on your computer
- Note: The esp32 must be connected to the computer using a micro-USB cable.<br /> <br />
<img src= "Images/SOP_Images/SOP_8.png" width = "500"> <br />
Figure 8 – Selecting board and port<br /><br />
- If no ports are shown, your computer may not be recognizing the esp32. To check this, navigate to your device manager and see if there is a device under “other devices” with a yellow warning icon on it. If this is the case, you need to download an additional driver found here (https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads). 
  - Download the latest zipped driver to your computer and extract it to your desktop so it’s easy to find.
  - Right click on the device in “other devices” in your device manager and select “update driver.”
  - Allow your computer to automatically find the driver or manually navigate to it on your desktop.
  - Now, your computer should be able to recognize your esp32 and list your available ports. Select the port that your esp32 is connected to

## Step 5: Upload Arduino Code to the esp32
- The "Arduino Code" folder in this repository contains the following 3 scripts:
   - LoadCellCalibration: This sketch will help you identify the calibration factor for your load cell.
   - Print_Force_Serial: This sketch will print force readings to the serial monitor in the Arduino IDE. You can use this sketch to check your output values from the ESP32.
   - Print_Force_BT: This sketch will print force readings via bluetooth. This is the code you need to run the  Python interface that reads force via bluetooth. 
- Once you have successfully uploaded the Print_Force_BT code, you may disconnect your computer from the Arduino and reconnect the Arduino to its battery. It is very important that you do not connect to the battery until AFTER you have disconnected from your computer. It is okay if the Arduino loses power during this switch. The code has now been uploaded to the board and the board will remember the code when it reconnects to a power source. 

## Step 6: Run the Executable File and Collect Data
- The walkingpole_live_plot.exe file allows you to run the GUI without having to install python or any other dependencies to your computer. If you choose to use this executable, you are done.<br /> <br />


# If You're Not Using the Executable...
- If you haven't already, install Python (https://www.python.org/downloads/) (scroll to bottom of the page to find installers)
- Before proceeding with the install, make sure you add python to your path (Figure 9).<br /><br />
<img src= "Images/SOP_Images/SOP_9.png" width = "500"> <br /> 
Figure 9 – Installing Python <br /> <br />

## Install Necessary Packages
Install the necessary packages manually in the command prompt using the “pip” command
  - Open your command prompt
  - Enter “pip install _________” for each package <br /><br />
  <img src= "Images/SOP_Images/SOP_14.png" width = "500"><br /><br />
- Necessary packages (enter the exact name after “pip install ____”)
  - wxPython
  - matplotlib
  - numpy
  - sys
  - csv
  - pybluez
    - pybluez requires Microsoft C++ Build Tools in order to run, which you can install at the following link: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    - During installation, make sure to select **Desktop Development with C++** and **Universal Windows Platform development**
 
## Step 10: Run the python code
- Ensuring the Arduino code has been uploaded to the walking stick and that the stick is on and connected to battery power, you can finally run the python code!
- Open IDLE (downloaded with python)<br /><br />
<img src= "Images/SOP_Images/SOP_15.png" width = "400"><br />
- On the toolbar, select “File” -> “Open” and locate your main.py file<br /><br />
<img src= "Images/SOP_Images/SOP_16.png" width = "400"><br />
- On the toolbar, select “Run” -> “Run Module”<br /><br />
<img src= "Images/SOP_Images/SOP_17.png" width = "400"><br />
 


