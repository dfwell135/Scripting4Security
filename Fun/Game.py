import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 960, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Barrel Trouble")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 24)
BIG_FONT = pygame.font.SysFont("consolas", 52, bold=True)

# Colors
SKY = (25, 25, 45)
PLATFORM_COLOR = (210, 55, 65)
PLATFORM_EDGE = (255, 145, 65)
LADDER_COLOR = (80, 190, 220)
PLAYER_COLOR = (70, 150, 255)
PLAYER_DARK = (25, 65, 150)
BARREL_COLOR = (150, 80, 35)
BARREL_DARK = (75, 35, 20)
ENEMY_COLOR = (145, 75, 40)
WHITE = (245, 245, 245)
YELLOW = (255, 220, 70)

FPS = 60
GRAVITY = 0.55


class Platform:
    def __init__(self, x, y, width, slant=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = 16
        self.slant = slant
        self.rect = pygame.Rect(x, y, width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, PLATFORM_COLOR, self.rect)
        pygame.draw.line(
            surface,
            PLATFORM_EDGE,
            (self.rect.left, self.rect.top),
            (self.rect.right, self.rect.top),
            4,
        )


class Ladder:
    def __init__(self, x, top, bottom):
        self.x = x
        self.top = top
        self.bottom = bottom
        self.rect = pygame.Rect(x - 12, top, 24, bottom - top)

    def draw(self, surface):
        pygame.draw.line(
            surface, LADDER_COLOR, (self.x - 10, self.top), (self.x - 10, self.bottom), 4
        )
        pygame.draw.line(
            surface, LADDER_COLOR, (self.x + 10, self.top), (self.x + 10, self.bottom), 4
        )

        for y in range(self.top + 8, self.bottom, 14):
            pygame.draw.line(
                surface, LADDER_COLOR, (self.x - 10, y), (self.x + 10, y), 3
            )


class Player:
    def __init__(self):
        self.width = 28
        self.height = 42
        self.x = 80
        self.y = 540
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 4
        self.jump_power = -11
        self.on_ground = False
        self.climbing = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def reset(self):
        self.x = 80
        self.y = 540
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.climbing = False

    def update(self, keys, platforms, ladders):
        current_rect = self.rect

        near_ladder = None
        for ladder in ladders:
            if current_rect.inflate(16, 8).colliderect(ladder.rect):
                near_ladder = ladder
                break

        if near_ladder and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.climbing = True

        if self.climbing:
            self.velocity_x = 0

            if keys[pygame.K_UP]:
                self.y -= 3
            if keys[pygame.K_DOWN]:
                self.y += 3

            self.x = near_ladder.x - self.width // 2 if near_ladder else self.x

            if not near_ladder:
                self.climbing = False
            else:
                if self.y + self.height < near_ladder.top:
                    self.y = near_ladder.top - self.height
                    self.climbing = False
                elif self.y > near_ladder.bottom:
                    self.y = near_ladder.bottom
                    self.climbing = False

            return

        self.velocity_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        if (
            (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP])
            and self.on_ground
        ):
            self.velocity_y = self.jump_power
            self.on_ground = False

        self.x += self.velocity_x
        self.x = max(0, min(WIDTH - self.width, self.x))

        previous_bottom = self.y + self.height
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        self.on_ground = False

        for platform in platforms:
            if (
                self.velocity_y >= 0
                and previous_bottom <= platform.rect.top
                and self.rect.colliderect(platform.rect)
            ):
                self.y = platform.rect.top - self.height
                self.velocity_y = 0
                self.on_ground = True
                break

        if self.y > HEIGHT + 50:
            self.reset()

    def draw(self, surface):
        rect = self.rect

        pygame.draw.rect(surface, PLAYER_COLOR, rect, border_radius=5)
        pygame.draw.rect(
            surface,
            PLAYER_DARK,
            (rect.x + 5, rect.y + 7, rect.width - 10, 10),
            border_radius=3,
        )
        pygame.draw.circle(surface, WHITE, (rect.x + 9, rect.y + 11), 3)
        pygame.draw.circle(surface, WHITE, (rect.x + 19, rect.y + 11), 3)
        pygame.draw.rect(surface, PLAYER_DARK, (rect.x + 4, rect.bottom - 7, 8, 7))
        pygame.draw.rect(surface, PLAYER_DARK, (rect.right - 12, rect.bottom - 7, 8, 7))


class Barrel:
    def __init__(self, x, y, direction):
        self.radius = 13
        self.x = x
        self.y = y
        self.velocity_x = direction * 3
        self.velocity_y = 0

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, platforms):
        previous_bottom = self.y + self.radius

        self.velocity_y += GRAVITY
        self.x += self.velocity_x
        self.y += self.velocity_y

        if self.x < self.radius:
            self.x = self.radius
            self.velocity_x *= -1

        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.velocity_x *= -1

        for platform in platforms:
            if (
                self.velocity_y >= 0
                and previous_bottom <= platform.rect.top
                and self.rect.colliderect(platform.rect)
            ):
                self.y = platform.rect.top - self.radius
                self.velocity_y = 0
                break

    def draw(self, surface):
        pygame.draw.circle(surface, BARREL_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(
            surface, BARREL_DARK, (int(self.x), int(self.y)), self.radius, 3
        )
        pygame.draw.line(
            surface,
            BARREL_DARK,
            (int(self.x - 8), int(self.y - 8)),
            (int(self.x + 8), int(self.y + 8)),
            3,
        )
        pygame.draw.line(
            surface,
            BARREL_DARK,
            (int(self.x + 8), int(self.y - 8)),
            (int(self.x - 8), int(self.y + 8)),
            3,
        )


def create_level():
    platforms = [
        Platform(0, 590, 960),
        Platform(0, 475, 800),
        Platform(160, 360, 800),
        Platform(0, 245, 800),
        Platform(160, 130, 800),
    ]

    ladders = [
        Ladder(720, 475, 590),
        Ladder(250, 360, 475),
        Ladder(650, 245, 360),
        Ladder(300, 130, 245),
    ]

    return platforms, ladders


def draw_enemy(surface):
    x, y = 75, 75

    pygame.draw.circle(surface, ENEMY_COLOR, (x, y), 38)
    pygame.draw.circle(surface, (95, 45, 25), (x - 15, y - 6), 7)
    pygame.draw.circle(surface, (95, 45, 25), (x + 15, y - 6), 7)
    pygame.draw.arc(surface, BARREL_DARK, (x - 23, y - 2, 46, 30), 0, 3.14, 4)

    pygame.draw.rect(surface, ENEMY_COLOR, (x - 45, y + 30, 90, 35), border_radius=10)
    pygame.draw.line(surface, ENEMY_COLOR, (x - 35, y + 45), (x - 75, y + 70), 14)
    pygame.draw.line(surface, ENEMY_COLOR, (x + 35, y + 45), (x + 75, y + 70), 14)


def draw_background(surface):
    surface.fill(SKY)

    for x in range(0, WIDTH, 80):
        pygame.draw.line(surface, (35, 35, 65), (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, 80):
        pygame.draw.line(surface, (35, 35, 65), (0, y), (WIDTH, y), 1)


def main():
    platforms, ladders = create_level()
    player = Player()
    barrels = []

    score = 0
    lives = 3
    game_over = False
    won = False
    barrel_timer = 0

    running = True

    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_r and (game_over or won):
                    platforms, ladders = create_level()
                    player.reset()
                    barrels.clear()
                    score = 0
                    lives = 3
                    game_over = False
                    won = False

        if not game_over and not won:
            keys = pygame.key.get_pressed()

            player.update(keys, platforms, ladders)

            barrel_timer += 1
            if barrel_timer >= 120:
                barrel_timer = 0
                barrels.append(Barrel(125, 105, 1))

            for barrel in barrels[:]:
                barrel.update(platforms)

                if barrel.y > HEIGHT + 50:
                    barrels.remove(barrel)
                    score += 100
                    continue

                if barrel.rect.colliderect(player.rect):
                    barrels.remove(barrel)
                    lives -= 1
                    player.reset()

                    if lives <= 0:
                        game_over = True

            goal = pygame.Rect(820, 82, 80, 48)
            if player.rect.colliderect(goal):
                won = True
                score += 1000

        draw_background(SCREEN)

        for ladder in ladders:
            ladder.draw(SCREEN)

        for platform in platforms:
            platform.draw(SCREEN)

        draw_enemy(SCREEN)

        pygame.draw.rect(SCREEN, YELLOW, (820, 82, 80, 48), border_radius=6)
        pygame.draw.rect(SCREEN, (120, 80, 20), (820, 82, 80, 48), 3)
        pygame.draw.circle(SCREEN, (80, 170, 80), (860, 105), 12)

        for barrel in barrels:
            barrel.draw(SCREEN)

        player.draw(SCREEN)

        score_text = FONT.render(f"SCORE: {score}", True, WHITE)
        lives_text = FONT.render(f"LIVES: {lives}", True, WHITE)
        help_text = FONT.render("ARROWS/WASD: Move   SPACE: Jump", True, WHITE)

        SCREEN.blit(score_text, (20, 15))
        SCREEN.blit(lives_text, (WIDTH - 130, 15))
        SCREEN.blit(help_text, (275, HEIGHT - 35))

        if game_over:
            message = BIG_FONT.render("GAME OVER", True, (255, 80, 80))
            restart = FONT.render("Press R to restart or ESC to quit", True, WHITE)
            SCREEN.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            SCREEN.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35)))

        if won:
            message = BIG_FONT.render("YOU WIN!", True, YELLOW)
            restart = FONT.render("Press R to play again or ESC to quit", True, WHITE)
            SCREEN.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            SCREEN.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()