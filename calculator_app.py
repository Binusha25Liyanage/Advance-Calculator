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

    def evaluate(self, expression: str) -> float:
        expression = expression.strip()
        if not expression:
            raise ValueError("Empty expression")

        normalized = expression.replace("^", "**")
        node = ast.parse(normalized, mode="eval")
        return float(self._eval_node(node.body))

    def _eval_node(self, node):
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
                left = self._eval_node(node.left)
                right = self._eval_node(node.right)
                return self.ALLOWED_BIN_OPS[op_type](left, right)
            raise ValueError("Operator not allowed")

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.ALLOWED_UNARY_OPS:
                operand = self._eval_node(node.operand)
                return self.ALLOWED_UNARY_OPS[op_type](operand)
            raise ValueError("Unary operator not allowed")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed")

            func_name = node.func.id
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"Function not allowed: {func_name}")

            args = [self._eval_node(arg) for arg in node.args]
            return self.ALLOWED_FUNCTIONS[func_name](*args)

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

        self._build_styles()
        self._build_ui()
        self._bind_keys()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        self.configure(bg="#111827")

        style.configure("Root.TFrame", background="#111827")
        style.configure("Panel.TFrame", background="#1F2937")
        style.configure("Display.TFrame", background="#0F172A")

        style.configure(
            "Display.TLabel",
            background="#0F172A",
            foreground="#E5E7EB",
            font=("Segoe UI", 16, "bold"),
            anchor="e",
        )

        style.configure(
            "Result.TLabel",
            background="#0F172A",
            foreground="#22D3EE",
            font=("Segoe UI", 24, "bold"),
            anchor="e",
        )

        style.configure(
            "Calc.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground="#E5E7EB",
            background="#374151",
            borderwidth=0,
            focuscolor="",
        )
        style.map("Calc.TButton", background=[("active", "#4B5563")])

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground="#E5E7EB",
            background="#0EA5E9",
            borderwidth=0,
            focuscolor="",
        )
        style.map("Accent.TButton", background=[("active", "#0284C7")])

        style.configure(
            "Warn.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8,
            foreground="#E5E7EB",
            background="#EF4444",
            borderwidth=0,
            focuscolor="",
        )
        style.map("Warn.TButton", background=[("active", "#DC2626")])

        style.configure(
            "History.TLabel",
            background="#1F2937",
            foreground="#9CA3AF",
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

        ttk.Button(controls, text="AC", style="Warn.TButton", command=self.clear).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(controls, text="DEL", style="Calc.TButton", command=self.delete_last).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(controls, text="ANS", style="Calc.TButton", command=lambda: self.insert_text("ans")).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(controls, text="=", style="Accent.TButton", command=self.evaluate_expression).pack(side="left", expand=True, fill="x", padx=(4, 0))

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
            bg="#1F2937",
            fg="#CBD5E1",
            highlightthickness=0,
            selectbackground="#334155",
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

    def _preprocess_expression(self, expression: str) -> str:
        if self.mode_var.get() == "DEG":
            for fn in ("sin", "cos", "tan"):
                expression = expression.replace(f"{fn}(", f"{fn}(rad(")
                expression = self._close_rad_argument(expression, fn)
        return expression

    @staticmethod
    def _close_rad_argument(expression: str, fn_name: str) -> str:
        """
        Balance inserted rad( by injecting a closing parenthesis before
        the matching function closing parenthesis.
        """
        target = f"{fn_name}(rad("
        idx = expression.find(target)
        while idx != -1:
            start = idx + len(target)
            depth = 1
            i = start
            while i < len(expression):
                ch = expression[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        expression = expression[:i] + ")" + expression[i:]
                        break
                i += 1
            idx = expression.find(target, idx + len(target) + 1)
        return expression

    def evaluate_expression(self):
        expr = self.expression_var.get().strip()
        if not expr:
            self.result_var.set("0")
            return

        try:
            processed = self._preprocess_expression(expr)
            value = self.evaluator.evaluate(processed)
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
