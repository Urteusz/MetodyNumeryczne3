import tkinter as tk
from tkinter import messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --- ZMIENNE GLOBALNE ---
function_type = "liniowa"
nodes_type = "równoodległe"
a_value = -5.0
b_value = 5.0
n_nodes = 5
custom_nodes = []

# --- FUNKCJE ---

def get_function(x, func_type=None):
    if func_type is None:
        func_type = function_type

    if func_type == "liniowa":
        return 0.5 * x + 1
    elif func_type == "moduł |x|":
        return np.abs(x)
    elif func_type == "wielomian":
        return x ** 3 - 2 * x ** 2 + 3 * x - 1
    elif func_type == "trygonometryczna":
        return np.sin(x) + 0.5 * np.cos(2 * x)
    elif func_type == "złożenie":
        return np.sin(x ** 2) * np.exp(-0.1 * np.abs(x))
    else:
        return x

def generate_nodes():
    global custom_nodes, a_value, b_value, n_nodes, nodes_type
    a = a_value
    b = b_value
    n = n_nodes

    if nodes_type == "równoodległe":
        return np.linspace(a, b, n)
    elif nodes_type == "Czebyszewa":
        k = np.arange(1, n + 1)
        nodes = 0.5 * (a + b) + 0.5 * (b - a) * np.cos((2 * k - 1) * np.pi / (2 * n))
        return nodes
    elif nodes_type == "własne":
        if len(custom_nodes) < 2:
            messagebox.showerror("Błąd", "Brak zdefiniowanych węzłów własnych")
            return np.linspace(a, b, n)
        return np.array(custom_nodes)

def newton_coefficients(x, y):
    n = len(x)
    coefs = np.copy(y)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coefs[i] = (coefs[i] - coefs[i - 1]) / (x[i] - x[i - j])
    return coefs

def newton_interpolate(x_points, coefs, x_new):
    n = len(x_points)
    result = coefs[n - 1]
    for i in range(n - 2, -1, -1):
        result = result * (x_new - x_points[i]) + coefs[i]
    return result

def load_nodes():
    if nodes_type != "własne":
        messagebox.showinfo("Info", "Wczytywanie węzłów dostępne tylko dla opcji 'własne'")
        return

    def save_nodes():
        global n_nodes
        nonlocal text_widget, input_dialog
        try:
            nodes_text = text_widget.get("1.0", tk.END).strip()
            loaded_nodes = [float(x) for x in nodes_text.split()]
            global custom_nodes
            custom_nodes = loaded_nodes
            n_nodes = len(custom_nodes)
            n_entry.delete(0, tk.END)
            n_entry.insert(0, str(n_nodes))
            messagebox.showinfo("Info", f"Wczytano {len(custom_nodes)} węzłów")
            input_dialog.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowy format danych. Wprowadź liczby oddzielone spacją.")

    input_dialog = tk.Toplevel(root)
    input_dialog.title("Wprowadź węzły")
    input_dialog.geometry("400x300")

    tk.Label(input_dialog, text="Wprowadź węzły (wartości x oddzielone spacją):").pack(pady=10)

    text_widget = tk.Text(input_dialog, height=10, width=40)
    text_widget.pack(pady=10)

    tk.Button(input_dialog, text="Zapisz", command=save_nodes).pack(pady=10)

def interpolate():
    try:
        x_nodes = generate_nodes()
        y_nodes = get_function(x_nodes)

        coefs = newton_coefficients(x_nodes, y_nodes)

        a, b = a_value, b_value
        x = np.linspace(a, b, 1000)
        y_original = get_function(x)

        y_interp = np.array([newton_interpolate(x_nodes, coefs, xi) for xi in x])

        plot_results(x, y_original, x_nodes, y_nodes, x, y_interp)

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas interpolacji: {str(e)}")

def plot_results(x_orig, y_orig, x_nodes, y_nodes, x_interp, y_interp):
    ax.clear()
    ax.plot(x_orig, y_orig, 'b-', label='Funkcja oryginalna')
    ax.plot(x_interp, y_interp, 'r--', label='Wielomian interpolacyjny')
    ax.plot(x_nodes, y_nodes, 'go', label='Węzły interpolacji')
    name = ""
    if function_type == "liniowa":
        name = r"$= \, 0.5x + 1$"
    elif function_type == "wielomian":
        name = r"$= \, x^3 - 2x^2 + 3x - 1$"
    elif function_type == "trygonometryczna":
        name = r"$= \, \sin(x) + 0.5\cos(2x)$"
    elif function_type == "złożenie":
        name = r"$= \, \sin(x^2) \times \exp\left(-0.1 |x|\right)$"

    ax.set_title(
        fr'Interpolacja Newtona - {function_type.capitalize()} {name}, liczba węzłów: {len(x_nodes)}'
    )
    ax.legend()
    ax.grid(True)
    canvas.draw()


# --- FUNKCJE HANDLERÓW RADIOBUTTONÓW I ENTRY ---

def set_function_type():
    global function_type
    function_type = func_var.get()

def set_nodes_type():
    global nodes_type
    nodes_type = nodes_var.get()

def update_a_value(*args):
    global a_value
    try:
        a_value = float(a_entry.get())
    except ValueError:
        pass

def update_b_value(*args):
    global b_value
    try:
        b_value = float(b_entry.get())
    except ValueError:
        pass


def update_n_nodes(*args):
    global n_nodes
    try:
        n_nodes = int(n_entry.get())
    except ValueError:
        pass

# --- GŁÓWNA FUNKCJA ---

def main():
    global root, canvas, ax, func_var, nodes_var, a_entry, b_entry, n_entry

    root = tk.Tk()
    root.title("Interpolacja Newtona dla nierównych odstępów")
    root.geometry("1000x800")

    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Funkcja
    tk.Label(control_frame, text="Funkcja:").grid(row=0, column=0, sticky=tk.W)
    func_var = tk.StringVar(value="liniowa")
    functions = ["liniowa", "moduł |x|", "wielomian", "trygonometryczna", "złożenie"]
    for i, func in enumerate(functions):
        tk.Radiobutton(control_frame, text=func, variable=func_var, value=func, command=set_function_type).grid(row=0, column=i+1, sticky=tk.W)

    # Typ węzłów
    tk.Label(control_frame, text="Typ węzłów:").grid(row=1, column=0, sticky=tk.W)
    nodes_var = tk.StringVar(value="równoodległe")
    nodes_types = ["równoodległe", "Czebyszewa", "własne"]
    for i, ntype in enumerate(nodes_types):
        tk.Radiobutton(control_frame, text=ntype, variable=nodes_var, value=ntype, command=set_nodes_type).grid(row=1, column=i+1, sticky=tk.W)

    # Przedział i liczba węzłów
    tk.Label(control_frame, text="Początek przedziału (a):").grid(row=2, column=0, sticky=tk.W)
    a_entry = tk.Entry(control_frame, width=8)
    a_entry.insert(0, str(a_value))
    a_entry.grid(row=2, column=1, sticky=tk.W)
    a_entry.bind("<KeyRelease>", update_a_value)

    tk.Label(control_frame, text="Koniec przedziału (b):").grid(row=3, column=0, sticky=tk.W)
    b_entry = tk.Entry(control_frame, width=8)
    b_entry.insert(0, str(b_value))
    b_entry.grid(row=3, column=1, sticky=tk.W)
    b_entry.bind("<KeyRelease>", update_b_value)

    tk.Label(control_frame, text="Liczba węzłów:").grid(row=4, column=0, sticky=tk.W)
    n_entry = tk.Entry(control_frame, width=8)
    n_entry.insert(0, str(n_nodes))
    n_entry.grid(row=4, column=1, sticky=tk.W)
    n_entry.bind("<KeyRelease>", update_n_nodes)

    # Przyciski
    tk.Button(control_frame, text="Wczytaj węzły", command=load_nodes).grid(row=2, column=2, sticky=tk.W)
    tk.Button(control_frame, text="Interpoluj", command=interpolate).grid(row=3, column=2, sticky=tk.W)

    # Wykres
    plot_frame = tk.Frame(root)
    plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    root.mainloop()

if __name__ == "__main__":
    main()
