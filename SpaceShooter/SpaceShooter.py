# -*- coding: utf-8 -*-
import tkinter as tk
import random
import os
import winsound

# --- Game Configuration ---
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 20
BULLET_SPEED = 10
ENEMY_SPEED = 3
SPAWN_RATE = 1000

class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Galaxy Defender - Final Submission")
        self.pack()

        # Get current script directory to find assets
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # --- 1. Try to load images ---
        self.bg_image = self.load_image("background.png") 
        self.player_image = self.load_image("player.png") 
        self.enemy_image = self.load_image("enemy.png")   

        # Create Canvas
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        # Draw Background if exists
        if self.bg_image:
            self.canvas.create_image(WIDTH/2, HEIGHT/2, image=self.bg_image)

        # Game State
        self.score = 0
        self.is_game_over = False
        self.bullets = []
        self.enemies = []
        self.keys_pressed = set()

        # UI Elements
        self.score_text = self.canvas.create_text(50, 30, text=f"Score: {self.score}", fill="white", font=("Arial", 14), anchor="w")

        # --- 2. Create Player (Use image if available, else use Polygon) ---
        self.player_center = [400, 550]
        if self.player_image:
            self.player = self.canvas.create_image(400, 550, image=self.player_image)
        else:
            # Fallback: Green Ship shape
            self.player = self.canvas.create_polygon(400, 550, 380, 580, 420, 580, fill="#00FF00", outline="white")

        # Bind Keys
        self.master.bind("<KeyPress>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)
        self.master.bind("<space>", self.shoot)

        # Start Game Loop
        self.spawn_enemy()
        self.update_game()

    def load_image(self, filename):
        """ Safely load image, return None if failed """
        try:
            path = os.path.join(self.base_path, "assets", filename)
            img = tk.PhotoImage(file=path)
            return img
        except Exception:
            # If image not found, return None (will use shapes instead)
            return None

    def play_sound(self, filename):
        """ Safely play sound """
        try:
            path = os.path.join(self.base_path, "assets", filename)
            winsound.PlaySound(path, winsound.SND_ASYNC)
        except:
            pass 

    def on_key_press(self, event):
        self.keys_pressed.add(event.keysym)

    def on_key_release(self, event):
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)

    def shoot(self, event):
        if not self.is_game_over:
            x, y = self.player_center
            # Create Bullet (Yellow rectangle)
            bullet = self.canvas.create_rectangle(x-2, y-20, x+2, y-10, fill="yellow")
            self.bullets.append(bullet)
            
            # --- 3. Play Shoot Sound ---
            self.play_sound("shoot.wav")

    def spawn_enemy(self):
        if not self.is_game_over:
            x = random.randint(30, WIDTH-30)
            
            # --- 4. Create Enemy ---
            if self.enemy_image:
                enemy = self.canvas.create_image(x, -30, image=self.enemy_image)
            else:
                # Fallback: Red Circle
                enemy = self.canvas.create_oval(x-15, -30, x+15, 0, fill="red", outline="red")
            
            self.enemies.append(enemy)
            # Increase difficulty
            rate = max(200, SPAWN_RATE - self.score * 10)
            self.master.after(rate, self.spawn_enemy)

    def move_player(self):
        dx = 0
        if "Left" in self.keys_pressed and self.player_center[0] > 20:
            dx = -PLAYER_SPEED
        elif "Right" in self.keys_pressed and self.player_center[0] < WIDTH - 20:
            dx = PLAYER_SPEED
        
        if dx != 0:
            self.canvas.move(self.player, dx, 0)
            self.player_center[0] += dx

    def check_collision(self):
        player_bbox = self.canvas.bbox(self.player)
        
        for enemy in self.enemies:
            enemy_bbox = self.canvas.bbox(enemy)
            
            if enemy_bbox and player_bbox:
                # Enemy hits Player
                if (player_bbox[0] < enemy_bbox[2] and player_bbox[2] > enemy_bbox[0] and
                    player_bbox[1] < enemy_bbox[3] and player_bbox[3] > enemy_bbox[1]):
                    self.game_over()
                    return

            # Bullet hits Enemy
            for bullet in self.bullets:
                bullet_bbox = self.canvas.bbox(bullet)
                if enemy_bbox and bullet_bbox:
                    if (bullet_bbox[0] < enemy_bbox[2] and bullet_bbox[2] > enemy_bbox[0] and
                        bullet_bbox[1] < enemy_bbox[3] and bullet_bbox[3] > enemy_bbox[1]):
                        
                        self.canvas.delete(enemy)
                        self.canvas.delete(bullet)
                        if enemy in self.enemies: self.enemies.remove(enemy)
                        if bullet in self.bullets: self.bullets.remove(bullet)
                        self.score += 10
                        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                        
                        # --- 5. Play Explosion Sound ---
                        self.play_sound("explosion.wav")
                        break

    def update_game(self):
        if self.is_game_over:
            return
        self.move_player()
        
        # Move Bullets
        for bullet in self.bullets:
            self.canvas.move(bullet, 0, -BULLET_SPEED)
            if self.canvas.coords(bullet)[3] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)
        
        # Move Enemies
        for enemy in self.enemies:
            self.canvas.move(enemy, 0, ENEMY_SPEED)
            if self.canvas.coords(enemy)[1] > HEIGHT:
                self.canvas.delete(enemy)
                self.enemies.remove(enemy)
                
        self.check_collision()
        self.master.after(16, self.update_game)

    def game_over(self):
        self.is_game_over = True
        self.canvas.create_text(WIDTH/2, HEIGHT/2, text="GAME OVER", fill="red", font=("Arial", 40, "bold"))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 50, text=f"Final Score: {self.score}", fill="white", font=("Arial", 20))

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    # Center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - WIDTH) // 2
    y = (screen_height - HEIGHT) // 2
    root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
    
    game = Game(root)
    root.mainloop()