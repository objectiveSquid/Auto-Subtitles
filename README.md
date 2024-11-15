# Auto Subtitles
A python program for automatically putting subtitles on any media, using Soundcard, VOSK and Deep Translator.

## Features
  - Automatically generates subtitles from the system's audio output.
  - Supports Linux, with potential compatibility for Windows and MacOS.
  - Can automatically translate into most languages on the fly.
  - More features coming!

## Prerequisites
  - Python 3.12+ with pip (on linux you may need to install pip separately)

## Installation
This project has NOT been tested to work on any Windows/MacOS versions! Though issues/PRs are welcome.

### If you have Git installed, you can clone the repository
```sh
git clone https://github.com/objectiveSquid/Autosubtitles.git
cd autosubtitles
```

### If you don’t have Git installed, you can download the repository as a ZIP file
  - Go to the GitHub repository page in another tab: [https://github.com/objectiveSquid/autosubtitles](https://github.com/objectiveSquid/autosubtitles)
  - Click the green Code button, then select Download ZIP.
  - Extract the downloaded ZIP file.
  - Open a terminal or command prompt and navigate to the extracted folder.


## Running it
### Unix-based OS's (Linux, MacOS...)
```sh
python3.12 autosubtitles
```

### Windows
```sh
py -3.12 autosubtitles
```

## Manually installing pip requirements

### Unix-based OS's (Linux, MacOS...)
```sh
python3.12 -m pip install -r requirements.txt
```

### Windows
```sh
py -3.12 -m pip install -r requirements.txt
```
