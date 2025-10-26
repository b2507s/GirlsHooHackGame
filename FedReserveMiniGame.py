"""Federal Reserve Mini-Game

Single-player popup mini-game that lets a player adjust the federal
funds rate to try to stabilize the economy. The UI uses tkinter and
is intentionally self-contained so it can be integrated into a larger
game.

Controls & mechanics:
- Start button opens the simulation loop
- Slider adjusts the federal funds rate (in percent)
- Dashboard shows Inflation (%), Unemployment (%), and GDP (index)
- Alerts appear when a metric "tanks"
- Exit button in top-right closes the popup

Run: python3 minigame.py

This file is dependency-free (uses stdlib tkinter). The simulation is
intentionally simple / pedagogical rather than an accurate macro model.
"""

import tkinter as tk
from tkinter import ttk, font
import random
import math


class FedMiniGame:
	def __init__(self, master):
		self.master = master
		master.title("Fed Mini-Game")

		# Root colors and style
		self.bg = "#F6F2F8"  # off-white
		self.panel_color = "#fff"  # white panel
		self.pastel_pink = "#FFD6E0"
		self.sage = "#C7E7D6"
		self.light_blue = "#DCEFFD"
		self.accent = "#8FB8C7"

		master.configure(bg=self.bg)

		# Create main popup frame (centered)
		self.popup = tk.Toplevel(master)
		self.popup.title("Stabilize the Economy")
		self.popup.configure(bg=self.bg)
		self.popup.geometry("760x460")
		self.popup.resizable(False, False)

		# Make a rounded-looking panel using a Canvas
		self.canvas = tk.Canvas(self.popup, bg=self.bg, highlightthickness=0)
		self.canvas.pack(fill=tk.BOTH, expand=True)

		# Draw rounded rectangle panel
		self._draw_panel()

		# Fonts
		self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
		self.body_font = font.Font(family="Helvetica", size=11)
		self.metric_font = font.Font(family="Helvetica", size=12, weight="bold")
		self.small_font = font.Font(family="Helvetica", size=9)

		# Title and exit
		self.canvas.create_text(40, 40, anchor="w", text="Stabilize the Economy",
								font=self.title_font, fill="#2F3B4A")

		# Exit button top-right
		exit_btn = tk.Button(self.popup, text="✕", command=self._exit,
							 bd=0, bg=self.panel_color, fg="#5A5A5A",
							 activebackground="#F2F2F2")
		self.canvas.create_window(720, 28, anchor="ne", window=exit_btn)

		# Start button (center)
		self.start_btn = tk.Button(self.popup, text="Start",
								   command=self.start_game,
								   bg=self.sage, fg="#1F3B2E",
								   font=self.body_font, bd=0,
								   padx=16, pady=8)
		self.canvas.create_window(380, 120, window=self.start_btn)

		# Placeholder for game content (added after Start)
		self.controls_window = None

		# Simulation state (defaults)
		self.running = False
		self.rate = 2.5  # current fed funds rate
		self.neutral_rate = 2.5

		# Economic variables
		self.inflation = 2.0  # %
		self.unemployment = 5.0  # %
		self.gdp = 100.0  # index (100 baseline)

		# Alert widget
		self.alert_var = tk.StringVar(value="")

		# Tick time (ms)
		self.tick_ms = 250

	def _draw_panel(self):
		w, h = 760, 460
		r = 18  # corner radius
		x0, y0, x1, y1 = 12, 12, w - 12, h - 12
		# Create rounded rectangle manually
		self.canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill=self.panel_color, outline="")
		self.canvas.create_rectangle(x0, y0 + r, x1, y1 - r, fill=self.panel_color, outline="")
		# four arcs
		self.canvas.create_arc(x0, y0, x0 + 2 * r, y0 + 2 * r, start=90, extent=90, fill=self.panel_color, outline="")
		self.canvas.create_arc(x1 - 2 * r, y0, x1, y0 + 2 * r, start=0, extent=90, fill=self.panel_color, outline="")
		self.canvas.create_arc(x0, y1 - 2 * r, x0 + 2 * r, y1, start=180, extent=90, fill=self.panel_color, outline="")
		self.canvas.create_arc(x1 - 2 * r, y1 - 2 * r, x1, y1, start=270, extent=90, fill=self.panel_color, outline="")

	def start_game(self):
		if self.running:
			return
		self.running = True
		# remove the start button so it disappears after being pressed
		try:
			self.start_btn.destroy()
		except Exception:
			pass
		self._build_controls()
		self._tick()  # start the simulation loop

	def _build_controls(self):
		# Left: slider & instructions
		frame_left = tk.Frame(self.popup, bg=self.panel_color, width=320)
		frame_left.configure(padx=14, pady=12)
		# move left frame slightly right so the layout is better centered
		self.canvas.create_window(200, 240, window=frame_left)


		# Interest rate label + slider row (use tk.Label so background can be set)
		tk.Label(frame_left, text="Interest Rate", font=self.metric_font, background=self.panel_color, foreground="#2F3B4A").pack(anchor="w")
		self.rate_var = tk.DoubleVar(value=self.rate)
		slider_row = tk.Frame(frame_left, bg=self.panel_color)
		slider_row.pack(fill=tk.X, pady=(6, 8))
		slider = ttk.Scale(slider_row, from_=-1.0, to=10.0, orient=tk.HORIZONTAL,
			   length=260, variable=self.rate_var, command=self._on_slider)
		slider.pack(side=tk.LEFT)
		# numeric display of current rate
		self.rate_display_label = tk.Label(slider_row, text=f"{self.rate:.2f}%", font=self.body_font, bg=self.panel_color, fg="#333")
		self.rate_display_label.pack(side=tk.LEFT, padx=(8, 0))

		# short instruction
		tk.Label(frame_left, text="Adjust the rate to try to keep inflation low\nand unemployment manageable.",
			   font=self.small_font, background=self.panel_color, justify=tk.LEFT, wraplength=300, foreground="#444").pack()

		# Right: dashboard
		frame_right = tk.Frame(self.popup, bg=self.panel_color, width=360)
		frame_right.configure(padx=12, pady=12)
		# nudge right frame a bit left so it centers with the left frame
		self.canvas.create_window(520, 240, window=frame_right)

		# Metric rows
		# Add metrics with readable min/max labels
		self._create_metric_row(frame_right, "Inflation", "inflation", min_label="0%", max_label="12%")
		self._create_metric_row(frame_right, "Unemployment", "unemployment", min_label="0%", max_label="40%")
		self._create_metric_row(frame_right, "GDP Index", "gdp", min_label="50", max_label="200")

		# Alert area at bottom
		alert_frame = tk.Frame(self.popup, bg=self.panel_color)
		self.canvas.create_window(380, 420, window=alert_frame)
		self.alert_label = tk.Label(alert_frame, textvariable=self.alert_var,
									font=self.small_font, bg=self.panel_color,
									fg="#7A1F1F")
		self.alert_label.pack()

	def _create_metric_row(self, parent, label_text, attr_name, min_label=None, max_label=None):
		row = tk.Frame(parent, bg=self.panel_color)
		row.pack(fill=tk.X, pady=8)
		# Metric title (make bold and visible)
		tk.Label(row, text=label_text, font=self.metric_font, bg=self.panel_color, fg="#2F3B4A").pack(anchor="w")
		# value label
		val = tk.Label(row, text="", font=self.body_font, bg=self.panel_color)
		val.pack(anchor="w")
		setattr(self, f"{attr_name}_label", val)


		# small bar (wider and centered) - background matches panel (white)
		bar_canvas = tk.Canvas(row, width=320, height=14, bg=self.panel_color, highlightthickness=0)
		bar_canvas.pack(pady=6, anchor="center")
		setattr(self, f"{attr_name}_bar", bar_canvas)

		# optional min/max labels under the bar for clarity
		if min_label is not None or max_label is not None:
			label_row = tk.Frame(row, bg=self.panel_color)
			label_row.pack(fill=tk.X, padx=6)
			left = tk.Label(label_row, text=(min_label or ""), font=self.small_font, bg=self.panel_color, fg="#555")
			right = tk.Label(label_row, text=(max_label or ""), font=self.small_font, bg=self.panel_color, fg="#555")
			left.pack(side=tk.LEFT)
			right.pack(side=tk.RIGHT)

	def _on_slider(self, _=None):
		self.rate = float(self.rate_var.get())
		# update numeric display immediately
		try:
			self.rate_display_label.configure(text=f"{self.rate:.2f}%")
		except Exception:
			pass

	def _tick(self):
		if not self.running:
			return

		# Update based on current rate vs neutral
		r = self.rate
		neutral = self.neutral_rate
		influence = neutral - r  # positive when rate below neutral (stimulative)

		# Inflation: stimulative policy increases inflation slowly
		# noise adds small randomness
		self.inflation += (0.03 * -influence) + random.uniform(-0.05, 0.05)

		# Unemployment: stimulative policy lowers unemployment, but with lag
		self.unemployment += (0.04 * influence) + random.uniform(-0.03, 0.03)

		# GDP: if stimulative (rate low), GDP grows; if restrictive, GDP growth slows
		gdp_change = (0.12 * -influence) + random.uniform(-0.08, 0.08)
		# Apply a small decay so GDP doesn't explode
		self.gdp += gdp_change

		# Clamp sensible ranges
		self.inflation = max(-1.0, min(20.0, self.inflation))
		self.unemployment = max(0.0, min(40.0, self.unemployment))
		self.gdp = max(50.0, min(200.0, self.gdp))

		# Update UI
		self._update_dashboard()

		# Schedule next tick
		self.popup.after(self.tick_ms, self._tick)

	def _update_dashboard(self):
		# Update numeric labels
		self.inflation_label.configure(text=f"{self.inflation:.2f}%")
		self.unemployment_label.configure(text=f"{self.unemployment:.2f}%")
		self.gdp_label.configure(text=f"{self.gdp:.2f}")

		# Update bars (normalized values for visuals)
		self._draw_bar(self.inflation_bar, self.inflation, 0, 12, bad_is_high=True)
		self._draw_bar(self.unemployment_bar, self.unemployment, 0, 15, bad_is_high=True)
		# For GDP: visualize distance from 100 baseline (good higher)
		self._draw_bar(self.gdp_bar, self.gdp - 100.0, -30, 50, bad_is_high=False)

		# Alerts when things 'tank'
		alerts = []
		if self.inflation > 8.0:
			alerts.append("High inflation — prices rising rapidly!")
		if self.unemployment > 12.0:
			alerts.append("Unemployment spike — too many people out of work!")
		if self.gdp < 90.0:
			alerts.append("GDP falling — economy shrinking!")

		if alerts:
			self.alert_var.set(" ⚠ " + "   •   ".join(alerts))
			self.alert_label.configure(fg="#8B1E1E")
		else:
			self.alert_var.set("")

	def _draw_bar(self, canvas, value, vmin, vmax, bad_is_high=True):
		# Draw background
		canvas.delete("all")
		w = int(canvas['width'])
		h = int(canvas['height'])
		canvas.create_rectangle(0, 0, w, h, fill="#F4F6F8", outline="")

		# Normalize value to [0,1]
		# If bad_is_high=True, larger values are worse (e.g. inflation)
		frac = (value - vmin) / (vmax - vmin)
		frac = max(0.0, min(1.0, frac))

		fill_w = int(frac * w)

		# Color depending on value
		if bad_is_high:
			# green at low, yellow mid, pink at high
			color = self._interpolate_color(self.sage, self.pastel_pink, frac)
		else:
			# For GDP: green is high, pink is low
			color = self._interpolate_color(self.pastel_pink, self.sage, frac)

		canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")

	def _interpolate_color(self, c1, c2, t):
		# Colors are hex like #RRGGBB; interpolate channels
		t = max(0.0, min(1.0, t))
		c1 = c1.lstrip('#')
		c2 = c2.lstrip('#')
		r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
		r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
		r = int(r1 + (r2 - r1) * t)
		g = int(g1 + (g2 - g1) * t)
		b = int(b1 + (b2 - b1) * t)
		return f"#{r:02x}{g:02x}{b:02x}"

	def _exit(self):
		self.running = False
		try:
			self.popup.destroy()
		except Exception:
			pass


def main():
	root = tk.Tk()
	root.withdraw()  # hide main window; we use a popup Toplevel
	game = FedMiniGame(root)
	# Center the popup on screen (simple approach)
	game.popup.update_idletasks()
	w = game.popup.winfo_width()
	h = game.popup.winfo_height()
	ws = game.popup.winfo_screenwidth()
	hs = game.popup.winfo_screenheight()
	x = (ws // 2) - (w // 2)
	y = (hs // 2) - (h // 2)
	game.popup.geometry(f"{w}x{h}+{x}+{y}")
	root.mainloop()


if __name__ == "__main__":
	main()

