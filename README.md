# Advanced Calculator (Tkinter)

A modern scientific calculator desktop app built with Python and Tkinter.

## Features

- Basic operations: `+`, `-`, `*`, `/`, `%`, power (`^`)
- Scientific functions: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sqrt`, `log`, `log10`, `ln`, `exp`, `fact`
- Constants: `pi`, `e`, and reusable `ans`
- Parentheses and decimal support
- Degree/Radian mode toggle
- Memory operations: `MC`, `MR`, `M+`, `M-`
- Theme toggle: `NIGHT` and `DAY`
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
- In `DEG` mode, inverse trigonometric functions (`asin`, `acos`, `atan`) return degrees.
- In `RAD` mode, all trigonometric functions use radians.
