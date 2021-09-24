import pygame
from pygame import mixer

# Chaeme Vogue

# Space Invaders

# Game Rules
# player wins if
#   - player kills all the enemies
# player loses if
#   - enemies collide with player
#   - enemies reach the bottom

# Instructions
# Press spacebar to shoot lasers at enemies
# use left and right keys to move the player

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("img/spaceship_64.png")
        self.rect = self.img.get_rect(topleft=(370, 580))
        self.x_change = 1.9

    # blit means draw
    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= self.x_change
        if key[pygame.K_RIGHT]:
            self.rect.x += self.x_change

        game.screen.blit(self.img, self.rect)

        # player boundaries
        if self.rect.x <= 0:
            self.rect.x = 0
        elif self.rect.x >= 736:
            self.rect.x = 736


# Enemy
# - given row and column for its position in the group
class Enemy(pygame.sprite.Sprite):
    def __init__(self, row, col):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("img/enemy_ufo_64.png")
        self.row = row
        self.col = col
        self.rect = self.img.get_rect(topleft=(row, col))
        self.timer = pygame.time.get_ticks()
        self.wait = 1300
        self.speed = 1
        self.move_left = True

    def update(self, start_time):
        game.screen.blit(self.img, self.rect)
        now = pygame.time.get_ticks()

        # if move left is true: rect.x -= 1
        # else: rect.x += 1
        if self.move_left == True:
            self.rect.x -= self.speed
        elif self.move_left == False:
            self.rect.x += self.speed

        # if wait time has passed, change enemies direction
        if now - self.timer >= self.wait:
            self.timer = now
            self.rect.y += 15
            if self.move_left == True:
                self.move_left = False
            elif self.move_left == False:
                self.move_left = True

        # enemy boundaries
        if self.rect.x <= 0:
            self.move_left = False
        elif self.rect.x >= 736:
            self.move_left = True

        if self.rect.y >= 600:
            game.enemies_before_kill()
            game.enemies_at_bottom = True

# Laser
# Ready State - cant see the laser on screen
# Fire State - laser is currently moving
# - given player's current position
class Laser(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("img/laser-beam.png")
        self.rect = self.img.get_rect(topleft=(x_pos - 2, y_pos - 21))
        self.x_change = 0
        self.y_change = 10
        self.timer = pygame.time.get_ticks()
        self.cooldown = 300

    def update(self):
        self.rect.y -= 1
        game.screen.blit(self.img, self.rect)
        now = pygame.time.get_ticks()

        if self.rect.y == 40:
            self.kill()


# Explosion
# - given current position of a collision between sprites
# - wait-time before explosion disappears
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, wait_time):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("img/explosion_64_1.png")
        self.rect = self.img.get_rect(topleft=(x_pos, y_pos))
        self.timer = pygame.time.get_ticks()
        self.wait_time = wait_time  # 250

    def update(self, start_time):
        game.screen.blit(self.img, self.rect)
        time_passed = start_time - self.timer

        now = pygame.time.get_ticks()
        if now - self.timer >= self.wait_time:
            self.kill()

        '''if time_passed > self.wait_time:
            self.kill()'''


class Game:
    def __init__(self):
        # Initialize the pygame
        pygame.init()
        self.width = 800
        self.height = 700

        # Create the screen
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Background
        self.background = pygame.image.load("img/starry-night-design-background.jpeg")

        # Background Sound
        mixer.music.load("sound/music_zapsplat_game_music_action_retro_8_bit_repeating_016.mp3")
        mixer.music.play(-1)

        # Title and Icon
        pygame.display.set_caption("Space Invaders")
        self.icon = pygame.image.load("img/rocket_64.png")
        pygame.display.set_icon(self.icon)

        # Clock
        self.clock = pygame.time.Clock()

        # Score
        self.score_value = 0
        self.score_font = pygame.font.Font('font/robot_crush_font/Robot Crush.otf', 32)

        # Play or Game Over?
        self.collided_w_player = False
        self.enemies_at_bottom = False
        self.play = True

        # Sprites
        self.player = Player()
        self.enemies_group = pygame.sprite.Group()
        self.lasers_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()

    def main(self):
        self.create_enemies()

        running = True
        while running:
            # RBG - Red, Green, Blue
            game.screen.fill((0, 0, 0))
            # Background Image
            game.screen.blit(self.background, (0, 0))

            if self.play:
                start_time = pygame.time.get_ticks()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    # if keystroke is pressed and its a spacebar
                    # player shoots a laser
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            laser_sound = mixer.Sound(
                                "sound/zapsplat_multimedia_game_sound_simple_retro_laser_shoot_002_73264.mp3")
                            laser_sound.play()
                            laser = Laser(self.player.rect.centerx, self.player.rect.y)
                            self.lasers_group.add(laser)

                # the game is over when all enemies are killed
                if len(self.enemies_group) == 0:
                    self.play = False

                self.enemies_group.update(start_time)
                self.lasers_group.update()
                self.explosions_group.update(start_time)
                self.detect_collision()

            # check if game over
            elif self.play == False:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    # if player wants to play again, they hit any key and the game resets
                    if event.type == pygame.KEYUP:
                        self.reset()
                if self.collided_w_player == True or self.enemies_at_bottom == True:
                    self.game_over_text(False)
                else:
                    self.game_over_text(True)

                # ask player if they want to play again
                self.display_play_again()

            self.show_score()
            self.player.update()
            pygame.display.update()

    def show_score(self):
        score = self.score_font.render("Score: " + str(self.score_value), True, (255, 255, 255))
        game.screen.blit(score, (15, 10))

    def game_over_text(self, outcome):
        outcome_msg = ''
        x = 0
        game_over_font = pygame.font.Font('font/robot_crush_font/Robot Crush.otf', 64)
        outcome_font = pygame.font.Font('font/robot_crush_font/Robot Crush.otf', 50)
        game_over_text = game_over_font.render("GAme Over", True, (255, 255, 255))

        if outcome == True:
            outcome_msg = "You Win"
            x = 320
        elif outcome == False:
            outcome_msg = "You Lose"
            x = 310

        outcome_text = outcome_font.render(outcome_msg, True, (255, 255, 255))
        game.screen.blit(game_over_text, (250, 250))
        game.screen.blit(outcome_text, (x, 350))

    # detect for collisions between sprites
    def detect_collision(self):
        # detect if enemy sprites collided with player lasers
        collisions = pygame.sprite.groupcollide(self.enemies_group, self.lasers_group, True, True)
        for collision in collisions:
            explosion = Explosion(collision.rect.x, collision.rect.y, 250)
            self.explosions_group.add(explosion)
            explosion_sound = mixer.Sound("sound/explosion.wav")
            explosion_sound.play()
            self.score_value += 1

        # player loses if enemies collide with the player
        player_collision = pygame.sprite.spritecollideany(self.player, self.enemies_group)
        if player_collision is not None:
            self.collided_w_player = True
            self.enemies_before_kill()

    # all enemies are killed if they collide with the player or reach the bottom
    # before all enemies are killed display explosion
    def enemies_before_kill(self):
        for enemy in self.enemies_group:
            explosion = Explosion(enemy.rect.x, enemy.rect.y, 250)
            self.explosions_group.add(explosion)
            explosion_sound = mixer.Sound("sound/explosion.wav")
            explosion_sound.play()
            enemy.kill()

    def display_play_again(self):
        play_again_font = pygame.font.Font('font/robot_crush_font/Robot Crush.otf', 25)
        play_again_text = play_again_font.render("Tap any key to play again!", True, (255, 255, 255))
        game.screen.blit(play_again_text, (260, 450))

    # if player wants tp play again:
    # reset game values,
    # create enemies,
    # kill any remaining laser or explosion sprites
    def reset(self):
        self.score_value = 0
        self.play = True
        self.collided_w_player = False
        self.enemies_at_bottom = False
        self.create_enemies()
        self.kill_group(self.lasers_group)
        self.kill_group(self.explosions_group)

    # create 6 x 7 enemies
    # then add them to sprite enemies_group
    def create_enemies(self):
        for i in range(6):
            for j in range(7):
                enemy = Enemy(i, j)
                enemy.rect.x = 164 + (i * 88)
                enemy.rect.y = 50 + (j * 63)
                self.enemies_group.add(enemy)

    # given a group of sprites, kill all sprites
    def kill_group(self, sprite_group):
        for sprite in sprite_group:
            sprite.kill()

if __name__ == '__main__':
    game = Game()
    game.main()
