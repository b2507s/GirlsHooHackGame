import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

class CreditScoreGame:
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Credit Score Challenge")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.root.minsize(900, 700)
        
        # Color scheme
        self.colors = {
            'pastel_pink': '#FFB6C1',
            'pastel_purple': '#DDA0DD', 
            'pastel_blue': '#B0E0E6',
            'sage_green': '#9CAF88',
            'light_purple': '#E6E6FA',
            'light_blue': '#F0F8FF',
            'soft_green': '#F0FFF0',
            'cream': '#FFF8DC'
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['light_blue'])
        
        # Game state
        self.current_month = 1
        self.max_months = 12
        self.target_score = 750
        self.game_over = False
        
        # Credit factors (0-100 scale, converted to credit score)
        self.payment_history = 0      # 35% weight
        self.credit_utilization = 0  # 30% weight  
        self.credit_age = 0          # 15% weight
        self.credit_mix = 0          # 10% weight
        self.inquiries = 0           # 10% weight
        
        # Game history
        self.credit_cards = []
        self.loans = []
        self.payment_history_list = []
        self.inquiry_count = 0
        self.monthly_events = []
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['light_blue'])
        title_frame.pack(pady=15)
        
        # Create rounded title background
        title_bg = tk.Frame(title_frame, bg=self.colors['pastel_purple'], relief=tk.RAISED, bd=3)
        title_bg.pack(pady=5, padx=20, ipadx=20, ipady=10)
        
        tk.Label(title_bg, text="🏦 Credit Score Challenge", 
                font=("Arial", 22, "bold"), fg="white", bg=self.colors['pastel_purple']).pack()
        
        tk.Label(title_bg, text="Build your credit score from scratch!", 
                font=("Arial", 13), fg="white", bg=self.colors['pastel_purple']).pack(pady=(5, 0))
        
        # Create main scrollable frame for entire window
        main_canvas = tk.Canvas(self.root, bg=self.colors['light_blue'], highlightthickness=0)
        main_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_scrollable_frame = tk.Frame(main_canvas, bg=self.colors['light_blue'])
        
        # Configure main scrolling
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
        
        # Pack main canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to main canvas
        def _on_main_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_main_mousewheel)
        
        # Update scroll region when main frame changes
        def _configure_main_scroll(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        main_scrollable_frame.bind("<Configure>", _configure_main_scroll)
        
        # Main content frame
        main_frame = tk.Frame(main_scrollable_frame, bg=self.colors['light_blue'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Credit Score Display
        left_panel = tk.Frame(main_frame, bg=self.colors['light_blue'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Credit Score Circle with rounded background
        self.score_frame = tk.Frame(left_panel, bg=self.colors['pastel_pink'], relief=tk.RAISED, bd=3)
        self.score_frame.pack(pady=10, padx=10, ipadx=10, ipady=10)
        
        self.score_canvas = tk.Canvas(self.score_frame, width=200, height=200, bg=self.colors['cream'], 
                                    highlightthickness=0, relief=tk.FLAT)
        self.score_canvas.pack()
        
        # Credit factors display with rounded styling
        factors_frame = tk.LabelFrame(left_panel, text="Credit Factors", font=("Arial", 12, "bold"),
                                    bg=self.colors['pastel_blue'], fg="white", relief=tk.RAISED, bd=3)
        factors_frame.pack(fill=tk.X, pady=10)
        
        self.factors_display = tk.Frame(factors_frame, bg=self.colors['pastel_blue'])
        self.factors_display.pack(fill=tk.X, padx=10, pady=5)
        
        # Right panel - Game controls
        right_panel = tk.Frame(main_frame, bg=self.colors['light_blue'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Month display with rounded styling
        month_frame = tk.Frame(right_panel, bg=self.colors['sage_green'], relief=tk.RAISED, bd=3)
        month_frame.pack(fill=tk.X, pady=5, padx=5, ipadx=10, ipady=5)
        
        tk.Label(month_frame, text="Month:", font=("Arial", 12, "bold"), 
                bg=self.colors['sage_green'], fg="white").pack(side=tk.LEFT)
        self.month_label = tk.Label(month_frame, text="1", font=("Arial", 12, "bold"), 
                                  bg=self.colors['sage_green'], fg="white")
        self.month_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Decision buttons with rounded styling
        decisions_frame = tk.LabelFrame(right_panel, text="This Month's Decisions", font=("Arial", 12, "bold"),
                                       bg=self.colors['pastel_pink'], fg="white", relief=tk.RAISED, bd=3)
        decisions_frame.pack(fill=tk.X, pady=10)
        
        self.decisions_container = tk.Frame(decisions_frame, bg=self.colors['pastel_pink'])
        self.decisions_container.pack(fill=tk.X, padx=10, pady=5)
        
        # Event display with rounded styling
        self.event_frame = tk.LabelFrame(right_panel, text="Current Events", font=("Arial", 12, "bold"),
                                       bg=self.colors['pastel_purple'], fg="white", relief=tk.RAISED, bd=3)
        self.event_frame.pack(fill=tk.X, pady=10)
        
        # Create scrollable text widget for events
        text_frame = tk.Frame(self.event_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.event_text = tk.Text(text_frame, height=4, width=40, wrap=tk.WORD,
                                bg=self.colors['cream'], font=("Arial", 10), relief=tk.FLAT,
                                fg="black")
        event_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.event_text.yview)
        self.event_text.configure(yscrollcommand=event_scrollbar.set)
        
        self.event_text.pack(side="left", fill=tk.BOTH, expand=True)
        event_scrollbar.pack(side="right", fill="y")
        
        # Action buttons with rounded styling
        button_frame = tk.Frame(right_panel, bg=self.colors['light_blue'])
        button_frame.pack(fill=tk.X, pady=10)
        
        self.next_month_btn = tk.Button(button_frame, text="Next Month", 
                                      command=self.next_month, state=tk.DISABLED,
                                      font=("Arial", 12, "bold"), bg='#4682B4',  # Steel blue
                                      fg="black", relief=tk.RAISED, bd=3, padx=15, pady=5)
        self.next_month_btn.pack(side=tk.RIGHT, padx=5)
        
        self.start_btn = tk.Button(button_frame, text="Start Game", 
                                 command=self.start_game,
                                 font=("Arial", 12, "bold"), bg='#228B22',  # Forest green
                                 fg="black", relief=tk.RAISED, bd=3, padx=15, pady=5)
        self.start_btn.pack(side=tk.RIGHT, padx=5)
        
    def draw_credit_score_circle(self):
        self.score_canvas.delete("all")
        
        # Calculate current score
        score = self.calculate_credit_score()
        
        # Draw circle
        center_x, center_y = 100, 100
        radius = 80
        
        # Background circle with pastel styling
        self.score_canvas.create_oval(center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius,
                                    fill=self.colors['light_purple'], outline=self.colors['pastel_purple'], width=3)
        
        # Score arc with pastel colors
        if score >= 700:
            color = self.colors['sage_green']
        elif score >= 600:
            color = self.colors['pastel_pink']
        else:
            color = self.colors['pastel_purple']
            
        # Draw score arc
        start_angle = -90  # Start at top
        extent = (score / 850) * 360  # 850 is max possible score
        
        self.score_canvas.create_arc(center_x - radius, center_y - radius,
                                    center_x + radius, center_y + radius,
                                    start=start_angle, extent=extent,
                                    fill=color, outline="")
        
        # Score text with black styling for better visibility
        self.score_canvas.create_text(center_x, center_y - 10, 
                                    text=str(score), font=("Arial", 24, "bold"), 
                                    fill="black")
        self.score_canvas.create_text(center_x, center_y + 20, 
                                    text="Credit Score", font=("Arial", 10, "bold"),
                                    fill="black")
        
    def calculate_credit_score(self):
        # Convert factors to credit score (300-850 range)
        base_score = 300
        
        # Payment history (35%)
        payment_score = (self.payment_history / 100) * 0.35 * 550
        
        # Credit utilization (30%) - lower is better
        utilization_score = max(0, (100 - self.credit_utilization) / 100) * 0.30 * 550
        
        # Credit age (15%)
        age_score = (self.credit_age / 100) * 0.15 * 550
        
        # Credit mix (10%)
        mix_score = (self.credit_mix / 100) * 0.10 * 550
        
        # Inquiries (10%) - fewer is better
        inquiry_score = max(0, (100 - self.inquiries) / 100) * 0.10 * 550
        
        total_score = base_score + payment_score + utilization_score + age_score + mix_score + inquiry_score
        return min(850, max(300, int(total_score)))
        
    def update_factors_display(self):
        # Clear existing labels
        for widget in self.factors_display.winfo_children():
            widget.destroy()
            
        factors = [
            ("Payment History (35%)", self.payment_history),
            ("Credit Utilization (30%)", self.credit_utilization),
            ("Credit Age (15%)", self.credit_age),
            ("Credit Mix (10%)", self.credit_mix),
            ("Inquiries (10%)", self.inquiries)
        ]
        
        for name, value in factors:
            frame = tk.Frame(self.factors_display, bg=self.colors['pastel_blue'])
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame, text=name, font=("Arial", 10, "bold"), 
                    bg=self.colors['pastel_blue'], fg="white").pack(side=tk.LEFT)
            
            # Progress bar with pastel styling
            progress = tk.Frame(frame, bg=self.colors['light_purple'], height=15, relief=tk.RAISED, bd=2)
            progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            
            # Colored progress with darker colors for better visibility
            if value > 0:
                if value >= 70:
                    color = '#6B8E6B'  # Darker sage green
                elif value >= 40:
                    color = '#D2691E'  # Darker orange
                else:
                    color = '#8B4B8C'  # Darker purple
                progress_width = int((value / 100) * 200)
                tk.Frame(progress, bg=color, width=progress_width, height=15, relief=tk.FLAT).pack(side=tk.LEFT)
            
            tk.Label(frame, text=f"{value}%", font=("Arial", 10, "bold"), 
                    bg=self.colors['pastel_blue'], fg="black").pack(side=tk.RIGHT, padx=(5, 0))
    
    def update_display(self):
        self.draw_credit_score_circle()
        self.update_factors_display()
        self.month_label.config(text=str(self.current_month))
        
    def start_game(self):
        self.start_btn.config(state=tk.DISABLED)
        self.next_month_btn.config(state=tk.NORMAL)
        self.generate_monthly_decisions()
        self.generate_random_event()
        
    def generate_monthly_decisions(self):
        # Clear previous decisions
        for widget in self.decisions_container.winfo_children():
            widget.destroy()
            
        decisions = []
        
        # Always available decisions
        if len(self.credit_cards) == 0:
            decisions.append(("Apply for Credit Card", self.apply_credit_card))
            
        if len(self.credit_cards) > 0:
            decisions.append(("Pay Credit Card Bill", self.pay_credit_card))
            decisions.append(("Make Large Purchase", self.make_large_purchase))
            
        if len(self.loans) == 0 and self.current_month >= 3:
            decisions.append(("Apply for Personal Loan", self.apply_loan))
            
        if len(self.loans) > 0:
            decisions.append(("Pay Loan Payment", self.pay_loan))
            
        # Add random decision
        if random.random() < 0.3:
            decisions.append(("Skip This Month", self.skip_month))
            
        # Create buttons for decisions with black text
        for i, (text, command) in enumerate(decisions):
            btn = tk.Button(self.decisions_container, text=text, 
                          command=lambda cmd=command: self.make_decision(cmd),
                          font=("Arial", 10, "bold"), width=25, 
                          bg='#4682B4', fg="black",  # Black text for better readability
                          relief=tk.RAISED, bd=2, padx=10, pady=3)
            btn.pack(pady=2)
            
    def generate_random_event(self):
        events = [
            ("Unexpected Medical Bill", "You have an unexpected $500 medical bill. How do you handle it?",
             [("Pay with savings", lambda: self.handle_medical_bill("savings")),
              ("Use credit card", lambda: self.handle_medical_bill("credit")),
              ("Apply for medical loan", lambda: self.handle_medical_bill("loan"))]),
              
            ("Credit Card Offer", "You receive a pre-approved credit card offer with 0% APR for 12 months.",
             [("Accept the offer", lambda: self.handle_credit_offer("accept")),
              ("Decline the offer", lambda: self.handle_credit_offer("decline"))]),
              
            ("Job Promotion", "Congratulations! You got a promotion with a 20% salary increase.",
             [("Celebrate!", lambda: self.handle_promotion())]),
              
            ("Credit Limit Increase", "Your credit card company offers to increase your limit by $2000.",
             [("Accept increase", lambda: self.handle_limit_increase("accept")),
              ("Decline increase", lambda: self.handle_limit_increase("decline"))]),
              
            ("Identity Theft Alert", "You notice suspicious activity on your credit report.",
             [("Report immediately", lambda: self.handle_identity_theft("report")),
              ("Wait and see", lambda: self.handle_identity_theft("wait"))])
        ]
        
        if random.random() < 0.4:  # 40% chance of event
            event = random.choice(events)
            self.event_text.delete(1.0, tk.END)
            self.event_text.insert(tk.END, f"🎲 Random Event: {event[0]}\n\n{event[1]}\n\n")
            
            # Add event decision buttons with black text
            for text, command in event[2]:
                btn = tk.Button(self.event_frame, text=text, command=command,
                              font=("Arial", 9, "bold"), width=20,
                              bg='#228B22', fg="black",  # Black text for better readability
                              relief=tk.RAISED, bd=2, padx=5, pady=2)
                btn.pack(pady=1)
        else:
            self.event_text.delete(1.0, tk.END)
            self.event_text.insert(tk.END, "No special events this month. Focus on your regular financial decisions!")
    
    def make_decision(self, decision_func):
        decision_func()
        self.update_display()
        
    def apply_credit_card(self):
        self.inquiry_count += 1
        self.inquiries = min(100, self.inquiries + 20)
        
        # Add credit card
        card = {
            "limit": random.randint(1000, 5000),
            "balance": 0,
            "age": 0
        }
        self.credit_cards.append(card)
        
        self.credit_mix = min(100, self.credit_mix + 15)
        self.credit_age = min(100, self.credit_age + 10)
        
        messagebox.showinfo("Credit Card", f"Approved! Credit limit: ${card['limit']}")
        
    def pay_credit_card(self):
        if not self.credit_cards:
            return
            
        # Pay off some debt
        for card in self.credit_cards:
            if card["balance"] > 0:
                payment = min(card["balance"], random.randint(100, 500))
                card["balance"] -= payment
                self.payment_history = min(100, self.payment_history + 10)
                self.payment_history_list.append(("payment", payment))
                
        messagebox.showinfo("Payment", "Credit card payment made!")
        
    def make_large_purchase(self):
        if not self.credit_cards:
            return
            
        card = random.choice(self.credit_cards)
        purchase = random.randint(200, 1000)
        
        if card["balance"] + purchase <= card["limit"]:
            card["balance"] += purchase
            self.credit_utilization = min(100, self.credit_utilization + 15)
            messagebox.showinfo("Purchase", f"Made purchase of ${purchase}")
        else:
            messagebox.showwarning("Purchase", "Purchase declined - would exceed credit limit!")
            
    def apply_loan(self):
        self.inquiry_count += 1
        self.inquiries = min(100, self.inquiries + 15)
        
        loan = {
            "amount": random.randint(5000, 15000),
            "balance": random.randint(5000, 15000),
            "age": 0
        }
        self.loans.append(loan)
        
        self.credit_mix = min(100, self.credit_mix + 20)
        messagebox.showinfo("Loan", f"Loan approved for ${loan['amount']}")
        
    def pay_loan(self):
        if not self.loans:
            return
            
        for loan in self.loans:
            if loan["balance"] > 0:
                payment = min(loan["balance"], random.randint(200, 800))
                loan["balance"] -= payment
                self.payment_history = min(100, self.payment_history + 15)
                self.payment_history_list.append(("loan_payment", payment))
                
        messagebox.showinfo("Loan Payment", "Loan payment made!")
        
    def skip_month(self):
        messagebox.showinfo("Skip Month", "You chose to skip this month's decisions.")
        
    def handle_medical_bill(self, choice):
        if choice == "savings":
            messagebox.showinfo("Medical Bill", "Paid with savings - no impact on credit")
        elif choice == "credit":
            if self.credit_cards:
                card = random.choice(self.credit_cards)
                card["balance"] += 500
                self.credit_utilization = min(100, self.credit_utilization + 10)
            messagebox.showinfo("Medical Bill", "Added to credit card balance")
        else:  # loan
            self.apply_loan()
            messagebox.showinfo("Medical Bill", "Applied for medical loan")
            
    def handle_credit_offer(self, choice):
        if choice == "accept":
            self.apply_credit_card()
            messagebox.showinfo("Credit Offer", "Accepted new credit card!")
        else:
            messagebox.showinfo("Credit Offer", "Declined the offer - no impact")
            
    def handle_promotion(self):
        # Promotion helps with credit utilization
        self.credit_utilization = max(0, self.credit_utilization - 10)
        messagebox.showinfo("Promotion", "Higher income helps your credit profile!")
        
    def handle_limit_increase(self, choice):
        if choice == "accept" and self.credit_cards:
            card = random.choice(self.credit_cards)
            card["limit"] += 2000
            self.credit_utilization = max(0, self.credit_utilization - 5)
            messagebox.showinfo("Limit Increase", "Credit limit increased!")
        else:
            messagebox.showinfo("Limit Increase", "Declined the increase")
            
    def handle_identity_theft(self, choice):
        if choice == "report":
            messagebox.showinfo("Identity Theft", "Reported immediately - credit protected")
        else:
            self.payment_history = max(0, self.payment_history - 20)
            messagebox.showwarning("Identity Theft", "Delayed reporting hurt your credit!")
    
    def next_month(self):
        self.current_month += 1
        
        # Age existing accounts
        for card in self.credit_cards:
            card["age"] += 1
            if card["age"] > 0:
                self.credit_age = min(100, self.credit_age + 5)
                
        for loan in self.loans:
            loan["age"] += 1
            if loan["age"] > 0:
                self.credit_age = min(100, self.credit_age + 3)
        
        # Decay inquiries over time
        if self.inquiry_count > 0:
            self.inquiry_count = max(0, self.inquiry_count - 1)
            self.inquiries = max(0, self.inquiries - 5)
        
        # Check win/lose conditions
        current_score = self.calculate_credit_score()
        
        if current_score >= self.target_score:
            self.end_game(True)
            return
        elif self.current_month > self.max_months:
            self.end_game(False)
            return
            
        # Generate new decisions and events
        self.generate_monthly_decisions()
        self.generate_random_event()
        self.update_display()
        
    def end_game(self, won):
        self.game_over = True
        self.next_month_btn.config(state=tk.DISABLED)
        
        final_score = self.calculate_credit_score()
        
        if won:
            title = "🎉 Congratulations!"
            message = f"You reached a credit score of {final_score}!\n\n"
        else:
            title = "Game Over"
            message = f"Final credit score: {final_score}\nTarget was {self.target_score}\n\n"
            
        message += "Credit Score Breakdown:\n"
        message += f"• Payment History: {self.payment_history}%\n"
        message += f"• Credit Utilization: {self.credit_utilization}%\n"
        message += f"• Credit Age: {self.credit_age}%\n"
        message += f"• Credit Mix: {self.credit_mix}%\n"
        message += f"• Inquiries: {self.inquiries}%\n\n"
        
        if won:
            message += "Key Success Factors:\n"
            if self.payment_history >= 80:
                message += "✓ Excellent payment history\n"
            if self.credit_utilization <= 30:
                message += "✓ Low credit utilization\n"
            if self.credit_age >= 60:
                message += "✓ Good credit age\n"
            if self.credit_mix >= 50:
                message += "✓ Good credit mix\n"
            if self.inquiries <= 20:
                message += "✓ Low inquiry count\n"
                
            message += "\nAreas for Further Improvement:\n"
        else:
            message += "Areas for Improvement:\n"
            
        # Always show improvement suggestions based on current values
        improvements = []
        
        if self.payment_history < 80:
            improvements.append("• Make payments on time consistently")
        if self.credit_utilization > 30:
            improvements.append("• Keep credit utilization below 30%")
        if self.credit_age < 60:
            improvements.append("• Build longer credit history")
        if self.credit_mix < 50:
            improvements.append("• Diversify credit types (cards, loans)")
        if self.inquiries > 20:
            improvements.append("• Limit credit applications")
            
        if improvements:
            for improvement in improvements:
                message += improvement + "\n"
        else:
            message += "• All credit factors are in excellent range!\n"
                
        messagebox.showinfo(title, message)
        
    def run(self):
        self.root.mainloop()

# Example integration function
def launch_credit_score_game(parent=None):
    """Launch the credit score mini-game as a popup"""
    game = CreditScoreGame(parent)
    game.run()

# Standalone execution
if __name__ == "__main__":
    launch_credit_score_game()
