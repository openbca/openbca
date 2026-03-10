#!/usr/bin/env python3
"""
Pre-render Mermaid code blocks to PNGs for PDF generation.
Reads README.md, extracts ```mermaid ... ``` blocks, renders each via
1) @mermaid-js/mermaid-cli (npx) if available, else
2) mermaid.ink API: encode diagram, fetch PNG, save to readme_pdf_temp (requires network).
Markdown always gets local image paths so the PDF shows diagrams.
"""

import base64
import json
import re
import ssl
import subprocess
import sys
import urllib.request
import zlib
from pathlib import Path


def extract_mermaid_blocks(content: str) -> list[tuple[int, int, str]]:
    """Return list of (start_pos, end_pos, mermaid_code) for each ```mermaid block."""
    blocks = []
    pattern = re.compile(r"^```mermaid\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
    for m in pattern.finditer(content):
        blocks.append((m.start(0), m.end(0), m.group(1).strip()))
    return blocks


def mermaid_ink_img_url(mermaid_code: str) -> str:
    """Return mermaid.ink image URL (pako: base64url of deflate-compressed JSON, no zlib header)."""
    state = {"code": mermaid_code, "mermaid": {"theme": "default"}}
    # ensure_ascii=True so JSON is ASCII (matches mermaid.live / mermaid.ink expectations)
    raw = json.dumps(state, ensure_ascii=True).encode("utf-8")
    compress = zlib.compressobj(9, zlib.DEFLATED, 15, 8, zlib.Z_DEFAULT_STRATEGY)
    compressed = compress.compress(raw) + compress.flush()
    b64 = base64.b64encode(compressed).decode("ascii").replace("+", "-").replace("/", "_")
    return f"https://mermaid.ink/img/pako:{b64}?type=png"


def fetch_mermaid_ink_to_file(url: str, png_path: Path) -> bool:
    """Fetch mermaid.ink image and save to png_path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenBCA-readme-pdf/1.0"})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read()
        if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
            png_path.parent.mkdir(parents=True, exist_ok=True)
            png_path.write_bytes(data)
            return True
        return False
    except Exception:
        return False


def _npx_cmd() -> list[str]:
    """Return [npx, ...] with npx path; try Homebrew on macOS if npx not in PATH."""
    import shutil
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", "@mermaid-js/mermaid-cli"]
    if sys.platform == "darwin":
        for prefix in ("/opt/homebrew", "/usr/local"):
            candidate = Path(prefix) / "bin" / "npx"
            if candidate.is_file():
                return [str(candidate), "-y", "@mermaid-js/mermaid-cli"]
    return ["npx", "-y", "@mermaid-js/mermaid-cli"]


def render_mermaid_to_png(mermaid_code: str, mmd_path: Path, png_path: Path) -> str | None:
    """
    Render one Mermaid diagram to PNG. Returns local path (readme_pdf_temp/diagram_N.png) or None.
    Tries mermaid-cli first; on failure fetches from mermaid.ink and saves to png_path.
    """
    mmd_path.parent.mkdir(parents=True, exist_ok=True)
    mmd_path.write_text(mermaid_code, encoding="utf-8")
    cmd = _npx_cmd() + ["-i", str(mmd_path), "-o", str(png_path)]
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return f"readme_pdf_temp/{png_path.name}"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        url = mermaid_ink_img_url(mermaid_code)
        if fetch_mermaid_ink_to_file(url, png_path):
            return f"readme_pdf_temp/{png_path.name}"
        print(f"Warning: could not render or fetch diagram (npx not available, mermaid.ink failed)", file=sys.stderr)
        return None


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    readme_path = repo_root / "README.md"
    out_md_path = repo_root / "README.pdf.md"
    temp_dir = repo_root / "readme_pdf_temp"

    content = readme_path.read_text(encoding="utf-8")
    blocks = extract_mermaid_blocks(content)
    if not blocks:
        # No mermaid blocks; just copy
        out_md_path.write_text(content, encoding="utf-8")
        return 0

    temp_dir.mkdir(parents=True, exist_ok=True)
    image_refs = []
    for i, (start, end, code) in enumerate(blocks):
        mmd_path = temp_dir / f"diagram_{i}.mmd"
        png_path = temp_dir / f"diagram_{i}.png"
        ref = render_mermaid_to_png(code, mmd_path, png_path)
        image_refs.append((start, end, f'\n![Mermaid diagram]({ref})\n' if ref else None))

    # Build new content with each mermaid block replaced by an image ref
    result = []
    pos = 0
    for start, end, replacement in image_refs:
        result.append(content[pos:start])
        result.append(replacement if replacement else content[start:end])
        pos = end
    result.append(content[pos:])
    out_md_path.write_text("".join(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
