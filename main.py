import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
import threading
import winsound
import random

# ===== БАЗОВЫЙ ТАЙМЕР =====
class BaseTimer:
    def __init__(self, label, font=("Arial", 16, "bold")):
        self.label = label
        self.font = font
        self.seconds = 0
        self.running = False

    def start(self):
        self.running = True
        self.tick_loop()

    def stop(self):
        self.running = False

    def tick_loop(self):
        if not self.running:
            return
        self.tick()
        self.update_display()
        self.label.after(1000, self.tick_loop)

    def tick(self):
        pass

    def update_display(self):
        pass

    def to_hhmmss(self, sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02}:{m:02}:{s:02}"


# ===== СТАНДАРТНЫЙ ТАЙМЕР =====
class StandardTimer(BaseTimer):
    def tick(self):
        self.seconds += 1

    def update_display(self):
        color = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
        self.label.config(
            text=f"⏳ Standard Timer: {self.to_hhmmss(self.seconds)}",
            font=self.font,
            fg=color,
            bg="#1e1e1e",
            relief="ridge",
            bd=4,
            padx=10,
            pady=5
        )


# ===== ИНТЕРВАЛЬНЫЙ ТАЙМЕР =====
class IntervalTimer(BaseTimer):
    def __init__(self, label, interval, font=("Arial", 16, "bold")):
        super().__init__(label, font)
        self.interval = interval

    def tick(self):
        self.seconds += 1
        if self.seconds % self.interval == 0:
            threading.Thread(target=lambda: winsound.Beep(1000, 400), daemon=True).start()

    def update_display(self):
        self.label.config(
            text=f"🔁 Interval Timer ({self.interval}s): {self.seconds} sec",
            font=self.font,
            fg="#ffd700",
            bg="#2b2b2b",
            relief="groove",
            bd=4,
            padx=10,
            pady=5
        )


# ===== ЦЕЛЕВОЙ ТАЙМЕР =====
class TargetTimer(BaseTimer):
    def __init__(self, label, target_hhmm, font=("Arial", 16, "bold")):
        super().__init__(label, font)
        self.target_hhmm = target_hhmm
        self.target_seconds = self.compute_seconds_until(target_hhmm)

    def compute_seconds_until(self, hhmm):
        hh = hhmm // 100
        mm = hhmm % 100
        now = datetime.now()
        target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return int((target - now).total_seconds())

    def tick(self):
        if self.target_seconds > 0:
            self.target_seconds -= 1
            if self.target_seconds == 0:
                threading.Thread(target=lambda: winsound.Beep(1500, 800), daemon=True).start()
                messagebox.showinfo("Target Timer", "🎯 Целевое время наступило!")

    def update_display(self):
        self.label.config(
            text=f"🎯 Target Timer {self.target_hhmm:04}: {self.to_hhmmss(self.target_seconds)}",
            font=self.font,
            fg="#ff4500",
            bg="#1c1c1c",
            relief="solid",
            bd=4,
            padx=10,
            pady=5
        )


# ===== ПРИЛОЖЕНИЕ =====
class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("450x400")
        self.root.configure(bg="#121212")
        self.root.title("🕒 Modern Timer App")

        font = ("Arial", 18, "bold")

        target_time = simpledialog.askinteger("Target Timer", "Введите целевое время (HHMM):", parent=self.root)
        if target_time is None:
            self.root.destroy()
            return

        # Метки таймеров с рамками
        self.standard_label = tk.Label(root, text="", font=font)
        self.interval_label = tk.Label(root, text="", font=font)
        self.target_label = tk.Label(root, text="", font=font)
        self.standard_label.pack(pady=15, fill="x", padx=20)
        self.interval_label.pack(pady=15, fill="x", padx=20)
        self.target_label.pack(pady=15, fill="x", padx=20)

        # Таймеры
        self.standard_timer = StandardTimer(self.standard_label, font)
        self.interval_timer = IntervalTimer(self.interval_label, 5, font)
        self.target_timer = TargetTimer(self.target_label, target_time, font)

        # Кнопки с современным оформлением
        btn_style = {"font": ("Arial", 12, "bold"), "bd": 0, "fg": "#fff", "width": 15, "height": 2}

        tk.Button(root, text="▶ Start Standard", command=self.standard_timer.start,
                  bg="#00bfff", **btn_style).pack(pady=5)
        tk.Button(root, text="⏹ Stop Standard", command=self.standard_timer.stop,
                  bg="#ff6347", **btn_style).pack(pady=5)

        tk.Button(root, text="▶ Start Interval", command=self.interval_timer.start,
                  bg="#00bfff", **btn_style).pack(pady=5)
        tk.Button(root, text="⏹ Stop Interval", command=self.interval_timer.stop,
                  bg="#ff6347", **btn_style).pack(pady=5)

        tk.Button(root, text="▶ Start Target", command=self.target_timer.start,
                  bg="#00bfff", **btn_style).pack(pady=5)
        tk.Button(root, text="⏹ Stop Target", command=self.target_timer.stop,
                  bg="#ff6347", **btn_style).pack(pady=5)


# ===== ЗАПУСК =====
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
