import os
import pygame
from pygame import mixer
import sys
import subprocess

# ---------------------------
# Initialize Pygame
# ---------------------------
pygame.init()
mixer.init()

# Load background music and click sound
mixer.music.load('cutemusic.ogg')
mixer.music.play(-1)
click_sound = mixer.Sound("mouse-click.ogg")
click_sound.set_volume(0.5)

# ---------------------------
# Window
# ---------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Finance Game with Character Customization")

# ---------------------------
# Colors
# ---------------------------
PURPLE = (160, 32, 240)
WHITE = (255, 255, 255)
LIGHTPINK = (247, 168, 200)
DARKPINK = (250, 123, 174)
BOX_COLOR = (50, 50, 50)
BOX_BORDER = (200, 200, 200)
NAME_COLOR = (255, 255, 0)
TEXT_COLOR = WHITE

# ---------------------------
# Fonts
# ---------------------------
title_font = pygame.font.SysFont("lucidahandwriting", 70, italic=True)
subtitle_font = pygame.font.SysFont("Segoe Script", 50)
button_font = pygame.font.SysFont("arial", 40)
FONT = pygame.font.SysFont("Georgia", 24)

# ---------------------------
# Menu setup
# ---------------------------
title_text = title_font.render("a girl's guide to finance", True, WHITE)
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

button_text = button_font.render("start", True, WHITE)
button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
button_box = pygame.Rect(button_rect.left - 20, button_rect.top - 10,
                        button_rect.width + 40, button_rect.height + 20)

# ---------------------------
# Character customization
# ---------------------------
subtitle_text = subtitle_font.render("character customization! choose your avatar.", True, WHITE)
subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))

outfit_files = ["outfit1.png", "outfit2.png", "outfit3.png", "outfit4.png"]
outfits = [pygame.transform.scale(pygame.image.load(f), (150, 150)) for f in outfit_files]

outfit_positions = [
   (WIDTH // 5 - 75, 200),
   (2 * WIDTH // 5 - 75, 200),
   (3 * WIDTH // 5 - 75, 200),
   (4 * WIDTH // 5 - 75, 200)
]

selected_outfit = None
character_sprite = None

char_continue_text = button_font.render("continue", True, WHITE)
char_continue_rect = char_continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
char_continue_box = pygame.Rect(char_continue_rect.left - 20, char_continue_rect.top - 10,
                               char_continue_rect.width + 40, char_continue_rect.height + 20)

# ---------------------------
# Chat setup
# ---------------------------
BOX_X, BOX_Y = 50, 400
BOX_WIDTH, BOX_HEIGHT = 700, 150

back_text = button_font.render("back", True, WHITE)
back_rect = back_text.get_rect(topright=(WIDTH - 50, 50))
back_box = pygame.Rect(back_rect.left - 10, back_rect.top - 5,
                      back_rect.width + 20, back_rect.height + 10)

conversations = {
   "federal reserve": [
       ("Invisible Mentor: Welcome to the Trade Port! Do you want to learn about federal reserve?",
        ["Yes, I’m curious!", "No, not right now."],
        ["Great! The federal reserve is the central banking system of the U.S. that manages money supply, interest rates, and financial stability.. (click space to move on)",
         "No worries! We can come back to federal reserve later. (click space to move on)"])
   ],
   "credit score": [
       ("Invisible Mentor: Would you like to learn some basics about credit score?",
        ["Yes, teach me!", "No, maybe later."],
        ["Awesome! Credit scores are numerical ratings that reflect a person’s creditworthiness based on their borrowing and repayment history. (click space to move on)",
         "That's okay! We can discuss credit scores another time. (click space to move on)"])
   ],
   "blockchain": [
       ("Invisible Mentor: Interested in hearing about blockchain?",
        ["Yes, tell me!", "No, thanks."],
        ["Blockchain decentralized digital ledger that securely records transactions in linked blocks. (click space to move on)",
         "No problem! You can learn about blockchain another time. (click space to move on)"])
   ]
}

chat_queue = [entry for topic in conversations for entry in conversations[topic]]
current_chat = 0
chat_state = "question"
selected_option = None

# ---------------------------
# Play screen setup
# ---------------------------
char_x, char_y = WIDTH // 2, HEIGHT // 2
speed = 5

map_background = pygame.image.load("map.png").convert()
map_background = pygame.transform.scale(map_background, (WIDTH, HEIGHT))

# ---------------------------
# Helper functions
# ---------------------------
def draw_chat_box():
   pygame.draw.rect(screen, BOX_COLOR, (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT))
   pygame.draw.rect(screen, BOX_BORDER, (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT), 3)

def draw_wrapped_text(text, x, y, max_width, color=TEXT_COLOR, line_height=25):
   words = text.split(' ')
   lines, current_line = [], ""
   for word in words:
       test_line = current_line + word + " "
       if FONT.size(test_line)[0] <= max_width:
           current_line = test_line
       else:
           lines.append(current_line)
           current_line = word + " "
   lines.append(current_line)
   for i, line in enumerate(lines):
       rendered = FONT.render(line, True, color)
       screen.blit(rendered, (x, y + i * line_height))

# ---------------------------
# Main loop
# ---------------------------
current_screen = "menu"
running = True
clock = pygame.time.Clock()

while running:
   dt = clock.tick(60)

   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False

       # Menu
       if current_screen == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
           if button_box.collidepoint(event.pos):
               click_sound.play()
               current_screen = "character"

       # Character selection
       elif current_screen == "character" and event.type == pygame.MOUSEBUTTONDOWN:
           for i, (x, y) in enumerate(outfit_positions):
               rect = pygame.Rect(x, y, 150, 150)
               if rect.collidepoint(event.pos):
                   selected_outfit = i
           if selected_outfit is not None and char_continue_box.collidepoint(event.pos):
               click_sound.play()
               character_sprite = outfits[selected_outfit]
               current_screen = "chat"
               current_chat = 0
               chat_state = "question"
               selected_option = None

       # Chat events
       elif current_screen == "chat":
           if event.type == pygame.MOUSEBUTTONDOWN and back_box.collidepoint(event.pos):
               click_sound.play()
               current_screen = "menu"
           elif event.type == pygame.KEYDOWN:
               click_sound.play()
               if chat_state == "options":
                   if event.key == pygame.K_1:
                       selected_option = 0
                       chat_state = "reply"
                   elif event.key == pygame.K_2:
                       selected_option = 1
                       chat_state = "reply"
               elif chat_state == "reply" and event.key == pygame.K_SPACE:
                   # Launch mini-game if option 1 was selected
                   q_text = chat_queue[current_chat][0]
                   try:
                       base_path = os.path.dirname(os.path.abspath(__file__))
                       if "Trade Port" in q_text and selected_option == 0:
                           subprocess.Popen([sys.executable, os.path.join(base_path, "FedReserveMiniGame.py")])
                       elif "credit score" in q_text and selected_option == 0:
                           subprocess.Popen([sys.executable, os.path.join(base_path, "CreditMiniGame.py")])
                       elif "blockchain" in q_text and selected_option == 0:
                           subprocess.Popen([sys.executable, os.path.join(base_path, "blockchain_game.py")])
                   except Exception as e:
                       print(f"Mini-game launch failed: {e}")

                   current_screen = "play"

       # Play screen events
       elif current_screen == "play" and event.type == pygame.KEYDOWN:
           if event.key == pygame.K_SPACE:
               click_sound.play()
               current_chat += 1
               if current_chat >= len(chat_queue):
                   running = False
               else:
                   chat_state = "question"
                   selected_option = None
                   current_screen = "chat"

   # ---------------- Drawing ----------------
   if current_screen == "menu":
       screen.fill(PURPLE)
       screen.blit(title_text, title_rect)
       pygame.draw.rect(screen, DARKPINK, button_box, border_radius=10)
       screen.blit(button_text, button_rect)

   elif current_screen == "character":
       screen.fill(LIGHTPINK)
       screen.blit(subtitle_text, subtitle_rect)
       for i, (x, y) in enumerate(outfit_positions):
           screen.blit(outfits[i], (x, y))
           if selected_outfit == i:
               pygame.draw.rect(screen, WHITE, (x-5, y-5, 160, 160), 3)
       pygame.draw.rect(screen, DARKPINK, char_continue_box, border_radius=10)
       screen.blit(char_continue_text, char_continue_rect)

   elif current_screen == "chat":
       screen.fill(LIGHTPINK)
       draw_chat_box()
       pygame.draw.rect(screen, DARKPINK, back_box, border_radius=5)
       screen.blit(back_text, back_rect)
       if current_chat < len(chat_queue):
           question, options, replies = chat_queue[current_chat]
           if chat_state == "question":
               draw_wrapped_text(question, BOX_X + 10, BOX_Y + 10, BOX_WIDTH - 20, NAME_COLOR)
               chat_state = "options"
           elif chat_state == "options":
               draw_wrapped_text(question, BOX_X + 10, BOX_Y + 10, BOX_WIDTH - 20, NAME_COLOR)
               draw_wrapped_text("1. " + options[0], BOX_X + 10, BOX_Y + 50, BOX_WIDTH - 20)
               draw_wrapped_text("2. " + options[1], BOX_X + 10, BOX_Y + 80, BOX_WIDTH - 20)
           elif chat_state == "reply":
               draw_wrapped_text(replies[selected_option], BOX_X + 10, BOX_Y + 10, BOX_WIDTH - 20)

   elif current_screen == "play":
       screen.blit(map_background, (0, 0))
       keys = pygame.key.get_pressed()
       if keys[pygame.K_LEFT]: char_x -= speed
       if keys[pygame.K_RIGHT]: char_x += speed
       if keys[pygame.K_UP]: char_y -= speed
       if keys[pygame.K_DOWN]: char_y += speed

       char_x = max(0, min(WIDTH - 150, char_x))
       char_y = max(0, min(HEIGHT - 150, char_y))

       if character_sprite:
           screen.blit(character_sprite, (char_x, char_y))

       info_text = FONT.render("Press SPACE to continue", True, WHITE)
       screen.blit(info_text, (WIDTH // 2 - 100, HEIGHT - 50))

   pygame.display.flip()

pygame.quit()
sys.exit()




