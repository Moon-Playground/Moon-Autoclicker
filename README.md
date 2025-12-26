# Moon Auto Clicker

A powerful, modern, and highly customizable auto-clicker built with Python and CustomTkinter. Featuring a sleek dark-themed UI, global hotkeys, and a robust preset system.

## Features

- **Modern UI**: Clean, responsive design using `customtkinter`.
- **Precise Timing**: Set intervals down to the millisecond (Hours, Minutes, Seconds, Milliseconds).
- **Click Configuration**:
    - Select mouse button (Left, Right, Middle).
    - Select click type (Single, Double).
- **Repetition Options**:
    - Repeat until stopped (Infinite).
    - Repeat for a specific number of times.
- **Cursor Location**:
    - Click at the current cursor position.
    - Click at a custom coordinate with a built-in "Pick Position" tool (includes a 3-second countdown).
- **Preset System**:
    - Save your favorite timing configurations.
    - Load presets instantly.
    - Delete unwanted presets.
- **Global Hotkeys**:
    - Configurable Start/Stop toggle (Default: `F6`).
    - Emergency Exit (Default: `F5`).

## Project Structure

```
autoclicker_src/
├── autoclicker/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── auto_clicker.py          # Main application & UI logic
│   ├── res/                     # Resources (icons, etc.)
│   │   └── icon.ico
│   └── utils/                   # Modular utility classes
│       ├── __init__.py          # Utils aggregator
│       ├── config.py            # Main configuration (hotkeys)
│       ├── hotkeys.py           # Global hotkey management
│       └── preset.py            # Preset management (load/save/delete)
│
├── config.toml                  # Hotkey configuration storage
├── preset.toml                  # Timing presets storage
├── autoclicker.spec             # PyInstaller build specification
└── README.md
```

## Installation

### Prerequisites
- Python 3.11+

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running from source
```bash
python -m autoclicker
```

## Building Standalone Executable

This project includes a PyInstaller `.spec` file for building a single-file `.exe`.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the build command:
   ```bash
   pyinstaller autoclicker.spec --noconfirm
   ```
3. The standalone executable will be found in the `dist/` directory as `MoonAutoClicker.exe`.

## Configuration

- **Hotkeys**: Configurable via the "Hotkeys" tab. These settings persist in `config.toml`.
- **Presets**: Timing configurations can be saved in the "Settings" tab and persist in `preset.toml`.

## Dependencies

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter): Modern themed widgets for Tkinter.
- [pynput](https://github.com/moses-palmer/pynput): Mouse control.
- [keyboard](https://github.com/boppreh/keyboard): Global hotkey handling.
- [pyautogui](https://github.com/asweigart/pyautogui): Cursor position picking.
- [tomlkit](https://github.com/sdispater/tomlkit): TOML style-preserving parser.
