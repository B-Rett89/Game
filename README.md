# Game

This is a simple prototype shooter inspired by Doom 64. The game is built with Python and Pygame and contains a single level.

## Requirements
- Python 3
- Pygame (`pip install pygame`)

## How to Run
```bash
python3 game.py
```

## Running on Android
The game can be packaged for Android with
[Python for Android](https://github.com/kivy/python-for-android) or run
with Pydroid3. Touch input is supported and a paired bluetooth gamepad can
also be used.

### Controls
- W/A/S/D: move the player
- Left mouse button: shoot
- U: open upgrade menu after completing a level or anytime
- ESC: pause/resume (Q quits from pause)

Collect coins and defeat enemies to earn points. When all enemies are defeated, move to the green exit box to finish the level. Points can be spent in the upgrade menu on improved textures for the gun, enemies, level and HUD. Each upgrade costs 10 points and there are 20 upgrade levels.
