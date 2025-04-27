import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def funkcja(x):
    return np.sin(x)  # przykładowa funkcja

def divided_differences(x, y):
    n = len(x)
    coef = y.copy()
    for j in range(1, n):
        for i in range(n-1, j-1, -1):
            coef[i] = (coef[i] - coef[i-1]) / (x[i] - x[i-j])
    return coef

def newton_polynomial(x_nodes, coef, x):
    n = len(coef) - 1
    p = coef[n]
    for k in range(1, n+1):
        p = coef[n-k] + (x - x_nodes[n-k]) * p
    return p

def interpolate(x_nodes, y_nodes, x_eval):
    coef = divided_differences(x_nodes, y_nodes)
    return newton_polynomial(x_nodes, coef, x_eval)

def generate_plot():
    global canvas
    try:
        nodes = list(map(float, entry_nodes.get().split()))
        x_nodes = np.array(nodes)
        y_nodes = funkcja(x_nodes)

        x_plot = np.linspace(min(x_nodes)-1, max(x_nodes)+1, 400)
        y_true = funkcja(x_plot)
        y_interp = interpolate(x_nodes, y_nodes, x_plot)

        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(x_plot, y_true, label="Funkcja prawdziwa", color='blue')
        ax.plot(x_plot, y_interp, label="Wielomian interpolacyjny", linestyle='--', color='red')
        ax.plot(x_nodes, y_nodes, 'ko', label="Węzły interpolacyjne")
        ax.set_title("Interpolacja Newtona dla nierównych odstępów")
        ax.grid(True)
        ax.legend()

        # Jeśli istnieje stary canvas - usuń
        if canvas:
            canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        print("Błąd:", e)

# --- GUI ---
root = tk.Tk()
root.title("Interpolacja Newtona")
root.geometry("900x700")

frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

frame_plot = tk.Frame(root)
frame_plot.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

label_nodes = tk.Label(frame_controls, text="Podaj węzły (oddzielone spacją):")
label_nodes.pack(side=tk.LEFT)

entry_nodes = tk.Entry(frame_controls, width=40)
entry_nodes.pack(side=tk.LEFT, padx=5)

button_plot = tk.Button(frame_controls, text="Interpoluj i narysuj", command=generate_plot)
button_plot.pack(side=tk.LEFT, padx=5)

canvas = None  # globalny canvas na wykres

root.mainloop()
