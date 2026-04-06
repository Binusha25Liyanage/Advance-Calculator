import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class MathSolverPopup(tk.Toplevel):
    def __init__(self, parent, image_path: str, payload: dict, theme_mode: str = "NIGHT"):
        super().__init__(parent)
        self.title("📐 Math Solver — Step-by-Step Solution")
        self.geometry("700x760")
        self.minsize(560, 560)
        self.transient(parent)
        self.grab_set()

        self.payload = payload
        self.theme_mode = theme_mode
        self.colors = self._colors_for_theme(theme_mode)
        self.configure(bg=self.colors["root"])

        self._thumbnail_ref = None
        self._build_ui(image_path)

    def _colors_for_theme(self, theme_mode: str):
        if theme_mode == "NIGHT":
            return {
                "root": "#111827",
                "panel": "#1F2937",
                "text": "#E5E7EB",
                "muted": "#9CA3AF",
                "answer": "#22C55E",
                "button": "#0EA5E9",
                "button_active": "#0284C7",
                "mono_bg": "#0F172A",
                "mono_fg": "#BFDBFE",
            }
        return {
            "root": "#F4F6FB",
            "panel": "#E7ECF5",
            "text": "#0F172A",
            "muted": "#334155",
            "answer": "#15803D",
            "button": "#2563EB",
            "button_active": "#1D4ED8",
            "mono_bg": "#FFFFFF",
            "mono_fg": "#0F172A",
        }

    def _build_ui(self, image_path: str):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Popup.TFrame", background=self.colors["root"])
        style.configure("PopupPanel.TFrame", background=self.colors["panel"])
        style.configure("PopupText.TLabel", background=self.colors["panel"], foreground=self.colors["text"], font=("Segoe UI", 11))
        style.configure("PopupTitle.TLabel", background=self.colors["panel"], foreground=self.colors["text"], font=("Segoe UI", 12, "bold"))
        style.configure("PopupAnswer.TLabel", background=self.colors["panel"], foreground=self.colors["answer"], font=("Segoe UI", 13, "bold"))
        style.configure("Popup.TButton", background=self.colors["button"], foreground="#F9FAFB", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Popup.TButton", background=[("active", self.colors["button_active"])])

        outer = ttk.Frame(self, style="Popup.TFrame", padding=12)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=self.colors["root"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = ttk.Frame(canvas, style="PopupPanel.TFrame", padding=12)
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

        def _on_content_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfigure(canvas_window, width=event.width)

        content.bind("<Configure>", _on_content_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        ttk.Label(content, text="🖼️ Preview", style="PopupTitle.TLabel").pack(fill="x", pady=(0, 6))
        image_holder = ttk.Frame(content, style="PopupPanel.TFrame")
        image_holder.pack(fill="x", pady=(0, 14))
        self._render_preview(image_path, image_holder)

        detected = self.payload.get("detected_question", "")
        ttk.Label(content, text="📝 Detected Question", style="PopupTitle.TLabel").pack(fill="x")
        ttk.Label(content, text=detected or "N/A", style="PopupText.TLabel", wraplength=620, justify="left").pack(fill="x", pady=(4, 14))

        final_answer = self.payload.get("final_answer", "")
        ttk.Label(content, text="✅ Final Answer", style="PopupTitle.TLabel").pack(fill="x")
        ttk.Label(content, text=final_answer or "N/A", style="PopupAnswer.TLabel", wraplength=620, justify="left").pack(fill="x", pady=(4, 14))

        ttk.Label(content, text="🧮 Step-by-Step Solution", style="PopupTitle.TLabel").pack(fill="x")
        steps_text = "\n".join(self.payload.get("steps", [])) or "No steps available."
        steps_widget = tk.Text(
            content,
            height=14,
            wrap="word",
            bg=self.colors["mono_bg"],
            fg=self.colors["mono_fg"],
            insertbackground=self.colors["mono_fg"],
            relief="flat",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        steps_widget.insert("1.0", steps_text)
        steps_widget.configure(state="disabled")
        steps_widget.pack(fill="both", expand=True, pady=(6, 12))

        button_bar = ttk.Frame(content, style="PopupPanel.TFrame")
        button_bar.pack(fill="x", pady=(0, 8))
        ttk.Button(button_bar, text="Copy Answer", style="Popup.TButton", command=self._copy_answer).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(button_bar, text="Copy All Steps", style="Popup.TButton", command=self._copy_steps).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(button_bar, text="Close", style="Popup.TButton", command=self.destroy).pack(side="left", expand=True, fill="x", padx=(4, 0))

        if self.payload.get("error_message"):
            ttk.Label(
                content,
                text=self.payload["error_message"],
                style="PopupText.TLabel",
                foreground="#F87171" if self.theme_mode == "NIGHT" else "#B91C1C",
                wraplength=620,
                justify="left",
            ).pack(fill="x", pady=(6, 0))

    def _render_preview(self, image_path: str, container):
        try:
            image = Image.open(image_path)
            image.thumbnail((360, 220))
            tk_image = ImageTk.PhotoImage(image)
            self._thumbnail_ref = tk_image
            label = tk.Label(container, image=tk_image, bg=self.colors["panel"])
            label.pack(anchor="w")
        except Exception:
            ttk.Label(container, text="Preview unavailable", style="PopupText.TLabel").pack(anchor="w")

    def _copy_answer(self):
        answer = self.payload.get("final_answer", "")
        self.clipboard_clear()
        self.clipboard_append(answer)

    def _copy_steps(self):
        steps = "\n".join(self.payload.get("steps", []))
        self.clipboard_clear()
        self.clipboard_append(steps)
