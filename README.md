# 👑 SKB 👑

🤖 SKB (formerly Tibia PilotNG) is an advanced 24/7 Full-Auto PixelBot for Tibia. Core logic has been migrated to Rust for improved performance and robustness, with the new core residing in the `rust_bot_ng` directory.

![Logo](docs/assets/images/logo.png)

## 📖 A brief history

This project began in December 2023 as PilotNG, a Python-based bot. It incorporated all necessary features for 24/7 operation and was actively used for bot farming. The original Python version demonstrated significant success, with multiple characters farming substantial amounts daily.

Recognizing the potential for performance and maintainability improvements, the core functionalities of PilotNG have been rewritten in Rust, leading to the birth of SKB. The new Rust core, located in the `rust_bot_ng` directory, offers enhanced speed and robustness. While the Python version was functional, the migration to Rust marks a significant evolution of the project. This repository now contains the Rust-based SKB, building upon the lessons learned and successes of its Python predecessor.

Below you'll find some images and videos of how the original bot worked, prints of its UI, and updated instructions on how to install and run the new Rust-based SKB.

## 📷 Gallery

![UI](docs/assets/images/ui.png)

### [You can see videos of it working on my Youtube channel](https://www.youtube.com/channel/UC4uyI035S2h0z862wpYVqXA)

## 📝 CAVEBOT SCRIPTS (SEE SCRIPTS FOLDER)

- DRAKEN WALLS NORTH ✔️
- MINOTAUR CULT -1 AND -2 ✔️

## 🟢 Features

- WORKS ON TIBIA GLOBAL ✔️
- 100% FULL AUTO ✔️
- CAVEBOT WITH WAYPOINTS (COORDINATES NOT CLICKMAP) ✔️
- SAVE AND SHARE CAVEBOT SCRIPTS ✔️
- CONFIGURABLE HOTKEYS ✔️
- CAITING CREATURES OVER BOXES ✔️
- OPEN DOORS, TRAVEL, CLICK ON BOATS ✔️
- IGNORE CREATURES ✔️
- DROP LOOT ON THE GROUND ✔️
- REFILER ✔️
- DEPOSITER ✔️
- WALK OVER THE FIRE ✔️
- ALERTS ✔️
- AUTO AMULET/RING ✔️
- COMBO SPELLS ✔️
- DROP FLASKS ✔️
- DEPOSIT GOLD ✔️
- DEPOSIT ITEMS ✔️
- FOOD EATER ✔️
- TARGETING ✔️
- HEALING ✔️
- QUICK LOOTING ✔️
- DEFAULT MESSAGE WHEN SEE A PLAYER ON THE SCREEN ✔️
- AUTO HUR ✔️
- AUTO CURE POISON ✔️
- FOLLOW ENEMY OR GO TO BOX TO KILL MONSTERS (DEPENDS THE CHAR LEVEL) ✔️

## 🔴 HARDWARE REQUIREMENTS

This bot needs good processing power to work properly (fast) i tested it with weak machines and didn't succeed, of the 3 machines i had running bots they all had a ryzen 5 5600 (6 core/12 threads +- 3.5ghz), use an equal or superior processor (or you can also use a worse one but overclock it), in addition to less input detection I chose to use a leonardo arduino to simulate mouse and keyboard inputs, you need a leonardo arduino to use this bot, if you don't have one you can change the source manually to use pyautogui or derivatives, or use a driver, but note that this may result in easier detection, inside the source I will leave a . ino file with the arduino code, just send it to your arduino leonardo and it will work (remember to leave the arduino as the standard COM33 port, otherwise the bot will not work), I also recommend spoofing the arduino (it's not necessary to run the project) so that it doesn't have the id of the arduino board but that of some input device (mouse/keyboard), thus making detection more difficult.

![Arduino](docs/assets/images/arduino.png)

## 🔴 SOFTWARE REQUIREMENTS

THE BOT ONLY WORKS IN 1920X1080 RESOLUTION

TESTED ONLY ON WIN10

- [PYTHON 3.11.7](https://www.python.org/downloads/release/python-3117/) (Still required for utility scripts and potentially `XET-SpecterHID`)
- [RUST (STABLE EDITION)](https://www.rust-lang.org/tools/install)
- [CARGO](https://doc.rust-lang.org/cargo/getting-started/installation.html) (Usually installed with Rust)
- [POETRY](https://python-poetry.org/) (If using Python utilities that depend on it)
- [TESSERACT-WINDOWS](https://github.com/UB-Mannheim/tesseract/wiki)
- [VIRTUAL DISPLAY](https://www.amyuni.com/downloads/usbmmidd_v2.zip&v=ybHKFZjSkVY)
- [OBS](https://obsproject.com/pt-br/download)

The primary configuration for the bot is now `rust_bot_ng/config.toml`.

COMMANDS TO ACTIVATE THE VIRTUAL DISPLAY:

- Extract the file, then:

```bash
cd C:\DIRECTORY\OF\EXTRACTED\FOLDER
deviceinstaller64 install usbmmidd.inf usbmmidd
```

-Add virtual display:

```bash
deviceinstaller64 enableidd 1
```

Once you have the second monitor activated, make sure your resolution is 1920x1080, then just open obs, add a game capture, select tibia and remove the pointer, then just open the game capture in windowed mode and click to maximise the window (windowed fullscreen)

OBS: If you have more than one physical screen, switch them all off and stick with just one

🔴 **IMPORTANT** YOU NEED TO REMOVE THE POINTER FROM THE OBS GAME CAPTURE, OTHERWISE IT MAY RESULT IN BUGS

⚠️ **OPTIONAL** IF YOU WANT, SPOOF THE VIRTUAL DISPLAY FOR LESS DETECTION

## 🔴 TIBIA CONFIG REQUIREMENTS

YOU NEED TO USE THIS CONFIGS IN YOUR CLIENT, OTHERWISE WILL NOT WORK

![Controls](docs/assets/images/controls.png)
![General Hotkeys](docs/assets/images/generalHotkeys.png)
![Action Bar Hotkeys](docs/assets/images/actionBarHotkeys.png)
![Custom hotkeys](docs/assets/images/customHotkeys.png)
![Interface](docs/assets/images/interface.png)
![HUD](docs/assets/images/hud.png)
![Console](docs/assets/images/console.png)
![Game Window](docs/assets/images/gameWindow.png)
![Action Bars](docs/assets/images/actionBars.png)
![Graphics](docs/assets/images/graphics.png)
![Effects](docs/assets/images/effects.png)
![Misc](docs/assets/images/misc.png)
![Gameplay](docs/assets/images/gameplay.png)

## ⚙️ HOW TO SETUP

🔴 USE AT YOUR OWN RISK

- DOWNLOAD AND INSTALL THE SOFTWARE DEPENDENCIES (Rust, Python, Tesseract, etc.)

- MAKE SURE THE ARDUINO IS PLUGGED IN (if used, see Hardware Requirements)

- CLONE/DOWNLOAD THE PROJECT

### Running the Rust Core (SKB)

1.  Navigate to the Rust core directory:
    ```bash
    cd rust_bot_ng
    ```
2.  Build the project (release mode for performance):
    ```bash
    cargo build --release
    ```
3.  Configure the bot by editing `config.toml`.
4.  Run the compiled executable:
    ```bash
    target/release/rust_bot_ng.exe 
    ```
    (The executable name might vary based on your project configuration in `Cargo.toml`)

### Python Utilities (If still applicable)

If you need to run Python-based utilities or scripts that are part of the project:

1.  Ensure Python and Poetry are installed.
2.  Install Python dependencies:
    ```bash
    poetry install
    ```
3.  Run the specific Python script (e.g., if `main.py` is now a utility or launcher):
    ```bash
    poetry run python main.py 
    ```
    (Or `python utility_script_name.py` as appropriate)

## 🤝 Contributing

Contributions are always welcome! Create a pull request xD

## 💬 Lets talk

if you want to talk to me, add me on [**Linkedin**](https://br.linkedin.com/in/paulordyl) or [**Discord**](https://discord.gg/YzVhxzy4W6)

<a href="https://www.buymeacoffee.com/paulordyl" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>


# ❤️ Acknowledgements

I started this project on the basis of the [**PyTibia**](https://github.com/lucasmonstrox/PyTibia) developed by [**lucasmonstrox**](https://github.com/lucasmonstrox), he did a great job, I was able to learn a lot from his project and the techniques he used, take a look at his project, he keeps updating it to this day.
