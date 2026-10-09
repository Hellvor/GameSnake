# GameSnake

A custom Python frontend for Libretro cores.

Started on a Friday because college was boring.

## Current Features

✅ Loads mGBA

✅ Loads GBA ROMs

✅ Video output

✅ Keyboard input

✅ Audio that mostly behaves itself

## Known Issues

❌ Audio occasionally turns into breakfast cereal

❌ No save support

❌ No controller support

❌ Probably several things I haven't found yet

## Tested Games

- Pokémon FireRed

## Roadmap

- Better audio
- Save files
- Save states
- Controllers
- Fast-forward
- More cores

## Development Status

"It's alive."

## Installation

### Requirements

- Python 3.11 or newer
- Pygame
- NumPy
- A Libretro compatible core (currently tested with mGBA)

### Clone the Repository

```bash
git clone https://github.com/YourUsername/GameSnake.git
cd GameSnake
```

### Install Dependencies

```bash
pip install pygame numpy libretro
```

### Core Setup

Create the following folder structure:

```text
GameSnake/
├── GameSnake.py
└── mGBA Core/
    └── mgba_libretro.dll
```

Place your copy of `mgba_libretro.dll` inside the `mGBA Core` folder.

### Running

```bash
python GameSnake.py
```

A file picker will appear allowing you to select a Game Boy, Game Boy Color, or Game Boy Advance ROM
