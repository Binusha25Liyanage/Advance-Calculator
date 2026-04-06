import base64
import os
import re
from typing import Optional


class ClaudeVisionSolver:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            import anthropic  # noqa: F401
            return True
        except Exception:
            return False

    def solve_from_image(self, image_path: str) -> dict:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured.")

        try:
            import anthropic
        except Exception as exc:
            raise RuntimeError("anthropic package is not installed.") from exc

        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": _media_type_from_path(image_path),
                                "data": encoded,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "You are a math tutor. Look at this image, extract the math question, solve it, "
                                "and return:\n"
                                "1) The detected question\n"
                                "2) Step-by-step solution\n"
                                "3) Final answer\n"
                                "Format clearly."
                            ),
                        },
                    ],
                }
            ],
        )

        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        raw = "\n".join(text_blocks)
        return _parse_claude_response(raw)


def _media_type_from_path(image_path: str) -> str:
    lower = image_path.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def _parse_claude_response(content: str) -> dict:
    question = _extract_section(content, r"detected question\s*[:\-]\s*(.+)")
    answer = _extract_section(content, r"final answer\s*[:\-]\s*(.+)")

    step_lines = []
    for line in content.splitlines():
        if re.match(r"\s*(step\s*\d+|\d+\.)", line.strip(), flags=re.IGNORECASE):
            step_lines.append(line.strip())

    if not step_lines:
        step_lines = [line.strip() for line in content.splitlines() if line.strip()]

    return {
        "success": True,
        "detected_question": question or "Extracted via Claude Vision",
        "final_answer": answer or "See steps",
        "steps": step_lines,
        "error_message": "",
    }


def _extract_section(content: str, pattern: str) -> str:
    match = re.search(pattern, content, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()
