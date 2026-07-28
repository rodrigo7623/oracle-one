"""Convierte docs/fuente_documentacion.md en docs/documentacion_novashop.pdf.

Se ejecuta una sola vez para producir el documento fuente que el agente
va a indexar. No forma parte del runtime del agente.
"""
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parent.parent
SOURCE_MD = ROOT / "docs" / "fuente_documentacion.md"
OUTPUT_PDF = ROOT / "docs" / "documentacion_novashop.pdf"

# Fuente TTF con soporte completo de acentos/ñ (los fonts core de PDF
# (Helvetica) usan tablas de ancho incompletas para caracteres latinos).
FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\DejaVuSans.ttf"),
]


def _register_font(pdf: FPDF) -> str:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            pdf.add_font("Body", "", str(candidate))
            bold_candidate = candidate.with_name(candidate.stem + "bd.ttf")
            if bold_candidate.exists():
                pdf.add_font("Body", "B", str(bold_candidate))
            else:
                pdf.add_font("Body", "B", str(candidate))
            return "Body"
    raise RuntimeError("No se encontro una fuente TTF con soporte unicode.")


def build_pdf() -> None:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    font_name = _register_font(pdf)
    pdf.set_font(font_name, size=11)

    for raw_line in SOURCE_MD.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line:
            pdf.ln(3)
            continue

        if line.startswith("## "):
            pdf.set_font(font_name, "B", 15)
            pdf.ln(4)
            pdf.multi_cell(0, 8, line.removeprefix("## "), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font(font_name, size=11)
            continue

        if line.startswith("# "):
            pdf.set_font(font_name, "B", 18)
            pdf.multi_cell(0, 10, line.removeprefix("# "), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font(font_name, size=11)
            continue

        text = line.replace("**", "")
        pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT_PDF))
    print(f"PDF generado en: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
