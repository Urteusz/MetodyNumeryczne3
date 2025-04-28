import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button, TextBox
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class NewtonInterpolation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interpolacja Newtona dla nierównych odstępów")
        self.root.geometry("1000x800")

        # Parametry
        self.function_type = tk.StringVar(value="liniowa")
        self.nodes_type = tk.StringVar(value="równoodległe")
        self.a_value = tk.DoubleVar(value=-5.0)
        self.b_value = tk.DoubleVar(value=5.0)
        self.n_nodes = tk.IntVar(value=5)
        self.custom_nodes = []

        # Tworzenie interfejsu
        self.create_widgets()

        # Wartości funkcji
        self.x_values = None
        self.y_values = None
        self.x_interpolated = None
        self.y_interpolated = None

    def create_widgets(self):
        # Ramka z kontrolkami
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Wybór funkcji
        tk.Label(control_frame, text="Funkcja:").grid(row=0, column=0, sticky=tk.W)
        functions = ["liniowa", "moduł |x|", "wielomian", "trygonometryczna", "złożenie"]
        for i, func in enumerate(functions):
            tk.Radiobutton(control_frame, text=func, variable=self.function_type,
                           value=func).grid(row=0, column=i + 1, sticky=tk.W)

        # Wybór typu węzłów
        tk.Label(control_frame, text="Typ węzłów:").grid(row=1, column=0, sticky=tk.W)
        nodes_types = ["równoodległe", "Czebyszewa", "własne"]
        for i, ntype in enumerate(nodes_types):
            tk.Radiobutton(control_frame, text=ntype, variable=self.nodes_type,
                           value=ntype).grid(row=1, column=i + 1, sticky=tk.W)

        # Parametry przedziału
        tk.Label(control_frame, text="Początek przedziału (a):").grid(row=2, column=0, sticky=tk.W)
        tk.Entry(control_frame, textvariable=self.a_value, width=8).grid(row=2, column=1, sticky=tk.W)

        tk.Label(control_frame, text="Koniec przedziału (b):").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(control_frame, textvariable=self.b_value, width=8).grid(row=3, column=1, sticky=tk.W)

        tk.Label(control_frame, text="Liczba węzłów:").grid(row=4, column=0, sticky=tk.W)
        tk.Entry(control_frame, textvariable=self.n_nodes, width=8).grid(row=4, column=1, sticky=tk.W)

        # Przyciski
        tk.Button(control_frame, text="Wczytaj węzły", command=self.load_nodes).grid(row=2, column=2, sticky=tk.W)
        tk.Button(control_frame, text="Interpoluj", command=self.interpolate).grid(row=3, column=2, sticky=tk.W)

        # Ramka na wykres
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tworzenie wykresu
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def load_nodes(self):
        if self.nodes_type.get() != "własne":
            messagebox.showinfo("Info", "Wczytywanie węzłów dostępne tylko dla opcji 'własne'")
            return

        # Okno dialogowe do wczytania węzłów
        input_dialog = tk.Toplevel(self.root)
        input_dialog.title("Wprowadź węzły")
        input_dialog.geometry("400x300")

        tk.Label(input_dialog, text="Wprowadź węzły (wartości x oddzielone spacją):").pack(pady=10)

        text_widget = tk.Text(input_dialog, height=10, width=40)
        text_widget.pack(pady=10)

        def save_nodes():
            try:
                nodes_text = text_widget.get("1.0", tk.END).strip()
                self.custom_nodes = [float(x) for x in nodes_text.split()]
                messagebox.showinfo("Info", f"Wczytano {len(self.custom_nodes)} węzłów")
                input_dialog.destroy()
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format danych. Wprowadź liczby oddzielone spacją.")

        tk.Button(input_dialog, text="Zapisz", command=save_nodes).pack(pady=10)

    def get_function(self, x, func_type=None):
        if func_type is None:
            func_type = self.function_type.get()

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
            return x  # domyślnie tożsamość

    def generate_nodes(self):
        a = self.a_value.get()
        b = self.b_value.get()
        n = self.n_nodes.get()
        nodes_type = self.nodes_type.get()

        if nodes_type == "równoodległe":
            return np.linspace(a, b, n)
        elif nodes_type == "Czebyszewa":
            # Węzły Czebyszewa w przedziale [a,b]
            k = np.arange(1, n + 1)
            nodes = 0.5 * (a + b) + 0.5 * (b - a) * np.cos((2 * k - 1) * np.pi / (2 * n))
            return nodes
        elif nodes_type == "własne":
            if len(self.custom_nodes) < 2:
                messagebox.showerror("Błąd", "Brak zdefiniowanych węzłów własnych")
                return np.linspace(a, b, n)
            return np.array(self.custom_nodes)

    def newton_coefficients(self, x, y):
        """Oblicza współczynniki wielomianu Newtona."""
        n = len(x)
        coefs = np.copy(y)

        for j in range(1, n):
            for i in range(n - 1, j - 1, -1):
                coefs[i] = (coefs[i] - coefs[i - 1]) / (x[i] - x[i - j])

        return coefs

    def newton_interpolate(self, x_points, coefs, x_new):
        """Interpolacja metodą Newtona."""
        n = len(x_points)
        result = coefs[n - 1]

        for i in range(n - 2, -1, -1):
            result = result * (x_new - x_points[i]) + coefs[i]

        return result

    def interpolate(self):
        try:
            # Generowanie węzłów
            x_nodes = self.generate_nodes()
            y_nodes = self.get_function(x_nodes)

            # Współczynniki wielomianu Newtona
            coefs = self.newton_coefficients(x_nodes, y_nodes)

            # Generowanie punktów do wykresu
            a, b = self.a_value.get(), self.b_value.get()
            x = np.linspace(a, b, 1000)
            y_original = self.get_function(x)

            # Interpolacja
            y_interp = np.array([self.newton_interpolate(x_nodes, coefs, xi) for xi in x])

            # Rysowanie wykresu
            self.plot_results(x, y_original, x_nodes, y_nodes, x, y_interp)

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas interpolacji: {str(e)}")

    def plot_results(self, x_orig, y_orig, x_nodes, y_nodes, x_interp, y_interp):
        self.ax.clear()

        # Wykres funkcji oryginalnej
        self.ax.plot(x_orig, y_orig, 'b-', label='Funkcja oryginalna')

        # Wykres interpolacji
        self.ax.plot(x_interp, y_interp, 'r--', label='Wielomian interpolacyjny')

        # Zaznaczenie węzłów
        self.ax.plot(x_nodes, y_nodes, 'go', label='Węzły interpolacji')

        self.ax.set_title(f'Interpolacja Newtona - {self.function_type.get()}, {len(x_nodes)} węzłów')
        self.ax.legend()
        self.ax.grid(True)

        self.canvas.draw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = NewtonInterpolation()
    app.run()