# slanted wall-picker for kde plasma
<img width="1920" height="1080" alt="screenshot" src="https://github.com/user-attachments/assets/fa23736d-299c-40d1-a651-a715d27e54dc" /> | <img width="480" height="270" alt="video" src="https://github.com/user-attachments/assets/37dedcb0-4249-4f4e-b743-3c04699e34b5" />

a smooth, coverflow-style 3d slanted wallpaper picker for kde plasma. written in python with pyqt6, it runs natively on wayland and x11 without heavy dependencies.

## features
- fully native & lightweight (pyqt6)
- smooth kinetic scrolling
- dynamic coverflow-style 3d scale animation
- seamless gaps and pixel-perfect geometry
- automatically applies wallpaper on click
- includes a `.desktop` entry for easy integration

## one-click install
just paste this command into your terminal. it will install `pyqt6` (if you are on arch or debian/ubuntu), ask for your wallpapers directory, and set everything up automatically:

curl -sL https://raw.githubusercontent.com/lamex30/wall-picker/main/install.sh | bash

## usage

after installation, Wall Picker will be available in your application launcher and krunner.
    1. scroll / arrow keys: navigate through wallpapers
    2. left click / enter: apply wallpaper and close
    3. escape: close without applying

setting a custom shortcut (for kde plasma users)
since the installer automatically creates a .desktop file, you can easily bind a global shortcut to launch the picker:
    1. open system settings -> shortcuts.
    2. click add new at the bottom -> application.
    3. search for wall picker and select it.
    4. assign your preferred shortcut (e.g., meta + w).
    5. click apply.
