import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
GROUND_Y = 500
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Clash")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 28, bold=True)
large_font = pygame.font.SysFont("Arial", 64, bold=True)


class Fighter:
    def __init__(self, x, color, name, controls, facing):
        self.rect = pygame.Rect(x, GROUND_Y - 120, 70, 120)
        self.color = color
        self.name = name
        self.controls = controls
        self.facing = facing
        self.health = 100
        self.speed = 5
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.has_hit = False

    def move(self, keys, opponent):
        dx = 0

        if keys[self.controls["left"]]:
            dx -= self.speed
            self.facing = -1

        if keys[self.controls["right"]]:
            dx += self.speed
            self.facing = 1

        new_rect = self.rect.move(dx, 0)

        if new_rect.left >= 0 and new_rect.right <= WIDTH:
            self.rect = new_rect

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attack_timer > 0:
            self.attack_timer -= 1

    def attack(self, opponent):
        if self.attack_cooldown > 0 or self.health <= 0:
            return

        self.attack_timer = 12
        self.attack_cooldown = 30
        self.has_hit = False

        attack_box = self.rect.copy()
        attack_box.width = 65

        if self.facing == 1:
            attack_box.left = self.rect.right
        else:
            attack_box.right = self.rect.left

        if attack_box.colliderect(opponent.rect) and not self.has_hit:
            opponent.health = max(0, opponent.health - 10)
            self.has_hit = True

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)

        # Head
        pygame.draw.circle(
            screen,
            (255, 210, 170),
            (self.rect.centerx, self.rect.top - 15),
            22,
        )

        # Attack effect
        if self.attack_timer > 0:
            attack_box = self.rect.copy()
            attack_box.width = 65

            if self.facing == 1:
                attack_box.left = self.rect.right
            else:
                attack_box.right = self.rect.left

            pygame.draw.rect(screen, (255, 230, 80), attack_box, border_radius=8)


def draw_health_bar(x, y, health, color, name, reverse=False):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, 350, 30))

    health_width = int(350 * health / 100)

    if reverse:
        pygame.draw.rect(
            screen,
            color,
            (x + 350 - health_width, y, health_width, 30),
        )
    else:
        pygame.draw.rect(screen, color, (x, y, health_width, 30))

    label = font.render(f"{name}: {health}", True, "white")
    screen.blit(label, (x, y - 35))


def reset_game():
    player = Fighter(
        180,
        (50, 130, 255),
        "PLAYER",
        {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "attack": pygame.K_f,
        },
        1,
    )

    enemy = Fighter(
        750,
        (220, 60, 70),
        "CPU",
        {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "attack": pygame.K_RCTRL,
        },
        -1,
    )

    return player, enemy


player, enemy = reset_game()
game_over = False

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == player.controls["attack"] and not game_over:
                player.attack(enemy)

            if event.key == pygame.K_r and game_over:
                player, enemy = reset_game()
                game_over = False

    keys = pygame.key.get_pressed()

    if not game_over:
        player.move(keys, enemy)

        # Simple CPU behavior
        distance = player.rect.centerx - enemy.rect.centerx

        if abs(distance) > 100:
            if distance > 0:
                enemy.rect.x += enemy.speed
                enemy.facing = 1
            else:
                enemy.rect.x -= enemy.speed
                enemy.facing = -1

        if abs(distance) < 120 and enemy.attack_cooldown == 0:
            enemy.attack(player)

        enemy.rect.x = max(0, min(WIDTH - enemy.rect.width, enemy.rect.x))

        if player.health <= 0 or enemy.health <= 0:
            game_over = True

    # Background
    screen.fill((25, 30, 60))

    # Arena
    pygame.draw.rect(screen, (70, 160, 90), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(screen, "white", (0, GROUND_Y), (WIDTH, GROUND_Y), 4)

    draw_health_bar(40, 55, player.health, (40, 120, 255), "PLAYER")
    draw_health_bar(610, 55, enemy.health, (220, 50, 70), "CPU", reverse=True)

    player.draw()
    enemy.draw()

    controls = font.render(
        "Player: A/D move | F attack | R restart after defeat",
        True,
        "white",
    )
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 40))

    if game_over:
        winner = "PLAYER WINS!" if enemy.health <= 0 else "CPU WINS!"
        message = large_font.render(winner, True, (255, 230, 80))
        restart = font.render("Press R to restart", True, "white")

        screen.blit(
            message,
            (WIDTH // 2 - message.get_width() // 2, 220),
        )
        screen.blit(
            restart,
            (WIDTH // 2 - restart.get_width() // 2, 300),
        )

    pygame.display.flip()