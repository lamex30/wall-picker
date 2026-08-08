#!/bin/bash

echo "installing slanted wall-picker..."

if command -v pacman &>/dev/null; then
  echo "arch linux detected. installing python-pyqt6..."
  sudo pacman -S --needed --noconfirm python-pyqt6
elif command -v apt &>/dev/null; then
  echo "debian/ubuntu detected. installing python3-pyqt6..."
  sudo apt update && sudo apt install -y python3-pyqt6
else
  echo "unsupported package manager. please install pyqt6 manually."
fi

echo ""
echo -n "enter the full path to your wallpapers directory (e.g., ~/Pictures/Wallpapers): "
read WALL_PATH

mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications

echo "downloading the script..."
curl -sL https://raw.githubusercontent.com/ТВОЙ_НИК/wall-picker/main/wall-picker.py -o ~/.local/bin/wall-picker

sed -i "s|WALLS_DIR = .*|WALLS_DIR = os.path.expanduser(\"$WALL_PATH\")|g" ~/.local/bin/wall-picker
chmod +x ~/.local/bin/wall-picker

echo "creating desktop entry..."
cat <<EOF >~/.local/share/applications/wall-picker.desktop
[Desktop Entry]
Name=Wall Picker
Comment=Slanted Wallpaper Picker for KDE
Exec=$HOME/.local/bin/wall-picker
Icon=preferences-desktop-wallpaper
Type=Application
Categories=Utility;
Terminal=false
EOF

echo ""
echo "done! search for 'Wall Picker' in your app menu or krunner."
echo "you can bind a custom shortcut to it via system settings -> shortcuts."
