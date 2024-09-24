import Game
import Menu
from time import sleep

def OpenScene(sceneName):
    sleep(0.25)  # หยุดเวลา 0.25 วินาที
    if sceneName == 'Menu':
        Menu.Menu()  # เรียกฟังก์ชัน Menu จากโมดูล Menu
    elif sceneName == 'Game':
        Game.Game()  # เรียกฟังก์ชัน Game จากโมดูล Game
