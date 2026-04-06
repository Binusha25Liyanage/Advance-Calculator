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
- Image-based math solver with OCR and step-by-step explanation popup
- Keyboard support:
  - `Enter` evaluate
  - `Backspace` delete
  - `Esc` clear

## Solve from Image

- Click `📷 Solve from Image`
- Upload `JPG`, `PNG`, or `WEBP`
- The app preprocesses the image with OpenCV and extracts text with Tesseract OCR
- It solves the detected problem using SymPy and shows:
  - Image preview
  - Detected question
  - Final answer
  - Numbered step-by-step solution
  - Copy buttons for answer and all steps

If OCR solving fails and `ANTHROPIC_API_KEY` is configured, Claude Vision fallback can be used.

## Dependencies

```bash
pip install pytesseract pillow opencv-python sympy anthropic
```

Install Tesseract OCR engine:

- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Linux: `sudo apt install tesseract-ocr`

Optional Claude fallback key:

```bash
set ANTHROPIC_API_KEY=your_key_here
```

## Run

```bash
python calculator_app.py
```

## Notes

- In `DEG` mode, trigonometric functions (`sin`, `cos`, `tan`) treat input as degrees.
- In `DEG` mode, inverse trigonometric functions (`asin`, `acos`, `atan`) return degrees.
- In `RAD` mode, all trigonometric functions use radians.
- New modules:
  - `solver.py` OCR + SymPy solve + step generator
  - `popup.py` themed result popup UI
  - `ai_solver.py` optional Claude Vision fallback
