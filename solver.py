import re
from dataclasses import dataclass
from typing import List, Optional

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


@dataclass
class SolveResult:
    success: bool
    detected_question: str
    final_answer: str
    steps: List[str]
    error_message: str = ""


def _normalize_math_text(text: str) -> str:
    replacements = {
        "x": "x",
        "X": "x",
        "*": "*",
        "×": "*",
        "·": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "^": "**",
        "√": "sqrt",
        "∫": "integrate",
        "π": "pi",
        "=": "=",
    }

    normalized = text
    for src, dst in replacements.items():
        normalized = normalized.replace(src, dst)

    normalized = normalized.replace("\r", "\n")
    normalized = "\n".join(line.strip() for line in normalized.split("\n") if line.strip())
    return normalized


def _looks_like_math(text: str) -> bool:
    if not text.strip():
        return False
    return bool(re.search(r"[0-9a-zA-Z=+\-*/()^]|sqrt|integrate|diff", text))


def extract_text_from_image(image_path: str) -> str:
    try:
        import cv2
        import pytesseract
    except Exception as exc:
        raise RuntimeError(
            "OCR dependencies are missing. Install pytesseract, pillow, and opencv-python."
        ) from exc

    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError("Could not load image file.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    raw_text = pytesseract.image_to_string(thresholded, config="--psm 6")
    return _normalize_math_text(raw_text)


def _parse_expression(expr: str):
    transformations = standard_transformations + (implicit_multiplication_application,)
    local_dict = {
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "ln": sp.log,
        "exp": sp.exp,
        "pi": sp.pi,
        "E": sp.E,
    }
    return parse_expr(expr, transformations=transformations, local_dict=local_dict, evaluate=True)


def _solve_arithmetic(problem: str) -> SolveResult:
    expression = _parse_expression(problem)
    simplified = sp.simplify(expression)
    steps = [
        f"Step 1: Parse expression -> {sp.sstr(expression)}",
        f"Step 2: Simplify expression -> {sp.sstr(simplified)}",
    ]
    return SolveResult(True, problem, sp.sstr(simplified), steps)


def _solve_single_equation(problem: str) -> SolveResult:
    left, right = problem.split("=", 1)
    left_expr = _parse_expression(left)
    right_expr = _parse_expression(right)

    symbols = sorted((left_expr.free_symbols | right_expr.free_symbols), key=lambda s: s.name)
    if not symbols:
        comparison = sp.simplify(left_expr - right_expr)
        is_true = comparison == 0
        return SolveResult(
            True,
            problem,
            "True" if is_true else "False",
            [
                f"Step 1: Compare both sides -> {sp.sstr(left_expr)} = {sp.sstr(right_expr)}",
                f"Step 2: Move all terms to one side -> {sp.sstr(comparison)} = 0",
            ],
        )

    target = symbols[0]
    equation = sp.Eq(left_expr, right_expr)

    moved = sp.expand(left_expr - right_expr)
    steps = [
        f"Step 1: Start with equation -> {sp.sstr(equation)}",
        f"Step 2: Move all terms to one side -> {sp.sstr(moved)} = 0",
    ]

    polynomial = sp.Poly(moved, target) if moved.is_polynomial(target) else None
    if polynomial is not None and polynomial.degree() == 2:
        a, b, c = polynomial.all_coeffs()
        discriminant = sp.simplify(b**2 - 4 * a * c)
        roots = sp.solve(equation, target)
        steps.extend(
            [
                f"Step 3: Identify quadratic coefficients -> a={sp.sstr(a)}, b={sp.sstr(b)}, c={sp.sstr(c)}",
                f"Step 4: Compute discriminant -> Delta = b^2 - 4ac = {sp.sstr(discriminant)}",
                f"Step 5: Solve for roots -> {target} = {sp.sstr(roots)}",
            ]
        )
        return SolveResult(True, problem, f"{target} = {sp.sstr(roots)}", steps)

    solutions = sp.solve(equation, target, dict=True)
    if not solutions:
        return SolveResult(False, problem, "", [], "Could not solve")

    solved_values = [sp.sstr(solution[target]) for solution in solutions if target in solution]
    steps.append(f"Step 3: Solve for {target} -> {target} = {solved_values}")
    return SolveResult(True, problem, f"{target} = {solved_values}", steps)


def _solve_system(problem: str) -> SolveResult:
    lines = [line for line in problem.split("\n") if line.strip()]
    equations = []
    symbols = set()

    for line in lines:
        if "=" not in line:
            continue
        left, right = line.split("=", 1)
        left_expr = _parse_expression(left)
        right_expr = _parse_expression(right)
        eq = sp.Eq(left_expr, right_expr)
        equations.append(eq)
        symbols |= left_expr.free_symbols | right_expr.free_symbols

    if len(equations) < 2:
        return SolveResult(False, problem, "", [], "Could not solve")

    ordered_symbols = sorted(symbols, key=lambda s: s.name)
    solution = sp.solve(equations, ordered_symbols, dict=True)

    steps = [
        f"Step 1: Identify system of equations -> {len(equations)} equations",
        "Step 2: Solve system simultaneously",
        f"Step 3: Solution -> {sp.sstr(solution)}",
    ]
    return SolveResult(True, problem, sp.sstr(solution), steps)


def _solve_derivative(problem: str) -> SolveResult:
    payload = problem.strip().replace(" ", "")
    x = sp.Symbol("x")

    if payload.startswith("d/dx"):
        expr_text = payload[4:]
    elif payload.lower().startswith("derivative"):
        expr_text = payload[len("derivative"):].strip("() ")
    elif payload.lower().startswith("diff"):
        expr_text = payload[len("diff"):].strip("() ")
    else:
        expr_text = payload

    expr = _parse_expression(expr_text)
    derivative = sp.diff(expr, x)
    steps = [
        f"Step 1: Start with function -> f(x) = {sp.sstr(expr)}",
        "Step 2: Differentiate with respect to x",
        f"Step 3: Result -> f'(x) = {sp.sstr(derivative)}",
    ]
    return SolveResult(True, problem, sp.sstr(derivative), steps)


def _solve_integral(problem: str) -> SolveResult:
    payload = problem.strip().replace(" ", "")
    x = sp.Symbol("x")

    if payload.lower().startswith("integrate"):
        expr_text = payload[len("integrate"):].strip("() ")
    elif payload.lower().startswith("int"):
        expr_text = payload[len("int"):].strip("() ")
    else:
        expr_text = payload

    expr = _parse_expression(expr_text)
    integral = sp.integrate(expr, x)
    steps = [
        f"Step 1: Start with expression -> {sp.sstr(expr)}",
        "Step 2: Integrate with respect to x",
        f"Step 3: Result -> {sp.sstr(integral)} + C",
    ]
    return SolveResult(True, problem, f"{sp.sstr(integral)} + C", steps)


def generate_steps(expression: str) -> SolveResult:
    normalized = _normalize_math_text(expression)
    if not _looks_like_math(normalized):
        return SolveResult(False, normalized, "", [], "No math detected in image")

    try:
        lowered = normalized.lower()
        non_empty_lines = [line for line in normalized.split("\n") if line.strip()]

        if any(token in lowered for token in ("d/dx", "derivative", "diff")):
            return _solve_derivative(normalized)

        if any(token in lowered for token in ("integrate", "int(", "int ", "∫")):
            return _solve_integral(normalized)

        if len(non_empty_lines) >= 2 and sum("=" in line for line in non_empty_lines) >= 2:
            return _solve_system(normalized)

        if "=" in normalized:
            return _solve_single_equation(normalized)

        return _solve_arithmetic(normalized)
    except Exception:
        return SolveResult(False, normalized, "", [], "Could not solve")


def solve_math_from_image(image_path: str, fallback_text: Optional[str] = None) -> SolveResult:
    text = fallback_text
    if text is None:
        text = extract_text_from_image(image_path)

    if not text.strip():
        return SolveResult(False, "", "", [], "No math detected in image")

    return generate_steps(text)
