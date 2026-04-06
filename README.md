# Advanced Calculator (Tkinter)

A modern scientific calculator desktop app built with Python and Tkinter.

## Features

- Basic operations: `+`, `-`, `*`, `/`, `%`, power (`^`)
- Scientific functions: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `log`, `log10`, `ln`, `exp`, `fact`
- Constants: `pi`, `e`, and reusable `ans`
- Parentheses and decimal support
- Degree/Radian mode toggle
- History panel with click-to-reuse expressions
- Keyboard support:
  - `Enter` evaluate
  - `Backspace` delete
  - `Esc` clear

## Run

```bash
python calculator_app.py
```

## Notes

- In `DEG` mode, trigonometric functions (`sin`, `cos`, `tan`) treat input as degrees.
- `asin`, `acos`, `atan` return radians by default.
