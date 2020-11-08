import keyboard
import time
import ctypes
import PIL.ImageGrab
import PIL.Image
import winsound
import os
import mss
from colorama import Fore, Style, init
from itertools import cycle
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# class Color(Enum):
#     purple = (250, 100, 250)
#     red = (250, 100, 250)
#     yellow = (250, 100, 250)


class GunMode(Enum):
    pistol = {"hold":False, "mode":5, "grabzone":15}
    phantom = {"hold":True, "mode":3, "grabzone":10}
    sniper = {"hold":False, "mode":1, "grabzone":5}


class Gun():
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def name(self): return self._name

    @name.setter
    def name(self, val): self._name = val

    @property
    def value(self): return self._value

    @value.setter
    def value(self, val): self._value = val

dat = []
with open("guns.txt") as w:
    dt_tmp = w.readlines()
    for gun in dt_tmp:
        gn_nm = gun.split(":")[0].strip()
        gun_prs = gun.split(":")[1].strip().split(",")
        prs = {}
        for gun_pr in gun_prs:
            p, v = [i.strip() for i in gun_pr.split("-")]
            if "false" in v.lower(): prs[p] = False
            elif "true" in v.lower(): prs[p] = True
            else: prs[p] = int(v)
            # dat[gn_nm] = {}
            # dat[gn_nm][p] = v
        dat.append(Gun(gn_nm, prs))
# pistol = Gun('pistol', {"hold":False, "mode":5, "grabzone":15})
# phantom = Gun('phantom', {"hold":True, "mode":3, "grabzone":10})

Colors = {
    "Purple": (250, 100, 250),
    "Red": (255, 0, 0),
    "Yellow": (249, 236, 73)
}

try:
    with open("color.txt", "r") as file:
        x = file.readlines()[0].strip()
        x = [int(i.strip()) for i in x.split(",")]
        # x = [i.strip() for i in x]
        Colors["Yellow"] = (x[0], x[1], x[2])
        print("color yellow set to: ", (x[0], x[1], x[2]))
        with open("output.txt", "w") as file_w:
            file_w.write(str((x[0], x[1], x[2])))

except Exception as e:
    print(e)

S_HEIGHT, S_WIDTH = (PIL.ImageGrab.grab().size)

# PURPLE_R, PURPLE_G, PURPLE_B = (250, 100, 250)
# RED_R, RED_G, RED_B = (250, 100, 250)
# YELLOW_R, YELLOW_G, YELLOW_B = (250, 100, 250)

TOLERANCE = 60

GRABZONE = 10
TRIGGER_KEY = "ctrl + alt"
SWITCH_KEY = "ctrl + tab"
GRABZONE_KEY_UP = "ctrl + up"
GRABZONE_KEY_DOWN = "ctrl + down"
HOLD_KEY = "ctrl + shift"
COLOR_SWITCH_KEY = "ctrl + F1"
# GUN_MODE_KEY_DOWN = "ctrl + 1"
GUN_MODE_KEY_UP = "ctrl + 1"
BURST_FIRE_MODE_TOGGLE_KEY = "ctrl + `"
mods = ["slow", "medium", "fast", "rapid", "super rapid", "heavy rapid"]
TIME_MODS = [0.5, 0.25, 0.12, 0.07, 0.04, 0.02]
COLORS = cycle([Colors["Purple"], Colors["Red"], Colors["Yellow"]])

# gun_modes = cycle([GunMode.pistol, GunMode.phantom, GunMode.sniper])
# gun_modes = cycle([pistol, phantom])
gun_modes = cycle(dat)

class FoundEnemy(Exception):
    pass


class triggerBot():
    def __init__(self):
        self.toggled = False
        self.mode = 3
        self.last_reac = 0
        self.hold = False
        # self.color_number = 0
        self.color = Colors["Purple"]
        self.set_gunmode(next(gun_modes))
        self.burst_fire = False

    def toggle(self):
        self.toggled = not self.toggled

    def switch_color(self):
        self.color = next(COLORS)

    def switch(self):
        if self.mode != 5:
            self.mode += 1
        else:
            self.mode = 0
        if self.mode == 0:
            winsound.Beep(200, 200)
        elif self.mode == 1:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
        elif self.mode == 2:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
        elif self.mode == 3:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
        elif self.mode == 4:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
        elif self.mode == 5:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)

    def click(self):
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up

    def right_click(self):
        ctypes.windll.user32.mouse_event(8, 0, 0, 0, 0) # Right down
        ctypes.windll.user32.mouse_event(10, 0, 0, 0, 0)  # Right up

    def approx(self, r, g, b):
        return self.color[0] - TOLERANCE < r < self.color[0] + TOLERANCE and self.color[1] - TOLERANCE < g < self.color[1] + TOLERANCE and self.color[2] - TOLERANCE < b < self.color[2] + TOLERANCE

    def grab(self):
        with mss.mss() as sct:
            bbox = (int(S_HEIGHT / 2 - GRABZONE), int(S_WIDTH / 2 - GRABZONE), int(S_HEIGHT / 2 + GRABZONE),
                    int(S_WIDTH / 2 + GRABZONE))
            sct_img = sct.grab(bbox)
            # Convert to PIL/Pillow Image
            return PIL.Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    def scan(self):
        start_time = time.time()
        pmap = self.grab()
        try:
            # with ThreadPoolExecutor.
            for x in range(0, GRABZONE * 2):
                for y in range(0, GRABZONE * 2):
                    r, g, b = pmap.getpixel((x, y))
                    if self.approx(r, g, b):
                        raise FoundEnemy
        except FoundEnemy:
            self.last_reac = int((time.time() - start_time) * 1000)
            if not self.hold:
                if self.burst_fire:
                    self.right_click()
                else: self.click()
                time.sleep(TIME_MODS[self.mode])
                # print("sleeping for:", TIME_MODS[self.mode])
            else:
                if not self.burst_fire:
                    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
                    time.sleep(TIME_MODS[self.mode])
                    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up
                else:
                    ctypes.windll.user32.mouse_event(8, 0, 0, 0, 0)  # left down
                    time.sleep(TIME_MODS[self.mode])
                    ctypes.windll.user32.mouse_event(10, 0, 0, 0, 0)  # left up
            print_banner(self)

    def set_gunmode(self, gunmode):
        self.gunmode_name = gunmode.name
        self.hold = gunmode.value["hold"]
        self.mode = gunmode.value["mode"]
        global GRABZONE
        GRABZONE = gunmode.value["grabzone"]
        # print("Gun mode set to:",self.gunmode_name)

def print_banner(bot: triggerBot):
    os.system("cls")
    print(Style.BRIGHT + Fore.CYAN + """
█▀▀█ █▀▀▄ █▀▀ █  █
█▄▄█ █  █ ▀▀█ █▀▀█
▀  ▀ ▀  ▀ ▀▀▀ ▀  ▀
v1.1.0
""" + Style.RESET_ALL)
    print("====== Controls ======")
    print("Activate Trigger Bot :", Fore.YELLOW + TRIGGER_KEY + Style.RESET_ALL)
    print("Switch fire mode     :", Fore.YELLOW + SWITCH_KEY + Style.RESET_ALL)
    print("Hold mode            :", Fore.YELLOW + HOLD_KEY + Style.RESET_ALL)
    print("Change Grabzone      :", Fore.YELLOW + GRABZONE_KEY_UP + "/" + GRABZONE_KEY_DOWN + Style.RESET_ALL)
    print("Change Color         :", Fore.YELLOW + COLOR_SWITCH_KEY + Style.RESET_ALL)
    print("Change gun mode      :", Fore.YELLOW + GUN_MODE_KEY_UP + Style.RESET_ALL)
    print("Toggle burst fire    :", Fore.YELLOW + BURST_FIRE_MODE_TOGGLE_KEY + Style.RESET_ALL)
    print("==== Information =====")
    print("Mode                 :", Fore.CYAN + mods[bot.mode] + Style.RESET_ALL)
    print("Hold                 :", (Fore.GREEN if bot.hold else Fore.RED) + str(bot.hold) + Style.RESET_ALL)
    print("Color                :", Fore.CYAN + list(Colors.keys())[list(Colors.values()).index(bot.color)] + Style.RESET_ALL)
    print("Gun Mode             :", Fore.CYAN + bot.gunmode_name + Style.RESET_ALL)
    print("Burst fire           :", (Fore.GREEN if bot.burst_fire else Fore.RED) + str(bot.burst_fire) + Style.RESET_ALL)
    print("Grabzone             :", Fore.CYAN + str(GRABZONE) + "x" + str(GRABZONE) + Style.RESET_ALL)
    print("Activated            :", (Fore.GREEN if bot.toggled else Fore.RED) + str(bot.toggled) + Style.RESET_ALL)
    print("Last reaction time   :", Fore.CYAN + str(bot.last_reac) + Style.RESET_ALL + " ms (" + str(
        (bot.last_reac) / (GRABZONE * GRABZONE)) + "ms/pix)")


if __name__ == "__main__":
    bot = triggerBot()
    print_banner(bot)
    while True:
        if keyboard.is_pressed(SWITCH_KEY):
            bot.switch()
            print_banner(bot)
            while keyboard.is_pressed(SWITCH_KEY):
                pass
        elif keyboard.is_pressed(GRABZONE_KEY_UP):
            GRABZONE += 5
            print_banner(bot)
            winsound.Beep(400, 200)
            while keyboard.is_pressed(GRABZONE_KEY_UP):
                pass
        elif keyboard.is_pressed(GRABZONE_KEY_DOWN):
            GRABZONE -= 5
            print_banner(bot)
            winsound.Beep(300, 200)
            while keyboard.is_pressed(GRABZONE_KEY_DOWN):
                pass
        elif keyboard.is_pressed(GUN_MODE_KEY_UP):
            bot.set_gunmode(next(gun_modes))
            print_banner(bot)
            winsound.Beep(400, 200)
            while keyboard.is_pressed(GUN_MODE_KEY_UP):
                pass
        # elif keyboard.is_pressed(GUN_MODE_KEY_DOWN):
        #     bot.set_gunmode(pre(gun_modes))
        #     print_banner(bot)
        #     winsound.Beep(400, 200)
        #     while keyboard.is_pressed(GUN_MODE_KEY_UP):
        #         pass
        elif keyboard.is_pressed(TRIGGER_KEY):
            bot.toggle()
            print_banner(bot)
            if bot.toggled:
                winsound.Beep(440, 75)
                winsound.Beep(700, 100)
            else:
                winsound.Beep(440, 75)
                winsound.Beep(200, 100)
            while keyboard.is_pressed(TRIGGER_KEY):
                pass

        elif keyboard.is_pressed(HOLD_KEY):
            bot.hold = not bot.hold
            print_banner(bot)

            while keyboard.is_pressed(HOLD_KEY):
                pass

        elif keyboard.is_pressed(COLOR_SWITCH_KEY):
            bot.switch_color()
            print_banner(bot)

            while keyboard.is_pressed(COLOR_SWITCH_KEY):
                pass

        elif keyboard.is_pressed(BURST_FIRE_MODE_TOGGLE_KEY):
            bot.burst_fire = not bot.burst_fire
            print_banner(bot)

            while keyboard.is_pressed(BURST_FIRE_MODE_TOGGLE_KEY):
                pass

        if bot.toggled:
            bot.scan()