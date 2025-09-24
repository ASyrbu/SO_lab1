import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
import threading
import winsound
import random

# ===== БАЗОВЫЙ ТАЙМЕР =====
class BaseTimer:
    def __init__(self, label, font=("Helvetica", 16)):
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
        self.label.after(1000, self.tick_loop)  # безопасный вызов в главном потоке

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
        self.label.config(text=f"⏳ Standard: {self.to_hhmmss(self.seconds)}", font=self.font, fg=color)


# ===== ИНТЕРВАЛЬНЫЙ ТАЙМЕР =====
class IntervalTimer(BaseTimer):
    def __init__(self, label, interval, font=("Helvetica", 16)):
        super().__init__(label, font)
        self.interval = interval

    def tick(self):
        self.seconds += 1
        if self.seconds % self.interval == 0:
            # звук в отдельном потоке
            threading.Thread(target=lambda: winsound.Beep(1000, 400), daemon=True).start()

    def update_display(self):
        self.label.config(text=f"🔁 Interval ({self.interval}s): {self.seconds} sec", font=self.font)


# ===== ЦЕЛЕВОЙ ТАЙМЕР =====
class TargetTimer(BaseTimer):
    def __init__(self, label, target_hhmm, font=("Helvetica", 16)):
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
        self.label.config(text=f"🎯 Target {self.target_hhmm:04}: {self.to_hhmmss(self.target_seconds)}", font=self.font)


# ===== ПРИЛОЖЕНИЕ =====
class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x300")
        self.root.configure(bg="#20232a")
        font = ("Helvetica", 18, "bold")

        target_time = simpledialog.askinteger("Target Timer", "Введите целевое время (HHMM):", parent=self.root)
        if target_time is None:
            self.root.destroy()
            return

        # Метки таймеров
        self.standard_label = tk.Label(root, text="", bg="#20232a", font=font)
        self.interval_label = tk.Label(root, text="", bg="#20232a", fg="#21a366", font=font)
        self.target_label = tk.Label(root, text="", bg="#20232a", fg="#f54291", font=font)
        self.standard_label.pack(pady=10)
        self.interval_label.pack(pady=10)
        self.target_label.pack(pady=10)

        # Таймеры
        self.standard_timer = StandardTimer(self.standard_label, font)
        self.interval_timer = IntervalTimer(self.interval_label, 5, font)
        self.target_timer = TargetTimer(self.target_label, target_time, font)

        # Кнопки управления
        tk.Button(root, text="Start Standard", command=self.standard_timer.start,
                  bg="#3498db", fg="#fff").pack(pady=2)
        tk.Button(root, text="Stop Standard", command=self.standard_timer.stop,
                  bg="#e74c3c", fg="#fff").pack(pady=2)

        tk.Button(root, text="Start Interval", command=self.interval_timer.start,
                  bg="#3498db", fg="#fff").pack(pady=2)
        tk.Button(root, text="Stop Interval", command=self.interval_timer.stop,
                  bg="#e74c3c", fg="#fff").pack(pady=2)

        tk.Button(root, text="Start Target", command=self.target_timer.start,
                  bg="#3498db", fg="#fff").pack(pady=2)
        tk.Button(root, text="Stop Target", command=self.target_timer.stop,
                  bg="#e74c3c", fg="#fff").pack(pady=2)


# ===== ЗАПУСК =====
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
