import tkinter as tk
from tkinter import ttk
import time
import threading

class BlockchainGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blockchain Transaction Game")
        self.root.geometry("1000x700")
        self.root.configure(bg='#E8F4FD')  # Light blue background
        
        # Game state
        self.game_running = False
        self.current_instruction_step = 0
        self.instruction_steps = [
            "Try giving Bob 5 coins by clicking on your coins",
            "Try giving Bob 3 coins by clicking on your coins", 
            "Try giving Bob 2 coins by clicking on your coins",
            "Click a coin in the bank to lend it to Bob to fix the broken link",
            "The blocks in the blockchain are now hashed together and encrypted by complex algorithms",
            "Congratulations! Your transaction was successful and a hacker will not be able to alter the data in the blockchain"
        ]
        self.current_scenario = 0
        self.scenarios = [
            {"coins_needed": 5},
            {"coins_needed": 3},
            {"coins_needed": 2}
        ]
        
        # Player states
        self.player_coins = 9
        self.bob_coins = 0
        self.bank_coins = float('inf')
        
        # UI elements
        self.coin_images = []
        self.bank_coin_images = []
        self.dragged_coins = []
        self.transaction_boxes = []
        self.blockchain_links = []

        # bank initialization guard
        self.bank_initialized = False
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure the pastel color scheme"""
        style = ttk.Style()
        
        style.configure('Start.TButton',
                        background='#A8D5BA',  # Sage green
                        foreground='#2C3E50',
                        font=('Segoe UI', 12, 'bold'),
                        padding=(20, 10))
        
        style.configure('Hash.TButton',
                        background='#F4A6B7',  # Pastel pink
                        foreground='#2C3E50',
                        font=('Segoe UI', 14, 'bold'),
                        padding=(15, 10))
        
        style.configure('Exit.TButton',
                        background='#F4A6B7',  # Pastel pink
                        foreground='#2C3E50',
                        font=('Segoe UI', 10),
                        padding=(10, 5))
        
    def setup_ui(self):
        """Create the main user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#E8F4FD', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                               text="Blockchain Transaction Game",
                               font=('Segoe UI', 24, 'bold'),
                               fg='#2C3E50',
                               bg='#E8F4FD')
        title_label.pack(pady=(0, 20))
        
        # Start button
        self.start_button = ttk.Button(main_frame,
                                       text="Start Game",
                                       style='Start.TButton',
                                       command=self.start_game)
        self.start_button.pack(pady=20)
        
        # Game container (initially hidden)
        self.game_container = tk.Frame(main_frame, bg='#E8F4FD')
        
        # Exit button
        exit_button = ttk.Button(self.game_container,
                                 text="✕ Exit",
                                 style='Exit.TButton',
                                 command=self.exit_game)
        exit_button.pack(anchor='ne', pady=(0, 20))
        
        # Goal display
        self.create_goal_display()
        
        # Separate instruction box
        self.create_separate_instruction_box()
        
        # Avatars and money display
        self.create_avatar_section()
        
        # Bank section (always has coins visually, but still "not accessible" until player=0)
        self.create_bank_section()
        
        # Transaction boxes area
        self.create_transaction_area()
        
        # Hash button (initially hidden)
        self.hash_button = ttk.Button(self.game_container,
                                      text="Hash it!",
                                      style='Hash.TButton',
                                      command=self.hash_transaction)
        
        # Success message (initially hidden)
        self.success_label = tk.Label(self.game_container,
                                      text="",
                                      font=('Segoe UI', 20, 'bold'),
                                      fg='#27AE60',
                                      bg='#E8F4FD')
        
    def create_separate_instruction_box(self):
        """Create a separate instruction box with Next button"""
        instruction_container = tk.Frame(self.game_container, bg='#E8F4FD')
        instruction_container.pack(fill='x', pady=(0, 20))
        
        # Instruction box
        self.separate_instruction_frame = tk.Frame(instruction_container,
                                                 bg='#FFF3CD',
                                                 relief='solid',
                                                 borderwidth=2,
                                                 padx=20,
                                                 pady=15)
        self.separate_instruction_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.separate_instruction_label = tk.Label(self.separate_instruction_frame,
                                                   text="Welcome! Click 'Start Game' to begin.",
                                                   font=('Segoe UI', 14, 'bold'),
                                                   fg='#856404',
                                                   bg='#FFF3CD',
                                                   wraplength=600,
                                                   justify='left')
        self.separate_instruction_label.pack(anchor='w')
        
        # Next button container
        next_button_container = tk.Frame(instruction_container, bg='#E8F4FD')
        next_button_container.pack(side='right', padx=(10, 0))
        
        self.separate_next_button = ttk.Button(next_button_container,
                                               text="Next",
                                               style='Hash.TButton',
                                               command=self.next_instruction_step)
        
    def create_goal_display(self):
        """Create the goal display"""
        goal_frame = tk.Frame(self.game_container, 
                             bg='#FFFFFF',
                             relief='solid',
                             borderwidth=1,
                             padx=15,
                             pady=10)
        goal_frame.pack(fill='x', pady=(0, 20))
        
        goal_text = "Goal: Get Bob to 10 coins. You can only access the bank if you have no money."
        tk.Label(goal_frame,
                 text=goal_text,
                 font=('Segoe UI', 14, 'bold'),
                 fg='#2C3E50',
                 bg='#FFFFFF',
                 wraplength=900).pack()
        
    def create_avatar_section(self):
        """Create the avatar and money display section"""
        avatar_frame = tk.Frame(self.game_container, bg='#E8F4FD')
        avatar_frame.pack(fill='x', pady=(0, 20))
        
        # Bob section
        bob_frame = tk.Frame(avatar_frame, bg='#FFFFFF', relief='solid', borderwidth=1, padx=20, pady=15)
        bob_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(bob_frame,
                 text="Bob",
                 font=('Segoe UI', 16, 'bold'),
                 fg='#2C3E50',
                 bg='#FFFFFF').pack()
        
        # removed bob amount label per request
        
        # Bob coin display area
        self.bob_coin_area = tk.Frame(bob_frame, bg='#F8F9FA', height=100, relief='solid', borderwidth=1)
        self.bob_coin_area.pack(fill='x', pady=10)
        self.bob_coin_area.pack_propagate(False)
        self.bob_coin_area.lift()  # Ensure coin area is on top (within bob_frame)

        # Player section
        player_frame = tk.Frame(avatar_frame, bg='#FFFFFF', relief='solid', borderwidth=1, padx=20, pady=15)
        player_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(player_frame,
                 text="You",
                 font=('Segoe UI', 16, 'bold'),
                 fg='#2C3E50',
                 bg='#FFFFFF').pack()
        
        # removed player amount label per request

        # Player coin display area
        self.player_coin_area = tk.Frame(player_frame, bg='#F8F9FA', height=100, relief='solid', borderwidth=1)
        self.player_coin_area.pack(fill='x', pady=10)
        self.player_coin_area.pack_propagate(False)
        self.player_coin_area.lift()  # Ensure coin area is on top (within player_frame)
        
    def create_bank_section(self):
        """Create the bank section (visually always has coins; access controlled by instruction text)"""
        bank_frame = tk.Frame(self.game_container,
                             bg='#FFFFFF',
                             relief='solid',
                             borderwidth=1,
                             padx=20,
                             pady=15)
        bank_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(bank_frame,
                 text="Bank",
                 font=('Segoe UI', 14, 'bold'),
                 fg='#2C3E50',
                 bg='#FFFFFF').pack()
        
        tk.Label(bank_frame,
                 text="Only accessible when you have no money",
                 font=('Segoe UI', 10),
                 fg='#7F8C8D',
                 bg='#FFFFFF').pack()
        
        # Bank coin area (starts filled)
        self.bank_coin_area = tk.Frame(bank_frame, bg='#F8F9FA', height=80, relief='solid', borderwidth=1)
        self.bank_coin_area.pack(fill='x', pady=10)
        self.bank_coin_area.pack_propagate(False)
        self.bank_coin_area.lift()
        
        # Always create bank coins visually, but access logic still prevents clicking when player > 0
        self.initialize_bank_coins()
        
    def create_transaction_area(self):
        """Create the transaction boxes area"""
        self.transaction_frame = tk.Frame(self.game_container, bg='#E8F4FD', height=200)
        self.transaction_frame.pack(fill='x', pady=(0, 20))
        self.transaction_frame.pack_propagate(False)
        
    def create_coin(self, parent, x, y, color='#FFD700'):
        """Create a coin that is transferred by clicking (drag/drop disabled)"""
        # Use parent's background for the canvas, so only the oval is visible
        coin = tk.Canvas(parent, width=30, height=30, bg=parent.cget('bg'), highlightthickness=0)
        coin.place(x=x, y=y)
        
        # Draw coin design and keep IDs
        oval_id = coin.create_oval(5, 5, 25, 25, fill=color if color != '#FFD700' else '#FFA500', outline='#FF8C00', width=2)
        coin.create_text(15, 15, text="$", font=('Arial', 12, 'bold'), fill='white')
        
        # Make clickable: clicking transfers the coin based on its logical location
        coin.bind("<Button-1>", lambda e, c=coin: self.coin_clicked(c))
        
        # Ensure coin is visible above other elements
        coin.tag_raise("all")
        
        # track logical location: will be set by caller after creation
        coin.location = None
        
        return coin
        
    def coin_clicked(self, coin):
        """Handle clicks on coins to transfer them (no dragging)"""
        loc = getattr(coin, "location", None)
        # If player coin clicked -> give to Bob
        if loc == 'player':
            # only allow transfers when we are in a scenario and game active
            if self.current_scenario < len(self.scenarios):
                new_coin = self.move_coin_to_bob(coin)
                # Track for current transaction (track new coin)
                self.dragged_coins.append(new_coin)
                scenario = self.scenarios[self.current_scenario]
                if len(self.dragged_coins) >= scenario["coins_needed"]:
                    # complete after a short delay to allow UI update
                    self.root.after(200, self.complete_transaction)
                else:
                    # if last coin and scenario requires bank, prompt
                    if (self.current_scenario == 2 and len(self.dragged_coins) == 1 and self.player_coins == 1):
                        self.show_bank_instruction()
        # If bank coin clicked -> withdraw to player (only if player has no money)
        elif loc == 'bank':
            if self.player_coins == 0 and self.current_scenario < len(self.scenarios):
                new_coin = self.move_coin_to_player(coin)
            else:
                # ignore clicks if player still has money
                pass
        # If Bob coin clicked -> do nothing
        else:
            pass

    def handle_coin_drop_to_bob(self, coin):
        """Legacy method (no-op now) kept for compatibility"""
        # drag/drop disabled — use coin_clicked instead
        self.move_coin_to_bob(coin)
        
    def handle_coin_drop_to_player(self, coin):
        """Legacy method (no-op now) kept for compatibility"""
        self.move_coin_to_player(coin)
        
    def handle_coin_drop_to_bank(self, coin):
        """Legacy method (no-op now) kept for compatibility"""
        self.move_coin_to_bank(coin)
        
    def update_coin_counts(self):
        """Update coin counts based on logical location of coins (canvas children)"""
        # Count coins in player's area
        player_count = sum(1 for widget in self.player_coin_area.winfo_children() if isinstance(widget, tk.Canvas))
        # Count coins in Bob's area
        bob_count = sum(1 for widget in self.bob_coin_area.winfo_children() if isinstance(widget, tk.Canvas))
        
        # Update the counts
        self.player_coins = player_count
        self.bob_coins = bob_count
        
        # Do NOT update labels (removed per request)
        
        # Bank is always visually filled; no need to change bank initialization here
                        
    def show_bank_instruction(self):
        """Show instruction to use bank when player runs out of money"""
        instruction_text = ("You don't have enough money!Click a coin in the bank to withdraw it to your wallet.")
        
        self.separate_instruction_label.config(text=instruction_text, fg='#C0392B')
        
        # Access is controlled by game logic: bank coins exist but are usable only when player_coins == 0
        # no further action required here
        pass
        
    def enable_bank_access(self):
        """Bank coins are clickable already; method kept for compatibility"""
        pass
        
    def complete_transaction(self):
        """Complete the current transaction"""
        if self.current_scenario < len(self.scenarios):
            scenario = self.scenarios[self.current_scenario]
            coins_transferred = len(self.dragged_coins)
            
            # Animate transaction box
            self.animate_transaction_box(coins_transferred)
            
            # reset tracked coins for this scenario and move to next
            self.dragged_coins = []
            self.current_scenario += 1
            # show completion after a short delay so animation can run
            self.root.after(400, self.show_transaction_complete)
            
    def show_transaction_complete(self):
        """Show transaction completion message"""
        completion_text = f"✅ Transaction complete! Bob now has {self.bob_coins} coins."
        self.separate_instruction_label.config(text=completion_text, fg='#27AE60')
        self.separate_next_button.pack(pady=10)
            
    def animate_transaction_box(self, coins_count):
        """Animate the transaction box moving to Bob's side"""
        # Create transaction box
        box = tk.Frame(self.transaction_frame, 
                       bg='#E8F4FD', 
                       relief='solid', 
                       borderwidth=2,
                       padx=10,
                       pady=5)
        box.pack(side='left', padx=10)
        
        tk.Label(box,
                 text=f"{coins_count} coins",
                 font=('Segoe UI', 12, 'bold'),
                 fg='#2C3E50',
                 bg='#E8F4FD').pack()
        
        self.transaction_boxes.append(box)
        
        # Animate movement
        self.animate_box_movement(box)
        
    def animate_box_movement(self, box):
        """Animate box moving to bottom of screen"""
        # Simple animation by changing position
        def move_box():
            box.pack_forget()
            box.pack(side='bottom', pady=10)
            
        self.root.after(500, move_box)
        
        
    def hash_transaction(self):
        """Create blockchain link animation"""
        if len(self.transaction_boxes) >= 2:
            # Create link between boxes
            self.create_blockchain_link()
            
    def create_blockchain_link(self):
        """Create visual link between transaction boxes"""
        # Create a canvas for the link
        link_canvas = tk.Canvas(self.transaction_frame, 
                                bg='#E8F4FD', 
                                height=50, 
                                highlightthickness=0)
        link_canvas.pack(fill='x', pady=10)
        
        # Draw chain link
        link_canvas.create_line(50, 25, 200, 25, fill='#34495E', width=3)
        link_canvas.create_text(125, 15, text="Blockchain Link", 
                                font=('Segoe UI', 10, 'bold'), 
                                fill='#2C3E50')
        
        self.blockchain_links.append(link_canvas)
        
    def show_success(self):
        """Show success message"""
        success_text = ("Congratulations! Your transaction was successful and a hacker "
                        "will not be able to alter the data in the blockchain")
        
        self.success_label.config(text=success_text)
        self.success_label.pack(pady=50)
        
    def start_game(self):
        """Start the game"""
        self.game_running = True
        self.start_button.pack_forget()
        self.game_container.pack(fill='both', expand=True)
        
        # Initialize coins (player first)
        self.initialize_coins()
        
        # Show first instruction immediately
        self.separate_instruction_label.config(text=self.instruction_steps[0])
        self.separate_next_button.pack(pady=10)
        
    def initialize_coins(self):
        """Initialize player coins"""
        # create player coins visually and set location marker
        for i in range(self.player_coins):
            x = 20 + (i % 5) * 35
            y = 20 + (i // 5) * 35
            coin = self.create_coin(self.player_coin_area, x, y)
            coin.location = 'player'
            self.coin_images.append(coin)
        # update logical counts after player coins exist
        self.update_coin_counts()
            
    def initialize_bank_coins(self):
        """Initialize bank with many coins (always present visually)"""
        if self.bank_initialized:
            return
        self.bank_coin_images = []
        for i in range(20):  # Fill bank with 20 coins
            x = 20 + (i % 10) * 30
            y = 20 + (i // 10) * 30
            coin = self.create_coin(self.bank_coin_area, x, y, '#A8D5BA')
            try:
                coin.itemconfig(1, fill='#A8D5BA', outline='#6F9E7C')
            except Exception:
                pass
            coin.location = 'bank'
            self.bank_coin_images.append(coin)
        self.bank_initialized = True
        # do NOT call update_coin_counts() here to avoid overwriting player_coins before player init
        # bank is visually present but inaccessible until player_coins == 0 per game rules
            
    # --- Helper methods for click-based movement ---
    def _recreate_coin_on_parent(self, old_coin, parent, x, y, location):
        """Create a new coin on `parent` with same appearance as old_coin and destroy old_coin.
           Returns the new coin."""
        # Try to get old color (oval id usually 1)
        color = '#FFA500'
        try:
            color = old_coin.itemcget(1, 'fill') or color
        except Exception:
            pass

        # Create new coin on target parent
        new_coin = self.create_coin(parent, x, y, color=color)
        new_coin.location = location

        # Remove old coin from any lists that reference it
        try:
            if old_coin in self.coin_images:
                self.coin_images.remove(old_coin)
        except Exception:
            pass
        try:
            if old_coin in self.bank_coin_images:
                self.bank_coin_images.remove(old_coin)
        except Exception:
            pass

        # If old_coin is visible, destroy it
        try:
            old_coin.destroy()
        except Exception:
            pass

        # Keep tracking for player coins list
        if location == 'player':
            self.coin_images.append(new_coin)
        elif location == 'bank':
            self.bank_coin_images.append(new_coin)

        return new_coin

    def move_coin_to_bob(self, coin):
        """Recreate coin as a child of Bob's area and return the new coin"""
        # compute next spot in bob area
        bob_children = [w for w in self.bob_coin_area.winfo_children() if isinstance(w, tk.Canvas)]
        i = len(bob_children)
        x = 10 + (i % 10) * 30
        y = 10 + (i // 10) * 30

        new_coin = self._recreate_coin_on_parent(coin, self.bob_coin_area, x, y, 'bob')
        new_coin.lift()
        # refresh logical counts after move
        self.update_coin_counts()
        return new_coin

    def move_coin_to_player(self, coin):
        """Withdraw bank coin to player's area (recreate) and return the new coin"""
        player_children = [w for w in self.player_coin_area.winfo_children() if isinstance(w, tk.Canvas)]
        i = len(player_children)
        x = 20 + (i % 5) * 35
        y = 20 + (i // 5) * 35

        new_coin = self._recreate_coin_on_parent(coin, self.player_coin_area, x, y, 'player')
        new_coin.lift()
        # refresh logical counts after move
        self.update_coin_counts()
        return new_coin

    def move_coin_to_bank(self, coin):
        """Return coin to bank area (recreate) and return the new coin"""
        bank_children = [w for w in self.bank_coin_area.winfo_children() if isinstance(w, tk.Canvas)]
        i = len(bank_children)
        x = 20 + (i % 10) * 30
        y = 20 + (i // 10) * 30

        new_coin = self._recreate_coin_on_parent(coin, self.bank_coin_area, x, y, 'bank')
        new_coin.lift()
        # refresh logical counts after move
        self.update_coin_counts()
        return new_coin
    # --- end helper methods ---
            
    def next_instruction_step(self):
        """Move to next instruction step"""
        self.current_instruction_step += 1
        
        if self.current_instruction_step < len(self.instruction_steps):
            instruction_text = self.instruction_steps[self.current_instruction_step]
            self.separate_instruction_label.config(text=instruction_text)
            
            # Show Next button
            self.separate_next_button.pack(pady=10)
            
            # Handle special cases
            if self.current_instruction_step == 3:  # Bank instruction
                self.enable_bank_access()
            elif self.current_instruction_step == 4:  # Blockchain explanation
                self.create_blockchain_link()
            elif self.current_instruction_step == 5:  # Final success
                self.separate_next_button.pack_forget()
        else:
            # Game complete
            self.separate_next_button.pack_forget()
            
    def exit_game(self):
        """Exit the game"""
        self.game_running = False
        self.root.quit()
        
    def run(self):
        """Start the game"""
        self.root.mainloop()

if __name__ == "__main__":
    game = BlockchainGame()
    game.run()