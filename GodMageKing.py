import pygame as pg
from threading import Timer,Thread,Event
import time
import math


class Unit:
    NORTH=1
    SOUTH=2
    EAST=3
    WEST=4
    def __init__(self, team, sprite, code, id_num, pos, atr):
        self.commands = []
        self.atr = atr #dict of atributes
        self.team = team
        self.sprite = sprite
        self.code = code
        self.id_num = id_num
        self.casting = False
        self.time_to_cast = 0
        self.spell_to_cast = 0 #spell obj
        self.energy_per_tick = 0
        self.target = 0 #target for spell
        self.x = pos[0]
        self.y = pos[1]
        self.moving = False
        self.dir = 0
    def regen_energy(self):
        atr = self.atr
        if atr["food"]==0 or arr["water"]==0: #don't regen without food/water
            return
        if atr["energy"]<atr["max_energy"]:
            food_consumption_mult = 2 - (atr["energy"]/atr["max_energy"]) #1-2x food consumption linear
            water_consumption_mult = 3 - 2*(atr["energy"]/atr["max_energy"])#1-3x water consumption linear
            atr["food"]-=(atr["max_energy"]/200) * 2.5 * food_consumption_mult
            atr["water"]-=(atr["max_energy"]/200) * 1 * water_consumption_mult
            atr["energy"] += atr["max_energy"]/200
            if atr["energy"]>atr["max_energy"]:
                atr["energy"] = atr["max_energy"]
        else: #20% cost to maintain a unit at full energy
            atr["food"]-=(atr["max_energy"]/200) * 0.5
            atr["water"]-=(atr["max_energy"]/200) * 0.2
    def regen_hp(self):
        atr = self.atr
        if atr["food"]==0 or arr["water"]==0: #don't regen without food/water
            return
        if atr["damage"]==0: #don't regen without damage
            return
        atr["damage"]-=1-(atr["energy"]/atr["max_energy"]) #0-1% damage per tick, linear on energy/max
    def tick(self):
        regen_energy()
        regen_hp()
        if atr["food"]<0:atr["food"]=0
        if atr["water"]<0:atr["water"]=0
        
        if self.casting:
            self.atr["energy"]-=self.energy_per_tick
            if self.atr["energy"]<0:
                self.casting = False
                self.time_to_cast = -1
            return
        if self.time_to_cast==0:
            self.spell.cast(self.target)
        if self.moving:
            self.atr["energy"]-=self.energy_per_tick
            if self.atr["energy"]<0:
                self.moving = False
                self.time_to_move = -1
            return
        if self.time_to_move==0:
            if self.dir==Unit.NORTH:
                self.y-=1
            if self.dir==Unit.SOUTH:
                self.y+=1
            if self.dir==Unit.EAST:
                self.x+=1
            if self.dir==Unit.WEST:
                self.x-=1
        self.time_to_cast-=1
        self.time_to_move
        self.code()
    def move(self,direction, EPT):
        self.moving = True
        self.dir = direction
        self.energy_per_tick=EPT
        
        speed = math.sqrt(EPT)
        dist = 50 #change this
        
        self.time_to_move = math.floor(dist/speed)
    def cast(self,spell, target, EPT):
        self.casting = True
        self.spell_to_cast = spell
        self.energy_per_tick=EPT

        speed = math.sqrt(EPT)
        cost = spell.cost

        self.time_to_cast = math.floor(cost/speed)
    def render(self):
        board.blit(self.sprite,(self.x*12+1,self.y*12+1))

class Spell:
    SELF=1
    UNIT=2
    TILE=3
    def __init__(self, target_type, effects, cost):
        self.target_type = target_type
        self.effects = effects
        self.cost = cost
    def cast(self,target):
        for key in self.effects.keys():
            target.atr[key]+=self.effects[key]
        
def get_command_loop(next_commands, cur_command, past_commands):
    while 1:
        time.sleep(5)
        past_commands.append(cur_command[0])
        if len(next_commands)==0:
            cur_command[0]=""
        else:
            cur_command[0]=next_commands.pop(0)

def main():
    screen = pg.display.set_mode((1600, 900))
    font = pg.font.Font(None, 32)
    command_font = pg.font.Font(None, 18)
    clock = pg.time.Clock()
    input_box = pg.Rect(1400, 868, 200, 32)
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    next_commands = []
    cur_command = [""]
    past_commands = []
    
    command_loop = Thread(name="command_loop",target=get_command_loop,args=(next_commands, cur_command, past_commands))
    command_loop.start()

    board = pg.Surface((2000,2000))

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        next_commands.append(text)
                        text = ''
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((255, 255, 255))
        # Render the current text.
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pg.draw.rect(screen, color, input_box, 2)

        font_base_height=860
        for c in next_commands[::-1]:
            c_surface = command_font.render(c, True, pg.Color('Red'))
            font_base_height-=c_surface.get_height()+4
            screen.blit(c_surface,(1405, font_base_height+2))
        for c in cur_command:
            c_surface = command_font.render(c, True, pg.Color('seaGreen'))
            font_base_height-=c_surface.get_height()+4
            screen.blit(c_surface,(1405, font_base_height+2))
        for c in past_commands[::-1]:
            c_surface = command_font.render(c, True, pg.Color('Black'))
            font_base_height-=c_surface.get_height()+4
            screen.blit(c_surface,(1405, font_base_height+2))
            if font_base_height<0:
                break
        test_surface = pg.Surface((11,11))
        test_surface.fill(pg.Color('Red'))
        screen.blit(test_surface,(121,121))

        for x in range(101):
            pg.draw.line(screen,pg.Color('Black'),(12*x,0),(12*x,900))
        for y in range(100):
            pg.draw.line(screen,pg.Color('Black'),(0,12*y),(1200,12*y))
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
