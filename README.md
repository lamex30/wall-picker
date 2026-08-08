# slanted wall-picker for kde plasma
<img width="1920" height="1080" alt="screenshot" src="https://github.com/user-attachments/assets/6d81398e-571a-43d4-87bc-1305fca3888c" />
<img width="480" height="270" alt="video" src="https://github.com/user-attachments/assets/b65fe0c2-a93c-4759-ae20-1598fe30678a" />

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

```bash
curl -sL [https://raw.githubusercontent.com/lamex30/wall-picker/main/install.sh](https://raw.githubusercontent.com/lamex30/wall-picker/main/install.sh) | bash
