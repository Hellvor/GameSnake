from libretro.core import Core
from libretro.api import retro_game_info
from libretro.ctypes import c_void_ptr
import pygame
import tkinter as tk
from tkinter import filedialog
import ctypes
import numpy as np

global globalKeys

mGBA = Core(".\\mGBA Core\\mgba_libretro.dll")

audioBuffer = bytearray()

inputMap = {
    pygame.K_z: 8,       # Z key = GBA A Button
    pygame.K_x: 0,       # X key = GBA B Button
    pygame.K_RETURN: 3,  # Enter key = GBA Start Button
    pygame.K_SPACE: 2,   # Space key = GBA Select Button
    pygame.K_UP: 4,      # Arrow Up = D-Pad Up
    pygame.K_DOWN: 5,    # Arrow Down = D-Pad Down
    pygame.K_LEFT: 6,    # Arrow Left = D-Pad Left
    pygame.K_RIGHT: 7,   # Arrow Right = D-Pad Right
}

activeButtons = set()
globalKeys = []

def video_refresh(data, width, height, pitch):
    global screen

    gameSurface = pygame.Surface((width, height), 0, 16)
    pygame_stride = width * 2
    base_address = data.value if hasattr(data, 'value') else int(data)
    
    surface_buffer = gameSurface.get_buffer()

    for y in range(height):
        row_pointer = base_address + (y * pitch)
        row_bytes = ctypes.string_at(row_pointer, pygame_stride)
        surface_buffer.write(row_bytes, y * pygame_stride)

    del surface_buffer

    screen.blit(gameSurface, (0, 0))
    
    pygame.display.update()

def audio_sample(*args):
    pass

def audio_sample_batch(data, frames, *args):
    global audioBuffer

    byte_count = frames * 4
    audioBuffer.extend(
        ctypes.string_at(data, byte_count)
    )

    return frames

def input_poll(*args):
    global globalKeys
    pygame.event.pump()
    globalKeys = pygame.key.get_pressed()

def input_state(port, device, index, id):
    global globalKeys

    #print(f"Input State Check: Port={port}, Device={device}, Index={index}, ID={id}")

    if id == 256:
        mask = 0

        if globalKeys[pygame.K_x]:      # B
            mask |= (1 << 0)

        if globalKeys[pygame.K_z]:      # A
            mask |= (1 << 8)

        if globalKeys[pygame.K_SPACE]:
            mask |= (1 << 2)

        if globalKeys[pygame.K_RETURN]:
            mask |= (1 << 3)

        if globalKeys[pygame.K_UP]:
            mask |= (1 << 4)

        if globalKeys[pygame.K_DOWN]:
            mask |= (1 << 5)

        if globalKeys[pygame.K_LEFT]:
            mask |= (1 << 6)

        if globalKeys[pygame.K_RIGHT]:
            mask |= (1 << 7)

        #if mask:
            #print("MASK =", hex(mask))

        return mask
    
    return 0

def enviroment(cmd, data):
    # Handle Command 17 (Variables)
    if cmd == 17:
        if data:
            return False

    # Handle Command 10 (Pixel Format)
    if cmd == 10:
        if data:
            # 1. Cast the pointer to a C integer pointer, then read its contents (.value)
            format_id = ctypes.cast(data, ctypes.POINTER(ctypes.c_int)).contents.value
            #print(f"mGBA wants to use Pixel Format: {format_id}")
            
            # 2. Return True to tell mGBA "I agree to use this format!"
            return True

    # Handle Command 15 (Geometry Setup)
    if cmd == 15:
        #print("mGBA sent screen dimensions. Handshake accepted!")
        return True

    # Safe fallback default for everything else
    return True

mGBA.set_video_refresh(video_refresh)
mGBA.set_audio_sample(audio_sample)
mGBA.set_audio_sample_batch(audio_sample_batch)
mGBA.set_input_poll(input_poll)
mGBA.set_input_state(input_state)
mGBA.set_environment(enviroment)

root = tk.Tk()
root.withdraw()

pygame.mixer.pre_init(
    frequency=48000,
    size=-16,
    channels=2,
    buffer=1024
)
pygame.init()

audioChannel = pygame.mixer.Channel(0)

screen = pygame.display.set_mode((240, 160))
pygame.display.set_caption("GameSnake")

romPath = filedialog.askopenfilename(
    title="Select a ROM:",
    filetypes=[("GameBoy Advance", "*.gba"), ("GameBoy Color", "*.gbc"),("GameBoy", "*.gb"),("All Files", "*.*")]
)

if romPath:
    #print(f"Loading: {romPath}")
    root.destroy()

    with open(romPath, "rb") as f:
        romData = f.read()
    romSize = len(romData)

    cBuffer = ctypes.create_string_buffer(romData, romSize)
    
    gameInfo = retro_game_info(
        path=romPath.encode('utf-8'),
        data=c_void_ptr(ctypes.addressof(cBuffer)),
        size=romSize,
        meta=None
    )

    mGBA.load_game(gameInfo)
#else:
    #print("No file selected! Exiting...")

pollRate = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #elif event.type == pygame.KEYDOWN:
            #print(f"Pygame Window captured physical key press ID: {event.key}")
    mGBA.run()
    if len(audioBuffer) >= 16384:
        chunk = bytes(audioBuffer[:16384])
        del audioBuffer[:16384]

        samples = np.frombuffer(
            chunk,
            dtype=np.int16
        ).reshape(-1, 2)

        sound = pygame.sndarray.make_sound(
            samples.copy()
        )

        if audioChannel.get_busy():
            audioChannel.queue(sound)
        else:
            audioChannel.play(sound)
    pollRate.tick(60)

pygame.quit()
print("GameSnake closed safely")
