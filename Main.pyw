import pygame
# import socket
import random
import math
import time

title = '광물캐기'
version = '0.4_alpha'

pygame.init()

class state:
    title = 'State.title'

    lobby = 'State.lobby'

    store = 'State.store'
    friend = 'State.friend'
    casino = 'State.casino'
    setting = 'State.setting'

class game:
    class display:
        width = 1280
        height = 720

        fps = 144
        display_fps = fps

        pygame.display.set_caption(f'{title} {version}')
    window = pygame.display.set_mode((display.width, display.height))

    exit = False

    # clock = pygame.time.Clock()

    state = None

class keyboard:
    lalt = False
    ralt = False

class cursor:
    position = pygame.mouse.get_pos()

    ppressed = pressed = pygame.mouse.get_pressed()
    fpressed = list(pressed)
    epressed = list(pressed)

    rel = pygame.mouse.get_rel()

class color:
    background = (222, 222, 222)
    text = (31, 33, 37)
    text2 = (134, 142, 148)
    gray = (88, 88, 90)

objects = []

def add_object(_obj):
    objects.append(_obj)

def delete_objects_by_type(object_type):
    count = 0

    indexes = []

    for obj in objects:
        if type(obj) == object_type:
            # obj.destroy()
            indexes.append(objects.index(obj))

    offset = 0
    for i in range(len(indexes)):
        del objects[indexes[i] - offset]
        offset += 1

    return count

class GameObject:
    def tick(self):
        pass

    def render(self):
        pass

    def destroy(self):
        objects.remove(self)

class Particle(GameObject):
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.color = colour

        self.size = random.randint(1, 5)

        self.vel_x = random.random() * 10 - 5
        self.vel_y = random.random() * 10 - 6

        self.gravity = 30 / game.display.display_fps

    def tick(self):
        self.x += self.vel_x
        self.y += self.vel_y

        self.vel_y += self.gravity

        if game.display.height <= self.y:
            self.destroy()

    def render(self):
        pygame.draw.rect(game.window, self.color, ((self.x, self.y), (self.size,) * 2))

class TextFormat:
    def __init__(self, font, size, color):
        self.font = font
        self.size = size
        self.color = color

        self.font = pygame.font.Font(font, size)

    def render(self, text):
        return self.font.render(text, True, self.color)

def center(x, y):
    return (x - y) / 2

class Text(GameObject):
    def __init__(self, x, y, text, text_format, move=None):
        self.x = x
        self.y = y

        self.text = text
        self.text_format = text_format

        self.surface = self.text_format.render(self.text)

        if self.x is None:
            self.x = center(game.display.width, self.surface.get_width())
        if self.y is None:
            self.y = center(game.display.height, self.surface.get_height())

        self.move_x = False
        self.move_y = False
        if move is not None:
            self.target_x = self.x + move[0]
            self.target_y = self.y + move[1]
            self.move_x = True
            self.move_y = True

    def tick(self):
        if self.move_x:
            self.x += (self.target_x - self.x) / (game.display.display_fps / 10)
            if math.fabs(self.target_x - self.x) - 0.1 < 0:
                self.move_x = False

        if self.move_y:
            self.y += (self.target_y - self.y) / (game.display.display_fps / 10)
            if math.fabs(self.target_y - self.y) - 0.1 < 0:
                self.move_y = False

    def render(self):
        game.window.blit(self.surface, (self.x, self.y))

class ButtonFrame(GameObject):
    def __init__(self, x, y, w, h, command, *args):
        self.x = x
        self.y = y

        self.width = w
        self.height = h

        self.command = command
        self.args = args

    def tick(self):
        if cursor.fpressed[0]:
            if self.x <= cursor.position[0] <= self.x + self.width:
                if self.y <= cursor.position[1] <= self.y + self.height:
                    self.command(*self.args)

class Cursor(GameObject):
    def __init__(self, pickaxe, images_count):
        self.pickaxe = pickaxe
        self.images_count = images_count

        self.surface = pygame.image.load(f'./src/image/pickaxe/{self.pickaxe}.png').convert_alpha()

        self.center_x = 0
        self.center_y = 0

        # self.x = 0
        # self.y = 0

        self.positions = []

        pygame.mouse.set_visible(False)

    def tick(self):
        self.positions = []
        for i in range(self.images_count):
            self.positions.append([cursor.position[0] - cursor.rel[0] * 2 * (i / self.images_count), cursor.position[1] - cursor.rel[1] * 2 * (i / self.images_count)])

    def render(self):
        # game.window.blit(self.surface, (self.x, self.y))

        for position in self.positions:
            game.window.blit(self.surface, position)

    def destroy(self):
        super().destroy()
        pygame.mouse.set_visible(True)

class Rect(GameObject):
    def __init__(self, x, y, w, h, colour, move=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        self.move = move
        self.move_x = False
        self.move_y = False
        if self.move is not None:
            self.target_x = self.x + self.move[0]
            self.target_y = self.y + self.move[1]

            self.move_x = True
            self.move_y = True

        self.color = colour

    def render(self):
        pygame.draw.rect(game.window, self.color, ((self.x, self.y), (self.width, self.height)))

class Stone(GameObject):
    def __init__(self, kinds, offset):
        self.kinds = kinds
        self.offset = offset

        self.surface = pygame.image.load(f'./src/image/stone/{kinds}.png').convert_alpha()

        self.x = center(game.display.width, self.surface.get_width())
        self.y = center(game.display.height, self.surface.get_height()) - 50

    def render(self):
        game.window.blit(self.surface, (self.x, self.y))

class HUD(GameObject):
    text_format: TextFormat

    objects_count_surface: pygame.Surface
    state_surface: pygame.Surface
    position_surface: pygame.Surface
    fps_surface: pygame.Surface

    def tick(self):
        self.text_format = TextFormat('./src/font/H2PORM.TTF', 10, color.text)

        self.objects_count_surface = self.text_format.render(str(len(objects)) + 'OBJS')
        self.state_surface = self.text_format.render(game.state + ' STTE')
        self.position_surface = self.text_format.render(f'{cursor.position} CRSR')
        self.fps_surface = self.text_format.render(f'{game.display.display_fps} FRPS')

    def render(self):
        game.window.blit(self.objects_count_surface, (game.display.width - self.objects_count_surface.get_width(), game.display.height - self.objects_count_surface.get_height()))
        game.window.blit(self.state_surface, (game.display.width - self.state_surface.get_width(), game.display.height - self.objects_count_surface.get_height() - self.state_surface.get_height()))
        game.window.blit(self.position_surface, (game.display.width - self.position_surface.get_width(), game.display.height - self.objects_count_surface.get_height() - self.state_surface.get_height() - self.position_surface.get_height()))
        game.window.blit(self.fps_surface, (game.display.width - self.fps_surface.get_width(), game.display.height - self.objects_count_surface.get_height() - self.state_surface.get_height() - self.position_surface.get_height() - self.fps_surface.get_height()))
hud = HUD()

def tick():
    for i in range(3):
        cursor.fpressed[i] = not cursor.ppressed[i] and cursor.pressed[i]
        cursor.epressed[i] = cursor.ppressed[i] and not cursor.pressed[i]

    if cursor.fpressed[0]:
        for i in range(16):
            add_object(Particle(*cursor.position, color.text))

    hud.tick()

def render():
    hud.render()

title_format = TextFormat('./src/font/H2PORL.TTF', 144, color.text)
common_text_format = TextFormat('./src/font/H2PORL.TTF', 32, color.text)
white_button_text_format = TextFormat('./src/font/H2PORM.TTF', 48, color.text2)

def change_state(next_state):
    if next_state == state.title:
        add_object(Text(None, 0, title, title_format, (0, center(game.display.height, 144))))
        add_object(Text(None, game.display.height, '아무곳이나 클릭해서 계속하기', common_text_format, (0, -200)))

        add_object(ButtonFrame(0, 0, game.display.width, game.display.height, change_state, state.lobby))

    elif next_state == state.lobby:
        delete_objects_by_type(Text)
        delete_objects_by_type(ButtonFrame)

        add_object(Stone('blue', 2))  # 테스트 코드

        add_object(Rect(0, game.display.height - 100, game.display.width, 100, color.gray))

        tmp = Text(0, game.display.height - 74, '상점', white_button_text_format)
        tmp.x = center(game.display.width / 4, tmp.surface.get_width())
        add_object(tmp)
        add_object(ButtonFrame(tmp.x, tmp.y, tmp.surface.get_width(), tmp.surface.get_height(), change_state, state.store))

        tmp = Text(0, game.display.height - 74, '친구', white_button_text_format)
        tmp.x = center(game.display.width / 4, tmp.surface.get_width()) + game.display.width / 4 * 1
        add_object(tmp)
        add_object(ButtonFrame(tmp.x, tmp.y, tmp.surface.get_width(), tmp.surface.get_height(), change_state, state.friend))

        tmp = Text(0, game.display.height - 74, '도박', white_button_text_format)
        tmp.x = center(game.display.width / 4, tmp.surface.get_width()) + game.display.width / 4 * 2
        add_object(tmp)
        add_object(ButtonFrame(tmp.x, tmp.y, tmp.surface.get_width(), tmp.surface.get_height(), change_state, state.casino))

        tmp = Text(0, game.display.height - 74, '설정', white_button_text_format)
        tmp.x = center(game.display.width / 4, tmp.surface.get_width()) + game.display.width / 4 * 3
        add_object(tmp)
        add_object(ButtonFrame(tmp.x, tmp.y, tmp.surface.get_width(), tmp.surface.get_height(), change_state, state.setting))

        add_object(Cursor('wooden_pickaxe', 3))

    elif next_state == state.store:
        delete_objects_by_type(Text)
        delete_objects_by_type(ButtonFrame)
        delete_objects_by_type(Rect)

    elif next_state == state.friend:
        delete_objects_by_type(Text)
        delete_objects_by_type(ButtonFrame)
        delete_objects_by_type(Rect)

    elif next_state == state.casino:
        delete_objects_by_type(Text)
        delete_objects_by_type(ButtonFrame)
        delete_objects_by_type(Rect)

    elif next_state == state.setting:
        delete_objects_by_type(Text)
        delete_objects_by_type(ButtonFrame)
        delete_objects_by_type(Rect)

    game.state = next_state

change_state(state.title)

delta = 0
delta2 = 0
delta2_loops = 0
time_per_loop = 1 / game.display.fps
now = time.time()

while not game.exit:
    pnow = now
    now = time.time()

    delta2 += now - pnow
    if delta2 >= 1:
        delta2 -= 1
        game.display.display_fps = delta2_loops
        delta2_loops = 0

    if delta >= 1:
        delta -= 1
        delta2_loops += 1
        cursor.ppressed = cursor.pressed
        cursor.pressed = pygame.mouse.get_pressed()
        cursor.position = pygame.mouse.get_pos()
        cursor.rel = pygame.mouse.get_rel()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LALT:
                    keyboard.lalt = True
                elif event.key == pygame.K_RALT:
                    keyboard.ralt = True
                elif event.key == pygame.K_F4:
                    if keyboard.lalt or keyboard.ralt:
                        game.exit = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LALT:
                    keyboard.lalt = False
                elif event.key == pygame.K_RALT:
                    keyboard.ralt = False

        tick()
        for obj in objects:
            obj.tick()

        game.window.fill(color.background)
        for obj in objects:
            obj.render()
        render()
        pygame.display.flip()
    else:
        try:
            delta += (now - pnow) / time_per_loop
        except ZeroDivisionError:
            pass

    # game.clock.tick(game.display.fps)
pygame.quit()
