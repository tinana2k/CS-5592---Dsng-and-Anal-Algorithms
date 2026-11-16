"""
Converts the presentation script Markdown into a clean, printable PDF document:
Presentation_Script_Tina_and_Haoran.pdf
"""

import os
from fpdf import FPDF

SCRIPT_MD_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "Presentation_Script_Tina_and_Haoran.md"))
OUT_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "Presentation_Script_Tina_and_Haoran.pdf"))

class ScriptPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "COMP-SCI 5592 Assignment 2 Presentation Script | Tina Nguyen & Haoran", 0, 0, "L")
        self.cell(0, 8, f"Page {self.page_no()}", 0, 1, "R")
        self.line(10, 15, 200, 15)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "University of Missouri - Kansas City | Presentation Date: Dec 8 & 10, 2026", 0, 0, "C")

pdf = ScriptPDF(orientation="P", unit="mm", format="A4")
pdf.set_margins(12, 12, 12)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

pdf.set_font("Helvetica", "B", 15)
pdf.set_text_color(0, 32, 96)
pdf.cell(0, 7, "Presentation Script & Defense Guide", 0, 1, "C")
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 5, "COMP-SCI 5592: Design and Analysis of Algorithms - Assignment 2", 0, 1, "C")
pdf.cell(0, 5, "Tina Nguyen (Problem 1 Lead) & Haoran (Problem 2 Lead)", 0, 1, "C")
pdf.ln(4)

with open(SCRIPT_MD_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_table = False
for line in lines:
    raw = line.strip()
    if not raw:
        pdf.ln(1.5)
        continue
    
    # Clean characters for latin-1
    clean = (raw.replace("—", " - ")
                .replace("–", "-")
                .replace("“", '"')
                .replace("”", '"')
                .replace("’", "'")
                .replace("‘", "'")
                .replace("≥", ">=")
                .replace("≤", "<=")
                .replace("≠", "!=")
                .replace("Δ", "Delta")
                .replace("ϕ", "phi")
                .replace("φ", "phi")
                .replace("≈", " approx ")
                .replace("•", "* ")
                .replace("⌈", "ceil(")
                .replace("⌉", ")")
                .replace("č", "c")
                .replace("ć", "c")
                .replace("ň", "n")
                .replace("š", "s")
                .replace("**", "")
                .replace("$$", "")
                .replace("$", ""))

    if clean.startswith("### Slide"):
        pdf.ln(3)
        pdf.set_fill_color(235, 242, 250)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 32, 96)
        pdf.cell(0, 6, clean.replace("### ", ""), 0, 1, "L", True)
        pdf.ln(1)
    elif clean.startswith("## "):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(10, 34, 64)
        pdf.cell(0, 7, clean.replace("## ", ""), 0, 1, "L")
        pdf.line(12, pdf.get_y(), 198, pdf.get_y())
        pdf.ln(2)
    elif clean.startswith("# "):
        continue
    elif clean.startswith("Speaker:"):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(180, 50, 50)
        pdf.cell(0, 4.5, clean, 0, 1, "L")
    elif clean.startswith("Estimated Time:") or clean.startswith("Visual:"):
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 4.5, clean, 0, 1, "L")
    elif clean.startswith("> Tina:") or clean.startswith("> Haoran:"):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(0, 80, 150)
        pdf.cell(0, 5, clean.replace("> ", ""), 0, 1, "L")
    elif clean.startswith(">"):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(pdf.epw, 4.2, clean.replace("> ", ""))
    elif clean.startswith("|"):
        # Table row
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 30)
        cells = [c.strip() for c in clean.split("|")[1:-1]]
        if cells and not all(c.startswith("-") for c in cells):
            row_txt = " | ".join(cells)
            pdf.multi_cell(pdf.epw, 4, row_txt)
    else:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(pdf.epw, 4.2, clean)

pdf.output(OUT_PDF_PATH)
print(f"Presentation script PDF saved successfully to {OUT_PDF_PATH}")
