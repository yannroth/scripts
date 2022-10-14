# Configuration

Folder to store configurations

## gTile
Configuration wizard is buggy, use text editor to directly edit conf file.

To get configuration:
´´´
dconf dump /org/gnome/shell/extensions/gtile/ > gtile.conf
´´´

To apply configuration:
´´´
dconf load /org/gnome/shell/extensions/gtile/ < gtile.conf
´´´
