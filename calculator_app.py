import ast
import math
import tkinter as tk
from tkinter import ttk


class SafeEvaluator:
    """Safely evaluate arithmetic expressions with selected math functions."""

    ALLOWED_BIN_OPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Pow: lambda a, b: a**b,
        ast.Mod: lambda a, b: a % b,
    }

    ALLOWED_UNARY_OPS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    ALLOWED_FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "fact": math.factorial,
        "deg": math.degrees,
        "rad": math.radians,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "ans": 0.0,
    }

    def set_ans(self, value: float) -> None:
        self.ALLOWED_CONSTANTS["ans"] = value

    def evaluate(self, expression: str, angle_mode: str = "RAD") -> float:
        expression = expression.strip()
        if not expression:
            raise ValueError("Empty expression")

        normalized = expression.replace("^", "**")
        node = ast.parse(normalized, mode="eval")
        return float(self._eval_node(node.body, angle_mode.upper()))

    def _eval_node(self, node, angle_mode: str):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid constant")

        if isinstance(node, ast.Name):
            if node.id in self.ALLOWED_CONSTANTS:
                return self.ALLOWED_CONSTANTS[node.id]
            raise ValueError(f"Unknown symbol: {node.id}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.ALLOWED_BIN_OPS:
                left = self._eval_node(node.left, angle_mode)
                right = self._eval_node(node.right, angle_mode)
                return self.ALLOWED_BIN_OPS[op_type](left, right)
            raise ValueError("Operator not allowed")

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.ALLOWED_UNARY_OPS:
                operand = self._eval_node(node.operand, angle_mode)
                return self.ALLOWED_UNARY_OPS[op_type](operand)
            raise ValueError("Unary operator not allowed")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed")

            func_name = node.func.id
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"Function not allowed: {func_name}")

            args = [self._eval_node(arg, angle_mode) for arg in node.args]

            if func_name in {"sin", "cos", "tan"} and len(args) == 1 and angle_mode == "DEG":
                args[0] = math.radians(args[0])

            result = self.ALLOWED_FUNCTIONS[func_name](*args)

            if func_name in {"asin", "acos", "atan"} and angle_mode == "DEG":
                return math.degrees(result)
            return result

        raise ValueError("Unsupported expression")


class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Calculator")
        self.geometry("520x700")
        self.minsize(460, 620)

        self.evaluator = SafeEvaluator()
        self.history_items = []
        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")
        self.mode_var = tk.StringVar(value="RAD")
        self.theme_var = tk.StringVar(value="NIGHT")
        self.memory_value = 0.0

        self._build_styles()
        self._build_ui()
        self._bind_keys()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        if self.theme_var.get() == "NIGHT":
            colors = {
                "root": "#111827",
                "panel": "#1F2937",
                "display": "#0F172A",
                "display_fg": "#E5E7EB",
                "result_fg": "#22D3EE",
                "button_bg": "#374151",
                "button_active": "#4B5563",
                "accent_bg": "#0EA5E9",
                "accent_active": "#0284C7",
                "warn_bg": "#EF4444",
                "warn_active": "#DC2626",
                "history_fg": "#9CA3AF",
                "list_fg": "#CBD5E1",
                "list_sel": "#334155",
            }
        else:
            colors = {
                "root": "#F4F6FB",
                "panel": "#E7ECF5",
                "display": "#FFFFFF",
                "display_fg": "#111827",
                "result_fg": "#0F766E",
                "button_bg": "#D5DCE8",
                "button_active": "#C3CDDD",
                "accent_bg": "#2563EB",
                "accent_active": "#1D4ED8",
                "warn_bg": "#DC2626",
                "warn_active": "#B91C1C",
                "history_fg": "#334155",
                "list_fg": "#1E293B",
                "list_sel": "#BFDBFE",
            }

        self.colors = colors
        self.configure(bg=colors["root"])

        style.configure("Root.TFrame", background=colors["root"])
        style.configure("Panel.TFrame", background=colors["panel"])
        style.configure("Display.TFrame", background=colors["display"])

        style.configure(
            "Display.TLabel",
            background=colors["display"],
            foreground=colors["display_fg"],
            font=("Segoe UI", 16, "bold"),
            anchor="e",
        )

        style.configure(
            "Result.TLabel",
            background=colors["display"],
            foreground=colors["result_fg"],
            font=("Segoe UI", 24, "bold"),
            anchor="e",
        )

        style.configure(
            "Calc.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground=colors["display_fg"],
            background=colors["button_bg"],
            borderwidth=0,
            focuscolor="",
        )
        style.map("Calc.TButton", background=[("active", colors["button_active"])])

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground="#F9FAFB",
            background=colors["accent_bg"],
            borderwidth=0,
            focuscolor="",
        )
        style.map("Accent.TButton", background=[("active", colors["accent_active"])])

        style.configure(
            "Warn.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground="#F9FAFB",
            background=colors["warn_bg"],
            borderwidth=0,
            focuscolor="",
        )
        style.map("Warn.TButton", background=[("active", colors["warn_active"])])

        style.configure(
            "History.TLabel",
            background=colors["panel"],
            foreground=colors["history_fg"],
            font=("Consolas", 10),
            anchor="w",
        )

    def _build_ui(self):
        root = ttk.Frame(self, style="Root.TFrame", padding=12)
        root.pack(fill="both", expand=True)

        display = ttk.Frame(root, style="Display.TFrame", padding=14)
        display.pack(fill="x")

        ttk.Label(display, textvariable=self.expression_var, style="Display.TLabel").pack(fill="x")
        ttk.Label(display, textvariable=self.result_var, style="Result.TLabel").pack(fill="x", pady=(8, 0))

        controls = ttk.Frame(root, style="Root.TFrame")
        controls.pack(fill="x", pady=(10, 6))

        top_controls = ttk.Frame(controls, style="Root.TFrame")
        top_controls.pack(fill="x")
        ttk.Button(top_controls, text="AC", style="Warn.TButton", command=self.clear).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(top_controls, text="DEL", style="Calc.TButton", command=self.delete_last).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(top_controls, text="ANS", style="Calc.TButton", command=lambda: self.insert_text("ans")).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(top_controls, text="=", style="Accent.TButton", command=self.evaluate_expression).pack(side="left", expand=True, fill="x", padx=(4, 0))

        memory_controls = ttk.Frame(controls, style="Root.TFrame")
        memory_controls.pack(fill="x", pady=(6, 0))
        ttk.Button(memory_controls, text="MC", style="Calc.TButton", command=self.memory_clear).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(memory_controls, text="MR", style="Calc.TButton", command=self.memory_recall).pack(side="left", expand=True, fill="x", padx=3)
        ttk.Button(memory_controls, text="M+", style="Calc.TButton", command=self.memory_add).pack(side="left", expand=True, fill="x", padx=3)
        ttk.Button(memory_controls, text="M-", style="Calc.TButton", command=self.memory_subtract).pack(side="left", expand=True, fill="x", padx=3)
        self.theme_button = ttk.Button(
            memory_controls,
            text=f"{self.theme_var.get()}",
            style="Accent.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.pack(side="left", expand=True, fill="x", padx=(3, 0))

        keypad = ttk.Frame(root, style="Root.TFrame")
        keypad.pack(fill="both", expand=True)

        buttons = [
            ["sin(", "cos(", "tan(", "log(", "sqrt("],
            ["asin(", "acos(", "atan(", "ln(", "exp("],
            ["(", ")", "^", "%", "/"],
            ["7", "8", "9", "*", "pi"],
            ["4", "5", "6", "-", "e"],
            ["1", "2", "3", "+", "fact("],
            ["0", ".", "rad(", "deg(", "MODE"],
        ]

        for r, row in enumerate(buttons):
            keypad.rowconfigure(r, weight=1)
            for c, item in enumerate(row):
                keypad.columnconfigure(c, weight=1)

                if item == "MODE":
                    btn = ttk.Button(
                        keypad,
                        text=f"{self.mode_var.get()}",
                        style="Accent.TButton",
                        command=self.toggle_mode,
                    )
                    self.mode_button = btn
                elif item in {"+", "-", "*", "/", "^", "%"}:
                    btn = ttk.Button(keypad, text=item, style="Accent.TButton", command=lambda t=item: self.insert_text(t))
                else:
                    btn = ttk.Button(keypad, text=item, style="Calc.TButton", command=lambda t=item: self.insert_text(t))

                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3, ipady=8)

        history_panel = ttk.Frame(root, style="Panel.TFrame", padding=10)
        history_panel.pack(fill="both", expand=False, pady=(10, 0))

        ttk.Label(
            history_panel,
            text="History (click to reuse):",
            style="History.TLabel",
        ).pack(fill="x")

        self.history_list = tk.Listbox(
            history_panel,
            height=6,
            bg=self.colors["panel"],
            fg=self.colors["list_fg"],
            highlightthickness=0,
            selectbackground=self.colors["list_sel"],
            relief="flat",
            font=("Consolas", 10),
        )
        self.history_list.pack(fill="both", expand=True, pady=(6, 0))
        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)

    def _bind_keys(self):
        for char in "0123456789.+-*/%^()":
            self.bind(char, lambda event, c=char: self.insert_text(c))

        self.bind("<Return>", lambda event: self.evaluate_expression())
        self.bind("<KP_Enter>", lambda event: self.evaluate_expression())
        self.bind("<BackSpace>", lambda event: self.delete_last())
        self.bind("<Escape>", lambda event: self.clear())

    def insert_text(self, text: str):
        current = self.expression_var.get()
        self.expression_var.set(current + text)

    def clear(self):
        self.expression_var.set("")
        self.result_var.set("0")

    def delete_last(self):
        current = self.expression_var.get()
        if current:
            self.expression_var.set(current[:-1])

    def toggle_mode(self):
        if self.mode_var.get() == "RAD":
            self.mode_var.set("DEG")
        else:
            self.mode_var.set("RAD")
        self.mode_button.config(text=self.mode_var.get())

    def toggle_theme(self):
        if self.theme_var.get() == "NIGHT":
            self.theme_var.set("DAY")
        else:
            self.theme_var.set("NIGHT")
        self.theme_button.config(text=self.theme_var.get())
        self._build_styles()
        self._refresh_history_style()

    def _refresh_history_style(self):
        self.history_list.configure(
            bg=self.colors["panel"],
            fg=self.colors["list_fg"],
            selectbackground=self.colors["list_sel"],
        )

    def _current_numeric_value(self) -> float:
        if self.result_var.get() not in {"", "Error"}:
            try:
                return float(self.result_var.get())
            except ValueError:
                pass

        expr = self.expression_var.get().strip()
        if not expr:
            raise ValueError("No value available")
        return self.evaluator.evaluate(expr, self.mode_var.get())

    def memory_clear(self):
        self.memory_value = 0.0

    def memory_recall(self):
        current = self.expression_var.get()
        value = f"{self.memory_value:.12g}"
        self.expression_var.set(current + value)

    def memory_add(self):
        try:
            self.memory_value += self._current_numeric_value()
        except Exception:
            self.result_var.set("Error")

    def memory_subtract(self):
        try:
            self.memory_value -= self._current_numeric_value()
        except Exception:
            self.result_var.set("Error")

    def evaluate_expression(self):
        expr = self.expression_var.get().strip()
        if not expr:
            self.result_var.set("0")
            return

        try:
            value = self.evaluator.evaluate(expr, self.mode_var.get())
            self.evaluator.set_ans(value)

            display_value = f"{value:.12g}"
            self.result_var.set(display_value)
            self._append_history(expr, display_value)
        except Exception:
            self.result_var.set("Error")

    def _append_history(self, expression: str, result: str):
        entry = f"{expression} = {result}"
        self.history_items.append(entry)
        if len(self.history_items) > 50:
            self.history_items.pop(0)

        self.history_list.delete(0, tk.END)
        for item in reversed(self.history_items):
            self.history_list.insert(tk.END, item)

    def on_history_select(self, _event):
        selection = self.history_list.curselection()
        if not selection:
            return
        index = selection[0]
        item = self.history_list.get(index)
        expression = item.split(" = ")[0]
        self.expression_var.set(expression)


def main():
    app = AdvancedCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()
