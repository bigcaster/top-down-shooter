import pygame
import sys
import math

pygame.init()
size = WIDTH, HEIGHT = 1536, 864
pygame.display.set_caption("top_down_sh00ter_2d")
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
hero_sprite = pygame.sprite.Group()
wall_sprites = pygame.sprite.Group()
cursor_sprite = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def blitRotate(image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    screen.blit(rotated_image, rotated_image_rect)


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, hero_sprite)
        self.orig_image = pygame.image.load("red_square.png")
        self.image = pygame.Surface((0, 0))
        self.rect = pygame.Rect(x, y, 42, 42)
        self.v = 8
        self.vx = self.vy = 0
        self.moving_left = self.moving_right = self.moving_up = self.moving_down = False
        self.has_deltas = False
        self.delta_x = self.delta_y = None
        self.zoom_k = 10

    def update(self):
        self.vx = self.vy = 0
        if self.moving_left:
            self.vx = -self.v
        elif self.moving_right:
            self.vx = self.v
        if self.moving_up:
            self.vy = -self.v
        elif self.moving_down:
            self.vy = self.v
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, wall_sprites):
            self.rect = self.rect.move(-self.vx, 0)
            if not pygame.sprite.spritecollideany(self, wall_sprites):
                pass
            else:
                self.rect = self.rect.move(self.vx, -self.vy)
                if not pygame.sprite.spritecollideany(self, wall_sprites):
                    pass
                else:
                    self.rect = self.rect.move(-self.vx, 0)
        cursor_x, cursor_y = cursor.rect.x, cursor.rect.y
        self.delta_x, self.delta_y = cursor_x - self.rect.x, cursor_y - self.rect.y
        corner_sin = self.delta_y / (self.delta_x ** 2 + self.delta_y ** 2) ** 0.5
        self.has_deltas = True

        if self.delta_x <= 0:
            angle = math.asin(corner_sin) * 180 / 3.14 + 90
        else:
            angle = -math.asin(corner_sin) * 180 / 3.14 - 90
        blitRotate(self.orig_image, self.rect.center, (20, 20), angle)

    def check_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
            elif event.key == pygame.K_d:
                self.moving_right = True
            elif event.key == pygame.K_w:
                self.moving_up = True
            elif event.key == pygame.K_s:
                self.moving_down = True
            elif event.key == pygame.K_LSHIFT:
                self.zoom_k = 3
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            elif event.key == pygame.K_d:
                self.moving_right = False
            elif event.key == pygame.K_w:
                self.moving_up = False
            elif event.key == pygame.K_s:
                self.moving_down = False
            elif event.key == pygame.K_LSHIFT:
                self.zoom_k = 10
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                Bullet(*self.rect.center)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__(all_sprites, wall_sprites)
        self.image = pygame.Surface((w, h))
        self.image.fill((255, 128, 0))
        self.rect = self.image.get_rect().move(x, y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, bullet_sprites)
        self.orig_image = pygame.image.load("bullet.png")
        self.image = pygame.Surface((0, 0))
        self.rect = pygame.Rect(x, y, 11, 11)
        self.v = 15
        cursor_x, cursor_y = cursor.rect.x, cursor.rect.y
        self.delta_x, self.delta_y = cursor_x - self.rect.x, cursor_y - self.rect.y
        corner_sin = self.delta_y / (self.delta_x ** 2 + self.delta_y ** 2) ** 0.5
        if self.delta_x <= 0:
            self.angle = math.asin(corner_sin) * 180 / 3.14 + 90
        else:
            self.angle = -math.asin(corner_sin) * 180 / 3.14 - 90

    def update(self):
        k = abs(self.delta_x / self.delta_y)
        k2 = 1 + k
        k3 = self.v / k2
        k4 = k3 * k
        k5 = 1 if self.delta_x > 0 else -1
        k6 = 1 if self.delta_y > 0 else -1
        self.rect = self.rect.move(k4 * k5, k3 * k6)
        blitRotate(self.orig_image, self.rect.center, (5, 2), self.angle)
        if pygame.sprite.spritecollideany(self, wall_sprites):
            bullet_sprites.remove(self)
            all_sprites.remove(self)


class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, cursor_sprite)
        self.frames = []
        self.cur_frame = 0
        self.cut_sheet()
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(WIDTH // 2, HEIGHT // 2)
        self.n = 0

    def update(self):
        self.n += 40 / FPS
        if self.n >= 1:
            self.cur_frame = (self.cur_frame + 1) % 13
            self.image = self.frames[int(self.cur_frame)]
            self.n = 0
        x, y = pygame.mouse.get_pos()
        self.rect.x, self.rect.y = x, y

    def cut_sheet(self):
        sheet = pygame.image.load("cursor_sheet.png")
        sheet = pygame.transform.scale(sheet, (338, 26))
        for i in range(13):
            frame_location = (26 * i, 0, 26, 26)
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location)))


class Camera:
    def __init__(self):
        pass

    def update(self):
        x, y = WIDTH // 2, HEIGHT // 2
        delta_x, delta_y = 0, 0
        if hero.has_deltas:
            delta_x, delta_y = hero.delta_x, hero.delta_y
        x_changed, y_changed = x - delta_x // hero.zoom_k - hero.rect.x, y - delta_y // hero.zoom_k - hero.rect.y
        hero.rect.x, hero.rect.y = x - delta_x // hero.zoom_k, y - delta_y // hero.zoom_k
        for spite in all_sprites:
            if spite != hero:
                spite.rect.x, spite.rect.y = spite.rect.x + x_changed, spite.rect.y + y_changed


hero = Hero(450, 50)
cursor = Cursor()
camera = Camera()
wall_1 = Wall(400, 0, 400, 10)
wall_2 = Wall(790, 10, 10, 150)
wall_3 = Wall(530, 160, 570, 10)
wall_4 = Wall(1090, 170, 10, 1200)
wall_5 = Wall(0, 1370, 1100, 10)
wall_6 = Wall(0, 160, 10, 1210)
wall_7 = Wall(10, 160, 400, 10)
wall_8 = Wall(400, 10, 10, 150)

wall_9 = Wall(400, 650, 210, 10)
wall_10 = Wall(600, 660, 10, 200)
wall_11 = Wall(400, 850, 200, 10)
wall_12 = Wall(400, 660, 10, 200)

wall_13 = Wall(600, 160, 10, 130)
wall_14 = Wall(600, 500, 10, 150)
wall_15 = Wall(610, 575, 190, 10)
wall_16 = Wall(940, 575, 150, 10)
wall_17 = Wall(800, 850, 290, 10)
wall_18 = Wall(400, 860, 10, 70)
wall_19 = Wall(400, 1170, 10, 200)
wall_20 = Wall(10, 420, 60, 10)
wall_21 = Wall(160, 420, 90, 10)
wall_22 = Wall(240, 170, 10, 250)

FPS = 90
time = pygame.time.Clock()
pygame.mouse.set_visible(False)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        hero.check_event(event)
    screen.fill((160, 160, 200))
    camera.update()
    all_sprites.update()
    all_sprites.draw(screen)
    time.tick(FPS)
    pygame.display.flip()
