import pygame
import math

pygame.init()

# ------------------------ PLAYER CLASS ------------------------
class Player:
    def __init__(self, name, color="white"):
        self.name = name
        self.color = color  # white=alive, red=eliminated, green=winner
        self.money = 0
        self.alive = True

# ------------------------ ACTION PANEL ------------------------
class ActionPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.total_money = 0
        self.shared_draw_count = 0

    def draw(self, screen, font):
        pygame.draw.rect(screen, (180, 180, 180), self.rect)
        pygame.draw.rect(screen, (0,0,0), self.rect,2)
        screen.blit(font.render(f"Total Money: {self.total_money}", True, (0, 0, 0)), (self.rect.x + 10, self.rect.y + 20))
        screen.blit(font.render(f"Draw Count: {self.shared_draw_count}", True, (0, 0, 0)), (self.rect.x + 10, self.rect.y + 50))

# ------------------------ PLAYER POSITIONS ------------------------
def get_player_positions(center_x, center_y, radius, num_players):
    positions = []
    angle_step = 360 / num_players
    for i in range(num_players):
        angle_rad = math.radians(angle_step * i)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        positions.append((x, y))
    return positions

def draw_players(screen, players, positions):
    font = pygame.font.SysFont(None,24)
    for player, pos in zip(players, positions):
        color_map = {"white": (255, 255, 255), "red": (255, 0, 0), "green": (0, 255, 0)}
        pygame.draw.circle(screen, color_map[player.color], (int(pos[0]), int(pos[1])), 40)
        pygame.draw.circle(screen, (0, 0, 0), (int(pos[0]), int(pos[1])), 40, 2)
        # 名稱與金額靠近圓心
        screen.blit(font.render(player.name, True, (0, 0, 0)), (pos[0]-20, pos[1]-25))
        screen.blit(font.render(f"${player.money}", True, (0, 0, 0)), (pos[0]-20, pos[1]+10))

# ------------------------ SETTINGS SCREEN ------------------------
def settings_screen(screen):
    num_players = 2
    num_cards = 2
    running = True
    font = pygame.font.SysFont(None, 40)

    while running:
        screen.fill((50, 50, 50))
        screen.blit(font.render("Game Settings", True, (255, 255, 255)), (550, 50))
        screen.blit(font.render(f"Players: {num_players}", True, (255, 255, 255)), (580, 150))
        screen.blit(font.render(f"Cards: {num_cards}", True, (255, 255, 255)), (580, 250))
        screen.blit(font.render("Up/Down: players, Left/Right: cards", True, (200, 200, 200)), (400, 350))
        screen.blit(font.render("Enter to start", True, (200, 200, 200)), (550, 400))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and num_players < 8:
                    num_players += 1
                    if num_cards < num_players:
                        num_cards = num_players
                elif event.key == pygame.K_DOWN and num_players > 2:
                    num_players -= 1
                    if num_cards < num_players:
                        num_cards = num_players
                elif event.key == pygame.K_RIGHT and num_cards < 30:
                    num_cards += 1
                    if num_cards < num_players:
                        num_cards = num_players
                elif event.key == pygame.K_LEFT and num_cards > num_players:
                    num_cards -= 1
                elif event.key == pygame.K_RETURN:
                    running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    return num_players, num_cards

# ------------------------ MAIN ------------------------
screen_width = 1400
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Card Game Prototype")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --- Settings ---
num_players, num_cards = settings_screen(screen)
if num_players is None:
    pygame.quit()
    exit()

players = [Player(f"P{i+1}") for i in range(num_players)]
# 調整操作區在畫面中央
action_panel = ActionPanel(screen_width//2 - 150, screen_height//2 - 75, 300, 150)

running = True
while running:
    screen.fill((50, 50, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw UI
    action_panel.draw(screen, font)
    positions = get_player_positions(screen_width//2, screen_height//2, 300, num_players)
    draw_players(screen, players, positions)

    pygame.display.flip()
    clock.tick(60)
