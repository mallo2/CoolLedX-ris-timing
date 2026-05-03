# CoolLEDX Ris-Timing

First and foremost, this project is based on UpDryTwist’s CoolLEDX-driver repository. 
It is a driver project for CoolLEDX LED panels, enabling these panels to be controlled via Bluetooth. The project is written in Python and uses the Bleak library for Bluetooth interactions.
All the code for this project is linked to the project’s core folder and is covered by its original MIT license.

The aim of this project is to use CoolLEDX LED panels for display purposes during motorsport races, showing useful information to the driver (lap times, position, etc.).
All the code for this project is linked to the project’s pro folder and is covered by its own license.

## Usage

You need to have a functioning Bluetooth device. This package
uses [Bleak](https://github.com/hbldh/bleak) for all its Bluetooth interactions. 
Personally, I have tried this on macOS and Windows.  
On Windows, it works well. But On macOS, I have had a lot of trouble with the Bluetooth stack, and it is very unreliable.
Bleak normally returns MAC addrsses on Windows, but on macOS it returns UUIDs. I have not been able to get the UUIDs to work, so I have only been able to use this on Windows.

## Credits and Sources

#### UpDryTwist

This project is based on the work of UpDryTwist, who developed the CoolLEDX driver ([coolledx-driver](https://github.com/UpDryTwist/coolledx-driver)) in Python. 
His work was essential in enabling the control of CoolLEDX LED panels via Bluetooth.
I opened an issue on his repository as it contained errors such as circular imports or timeouts that blocked all communication with the panel.
However, this repository forms the basis of this project, and I am grateful to him for his work.

#### TheDavSmasher

TheDavSmasher, for his part, is a contributor to the UpDryTwist project, having created a fork of the project ([coolledx-driver](https://github.com/TheDavSmasher/coolledx-driver)) in order to refactor the errors mentioned in the original repository.
This fork formed the basis of my work, as it corrected the errors in the original repository and allowed me to establish communication with the panel, which was essential for my project.
I am also grateful to him for his work.

#### Mallo2 (myself)

I used the work of UpDryTwist and TheDavSmasher to create this project ([CoolLEDX Ris-Timing](https://github.com/mallo2/CoolLedX-ris-timing)). 
Once communication with the display was established, I noticed that the text-sending function was faulty as it did not adhere to the display’s communication protocol, meaning that commands sent to the display were often misinterpreted, and random dots appeared on the screen.
I also found that the JT image sending feature was working. So, I decided to focus on sending JT images by converting the text into a JT image.
Once I had successfully sent text in JT format to the display, and it was displaying it correctly, I decided to automate the retrieval of telemetry data from a race in the Belgian Superquad Championship, in order to display useful information for the rider on the display during the race.
Now that I finally have a working solution, I’ve decided to completely refactor the code that served as my basis.
Beyond that, my aim is to turn this project into a portfolio piece, to showcase my software development skills and the resourcefulness required to make a project of this kind work, starting from a base code that didn’t work and arriving at a functional solution.

## CoolLEDX Ris-Timing Installation

Make sure you have Python 3.8 or higher installed on your system.

### Installation

To install CoolLEDX Ris-Timing:

1. Clone the repository to your PC:
   ```bash
   git clone https://github.com/mallo2/CoolLedX-ris-timing
   ```
2. Navigate to the project directory:
   ```bash
   cd CoolLedX-ris-timing
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the main script:
   ```bash
    python main.py
    ```