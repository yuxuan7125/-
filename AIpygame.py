import pygame
import math
import random
import sys

pygame.init()

# -------------------------
# Screen Setup
# -------------------------
WIDTH, HEIGHT = 1540, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pool Cards Game - Fused Version")
FONT = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

MAX_CARDS = 30
CARD_WIDTH = 150
CARD_HEIGHT = 50
SPACING = 15
MAX_COLS = 6

# -------------------------
# Game Globals
# -------------------------
pool_cards = []
players = []
total_money = 0
forced_draws = 0
current_bet = 0
round_number = 1  # 新增回合數顯示

# -------------------------
# Input Screen
# -------------------------
def input_screen():
    player_count = 4
    total_cards = 10
    while True:
        screen.fill((30,30,40))
        screen.blit(FONT.render(f"Players (2-8): {player_count}", True, (255,255,255)), (100,200))
        screen.blit(FONT.render(f"Total Cards (≥players, ≤30): {total_cards}", True, (255,255,255)), (100,230))
        screen.blit(FONT.render("UP/DOWN: players | LEFT/RIGHT: total cards | ENTER: start", True, (200,200,200)), (100,260))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_count = min(8, player_count+1)
                    total_cards = max(total_cards, player_count)
                if event.key == pygame.K_DOWN:
                    player_count = max(2, player_count-1)
                    total_cards = max(total_cards, player_count)
                if event.key == pygame.K_RIGHT:
                    total_cards = min(MAX_CARDS, total_cards+1)
                if event.key == pygame.K_LEFT:
                    total_cards = max(player_count, total_cards-1)
                if event.key == pygame.K_RETURN:
                    return player_count, total_cards

# -------------------------
# Player Class
# -------------------------
class Player:
    def __init__(self, idx):
        self.idx = idx
        self.pos = (0,0)
        self.money = 0
        self.alive = True
        self.color = (255,255,255)  # 白色=活著, 紅色=淘汰, 綠色=勝利

# -------------------------
# Pool Card Class
# -------------------------
class PoolCard:
    def __init__(self, type, rect, number):
        self.type = type  # WIN / DEAD / SAFE
        self.rect = rect
        self.number = number
        self.used = False
        self.revealed = False

# -------------------------
# Game Screen
# -------------------------
def game_screen(player_count, total_cards):
    global pool_cards, players, total_money, forced_draws, current_bet, round_number

    def setup_game():
        global pool_cards, total_money, card_area_top, card_area_bottom, forced_draws, current_bet, round_number

        CENTER = (WIDTH//2, HEIGHT//2)
        RADIUS = 380

        # -----------------------------
        # 初始化玩家位置與狀態
        # -----------------------------
        for i, p in enumerate(players):
            angle = 2*math.pi*i/len(players) - math.pi/2
            x = CENTER[0] + RADIUS*math.cos(angle)*1.5
            y = CENTER[1] + RADIUS*math.sin(angle)
            p.pos = (int(x), int(y))
            p.alive = True
            p.color = (255,255,255)
            p.money = 0

        # -----------------------------
        # 生成卡牌列表
        # -----------------------------
        safe_count = total_cards - len(players)
        pool_list = ["DEAD"]*(len(players)-1) + ["SAFE"]*safe_count

        pool_list.insert(0, None)  # 先占位給 WIN

        # 計算回合數十位+個位數
        round_digit_sum = round_number % 10 + round_number // 10

        # 設定合法 WIN 編號（奇數或偶數）
        if round_digit_sum % 2 == 0:
            valid_numbers = [n for n in range(2, total_cards+1, 2)]  # 偶數
        else:
            valid_numbers = [n for n in range(1, total_cards+1, 2)]  # 奇數

        # 隨機選一個合法編號放 WIN
        win_number = random.choice(valid_numbers)
        win_index = win_number - 1  # 列表索引 = 編號-1
        pool_list[0], pool_list[win_index] = pool_list[win_index], "WIN"  # 交換

        # 隨機排列其他牌（不改 WIN 位置）
        other_indices = [i for i in range(len(pool_list)) if i != win_index]
        other_cards = [pool_list[i] for i in other_indices]
        random.shuffle(other_cards)
        for idx, i in enumerate(other_indices):
            pool_list[i] = other_cards[idx]

        # -----------------------------
        # 計算卡牌在畫面上的位置
        # -----------------------------
        rows = (len(pool_list) + MAX_COLS - 1) // MAX_COLS
        start_x = WIDTH//2 - ((min(len(pool_list), MAX_COLS)*(CARD_WIDTH+SPACING)-SPACING)//2)
        start_y = HEIGHT//2 - ((rows*(CARD_HEIGHT+SPACING)-SPACING)//2)

        card_area_top = start_y
        card_area_bottom = start_y + rows*(CARD_HEIGHT+SPACING)

        # -----------------------------
        # 生成 PoolCard 物件
        # -----------------------------
        pool_cards.clear()
        for idx, type in enumerate(pool_list):
            row = idx // MAX_COLS
            col = idx % MAX_COLS
            x = start_x + col*(CARD_WIDTH+SPACING)
            y = start_y + row*(CARD_HEIGHT+SPACING)
            pool_cards.append(PoolCard(type, pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT), idx+1))

        # -----------------------------
        # 初始化金錢與抽牌次數
        # -----------------------------
        total_money = 0
        forced_draws = 0
        current_bet = 0

    players[:] = [Player(i) for i in range(player_count)]
    setup_game()

    current_index = random.randint(0, player_count-1)
    direction = 1
    game_over = False
    show_next_button = False
    next_button_rect = pygame.Rect(WIDTH//2-60, HEIGHT-70, 120, 50)

    def update_bet_buttons():
        buttons = []
        curr = players[current_index]
        if not curr.alive or game_over:
            return buttons
        options = []
        if forced_draws == 0:
            options = [5,10]
        elif forced_draws == 1:
            options = [10,15]
        elif forced_draws == 2:
            options = [15]
        x_start = WIDTH//2 - (len(options)*90)//2
        y_start = card_area_bottom + 40
        for i, val in enumerate(options):
            rect = pygame.Rect(x_start + i*90, y_start, 80, 40)
            buttons.append( (rect, val) )
        return buttons

    while True:
        clock.tick(60)
        screen.fill((30,30,40))

        # 回合數
        round_text = FONT.render(f"Round: {round_number}", True, (255,255,255))
        screen.blit(round_text, (20,20))

        # Total Money 顯示
        pot_text = FONT.render(f"Total Money: {total_money}", True, (255,255,0))
        if pool_cards:
            screen.blit(pot_text, (WIDTH//2 - pot_text.get_width()//2, pool_cards[0].rect.y - 40))

        # TIMES 顯示
        times_text = FONT.render(f"TIMES: {max(forced_draws,0)}", True, (255,255,255))
        if pool_cards:
            screen.blit(times_text, (WIDTH//2 - times_text.get_width()//2, pool_cards[-1].rect.y + CARD_HEIGHT + 10))

        # 畫玩家
        for p in players:
            pygame.draw.circle(screen, p.color, p.pos, 40)  # 玩家顏色變化
            pygame.draw.circle(screen, (0,0,0), p.pos, 40, 2)
            id_text = FONT.render(f"P{p.idx+1}", True, (0,0,0))
            money_text = FONT.render(str(p.money), True, (0,0,0))
            screen.blit(id_text, (p.pos[0] - id_text.get_width()//2, p.pos[1] - 25))
            screen.blit(money_text, (p.pos[0] - money_text.get_width()//2, p.pos[1] + 5))

        # 畫玩家頭像
        for i, p in enumerate(players):
            # 判斷是否輪到該玩家
            if not game_over and i == current_index and p.alive:
                draw_color = (255,255,0)  # 輪到玩家 → 黃色
            else:
                draw_color = p.color      # 原本顏色：白/紅/綠

            pygame.draw.circle(screen, draw_color, p.pos, 40, 0)  # 填滿顏色
            pygame.draw.circle(screen, (255,255,255), p.pos, 40, 2)  # 邊框

            id_text = FONT.render(f"P{p.idx+1}", True, (0,0,0))
            money_text = FONT.render(str(p.money), True, (0,0,0))
            screen.blit(id_text, (p.pos[0]-id_text.get_width()//2, p.pos[1]-25))
            screen.blit(money_text, (p.pos[0]-money_text.get_width()//2, p.pos[1]+5))

        # 畫卡牌
        for card in pool_cards:
            if card.revealed:
                if card.type=="SAFE":
                    color = (100,200,100)
                    text_str = "SAFE"
                elif card.type=="DEAD":
                    color = (200,100,100)
                    text_str = "LOSE"
                else:
                    color = (255,255,0)
                    text_str = "WIN"
                text = FONT.render(text_str, True, (0,0,0))
            else:
                color = (50,50,150)
                text = FONT.render(f"{card.number}", True, (255,255,255))
            pygame.draw.rect(screen, color, card.rect)
            screen.blit(text, (card.rect.x+5, card.rect.y+5))

        # Next 按鈕
        if show_next_button:
            pygame.draw.rect(screen, (255,255,255), next_button_rect)
            next_text = FONT.render("Next", True, (0,0,0))
            screen.blit(next_text, (next_button_rect.x+25, next_button_rect.y+10))

        # 加注按鈕
        bet_buttons = update_bet_buttons()
        for rect, val in bet_buttons:
            pygame.draw.rect(screen, (200,200,200), rect)
            btext = FONT.render(f"+{val}", True, (0,0,0))
            screen.blit(btext, (rect.x + 20, rect.y + 5))

        pygame.display.flip()

        # -------------------------
        # 事件處理
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Next 按鈕
                if show_next_button and next_button_rect.collidepoint(pos):
                    round_number += 1
                    setup_game()
                    current_index = random.randint(0, player_count-1)
                    direction = 1
                    game_over = False
                    show_next_button = False
                    continue

                if game_over:
                    continue

                curr = players[current_index]
                if not curr.alive:
                    while True:
                        current_index = (current_index + direction) % player_count
                        if players[current_index].alive:
                            break
                    continue

                # 點加注
                for rect, val in bet_buttons:
                    if rect.collidepoint(pos):
                        current_bet = val
                        forced_draws = val // 5
                        curr.money += current_bet
                        total_money += current_bet
                        while True:
                            current_index = (current_index + direction) % player_count
                            if players[current_index].alive:
                                break
                        break

                # 點卡牌抽取
                for card in pool_cards:
                    if card.rect.collidepoint(pos) and not card.used:
                        card.used = True
                        card.revealed = True
                        if forced_draws > 0:
                            forced_draws -= 1
                        else:
                            forced_draws = 0

                        if card.type=="WIN":
                            if curr.money > 0:
                                curr.color = (0,255,0)
                                game_over = True
                                show_next_button = True
                            else:
                                # 金額=0時視為SAFE，什麼都不做，玩家繼續抽牌
                                pass
                        elif card.type=="DEAD":
                            curr.color = (255,0,0)
                            curr.alive = False
                            direction *= -1

                        alive_players = [p for p in players if p.alive]
                        if len(alive_players)==1 or (card.type=="WIN" and curr.money > 0):
                            for c in pool_cards:
                                c.revealed = True
                            if len(alive_players)==1:
                                alive_players[0].color = (0,255,0)
                            game_over = True
                            show_next_button = True
                            break

                        if forced_draws == 0:
                            while True:
                                current_index = (current_index + direction) % player_count
                                if players[current_index].alive:
                                    break
                        break

# -------------------------
# Main
# -------------------------
def main():
    player_count, total_cards = input_screen()
    game_screen(player_count, total_cards)

if __name__=="__main__":
    main()
