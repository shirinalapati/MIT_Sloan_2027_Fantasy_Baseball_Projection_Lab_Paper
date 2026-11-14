"""Manuscript machinery: official SSAC Word template, numbered OMML equations, figures, tables, and a claims log.

The official template is NOT redistributed in this repository. Point SSAC_TEMPLATE at the organizers' file
(default: the author's research worktree copy). Content lives in build_content.py, which imports this module.
Every number printed through ev()/pct() is logged with its source artifact to claims_to_evidence.csv.
"""
from __future__ import annotations

import copy
import os
import re
from pathlib import Path

import docx
import pandas as pd
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "sloan2027_fantasy" / "paper"
FIGS = REPO / "sloan2027_fantasy" / "figures"
PSL_ROOT = Path(os.environ.get("PSL_ROOT", "/Users/Shirin/Future_Predictor/.worktrees/sloan-2027"))
TEMPLATE = Path(os.environ.get("SSAC_TEMPLATE", PSL_ROOT / "sloan2027/paper/SSAC_Paper_Template_official.docx"))
MINUS = "−"
CLAIMS: list[dict] = []


def m(s: str) -> str:
    """Typographic minus for numeric strings only (never apply to words)."""
    return re.sub(r"(?<![A-Za-z])-(?=\d)", MINUS, s) if isinstance(s, str) else s


def ev(text: str, source: str, section: str = "") -> str:
    CLAIMS.append({"section": section, "value_as_printed": text, "source_artifact": source})
    return text


def pct(v: float, lo: float | None = None, hi: float | None = None, nd: int = 1, src: str = "", sec: str = "", brackets: bool = True) -> str:
    """'−2.6% [−4.4, −0.9]' with typographic minus; logged."""
    def f(x):  # avoid printing a signed zero such as "-0.0"
        out = f"{x:+.{nd}f}"
        return out[1:] if float(out) == 0 else out
    s = f"{f(v)}%"
    if lo is not None:
        s += f" [{f(lo)}, {f(hi)}]" if brackets else f" (95% CI {f(lo)} to {f(hi)})"
    return ev(m(s), src, sec)


def num(v: float, fmt: str, src: str = "", sec: str = "") -> str:
    return ev(m(format(v, fmt)), src, sec)


# ------------------------------------------------------------------ OMML helpers
MNS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
RPR = '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'


def r_(t, plain=False):
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if plain else ""
    return f'<m:r>{sty}{RPR}<m:t xml:space="preserve">{t}</m:t></m:r>'


def sub(b, s): return f"<m:sSub><m:e>{b}</m:e><m:sub>{s}</m:sub></m:sSub>"
def sup(b, s): return f"<m:sSup><m:e>{b}</m:e><m:sup>{s}</m:sup></m:sSup>"
def frac(n, d): return f"<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>"
def rad(e): return f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{e}</m:e></m:rad>'
def nary(ch, lo, hi, e): return f'<m:nary><m:naryPr><m:chr m:val="{ch}"/>{"" if hi else "<m:supHide m:val=\"1\"/>"}</m:naryPr><m:sub>{lo}</m:sub><m:sup>{hi}</m:sup><m:e>{e}</m:e></m:nary>'
def dl(e, b="(", c=")"): return f'<m:d><m:dPr><m:begChr m:val="{b}"/><m:endChr m:val="{c}"/></m:dPr><m:e>{e}</m:e></m:d>'


EQ = {
    "rmse": (sub(r_("RMSE"), r_("k")) + dl(r_("F")) + r_("=") +
             rad(frac(nary("∑", r_("i∈k"), "", sub(r_("w"), r_("i")) + sup(dl(sub(r_("y"), r_("i")) + r_("−") + sub(r_("ŷ"), r_("i")) + dl(r_("F"))), r_("2"))),
                      nary("∑", r_("i∈k"), "", sub(r_("w"), r_("i")))))),
    "delta": (sub(r_("Δ"), r_("j")) + r_("=") + frac(r_("1"), r_("K")) +
              nary("∑", r_("k=1"), r_("K"), dl(sub(r_("RMSE"), r_("k")) + dl(r_("B∪") + dl(r_("j"), "{", "}")) + r_("−") + sub(r_("RMSE"), r_("k")) + dl(r_("B")), "[", "]"))),
    "admit": (r_("admit ", True) + r_("j") + r_("  ⟺  ") + sub(r_("Δ"), r_("j")) + r_("≤−0.005·RMSE") + dl(r_("B")) + r_(",  K≥3,  ") +
              dl(sub(r_("π"), r_("j")) + r_("≥0.6  or  ") + sub(r_("u"), r_("j")) + r_("&lt;0"))),
    "nested": (sub(r_("S"), r_("T")) + r_("=") + r_("𝒜") + dl(sub(r_("𝒟"), r_("≤T−2")) + r_(";  inner years 2018,…,T−1")) + r_(",     ") +
               sub(r_("ŷ"), r_("i,T")) + r_("=") + sub(r_("f"), r_("B∪") + sub(r_("S"), r_("T"))) + dl(sub(r_("x"), r_("i,T−1")))),
    "value": (sub(r_("V"), r_("i")) + r_("=") + nary("∑", r_("c∈C"), "", frac(sub(r_("x"), r_("i,c")) + r_("−") + sub(r_("μ"), r_("c")), sub(r_("σ"), r_("c")))) +
              r_(",   ") + sub(r_("x"), r_("i,AVG")) + r_("=") + sub(r_("H"), r_("i")) + r_("−") + sub(r_("AB"), r_("i")) + r_("·") + sub(r_("AVG"), r_("ref")) +
              r_(",   ") + sub(r_("x"), r_("i,ERA")) + r_("=") + frac(sub(r_("IP"), r_("i")) + r_("·") + sub(r_("ERA"), r_("ref")), r_("9")) + r_("−") + sub(r_("ER"), r_("i")) +
              r_(",   ") + sub(r_("x"), r_("i,WHIP")) + r_("=") + sub(r_("IP"), r_("i")) + r_("·") + sub(r_("WHIP"), r_("ref")) + r_("−") + dl(sub(r_("BB"), r_("i")) + r_("+") + sub(r_("H"), r_("i")))),
}


class Builder:
    def __init__(self, blind: bool):
        if not TEMPLATE.exists():
            raise SystemExit(f"Official SSAC template not found at {TEMPLATE}; set SSAC_TEMPLATE")
        self.blind = blind
        self.doc = docx.Document(str(TEMPLATE))
        ps = self.doc.paragraphs
        self.p_title, self.p_track, self.p_h1, self.p_h2 = (copy.deepcopy(ps[i]._element) for i in (0, 2, 5, 12))
        for proto in (self.p_h1, self.p_h2):  # the template's 1.6-inch tab stop pushes two-digit section titles far right
            for tabs in proto.findall(".//" + qn("w:tabs")):
                tabs.getparent().remove(tabs)
        self.p_body, self.p_refhead = copy.deepcopy(ps[7]._element), copy.deepcopy(ps[29]._element)
        self.t_eq = copy.deepcopy(self.doc.tables[0]._element)
        self.body = self.doc.element.body
        for el in list(self.body):
            if el.tag != qn("w:sectPr"):
                self.body.remove(el)
        self.eq_n = self.fig_n = self.tab_n = 0
        self.eq_num: dict[str, int] = {}
        self.ref_order: list[str] = []
        self.section = ""

    def _append(self, el):
        self.body.insert(len(self.body) - 1, el)
        return el

    def _fresh(self, proto):
        p = copy.deepcopy(proto)
        for ch in list(p):
            if ch.tag != qn("w:pPr"):
                p.remove(ch)
        return p

    @staticmethod
    def _run(text, size=22, bold=False, italic=False, color=None, font="Cambria"):
        r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
        f = OxmlElement("w:rFonts")
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            f.set(qn(a), font)
        rpr.append(f)
        if bold: rpr.append(OxmlElement("w:b"))
        if italic: rpr.append(OxmlElement("w:i"))
        if color:
            c = OxmlElement("w:color"); c.set(qn("w:val"), color); rpr.append(c)
        for tag in ("w:sz", "w:szCs"):
            s = OxmlElement(tag); s.set(qn("w:val"), str(size)); rpr.append(s)
        r.append(rpr)
        t = OxmlElement("w:t"); t.set(qn("xml:space"), "preserve"); t.text = text; r.append(t)
        return r

    def _rich(self, p, text, size=22):
        for tok in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*)", text):
            if not tok:
                continue
            if tok.startswith("**"):
                p.append(self._run(tok[2:-2], size, bold=True))
            elif tok.startswith("*"):
                p.append(self._run(tok[1:-1], size, italic=True))
            else:
                p.append(self._run(tok, size))

    def cite(self, *keys) -> str:
        nums = []
        for k in keys:
            if k not in self.ref_order:
                self.ref_order.append(k)
            nums.append(self.ref_order.index(k) + 1)
        return "[" + ", ".join(str(n) for n in sorted(nums)) + "]"

    def title_block(self, title: str):
        p = self._fresh(self.p_title); p.append(self._run(title, 36, bold=True)); self._append(p)
        p = self._fresh(self.p_track); p.append(self._run("Baseball", 28)); self._append(p)
        p = self._fresh(self.p_track); p.append(self._run("Paper ID: 18", 28)); self._append(p)
        if not self.blind:
            p = self._fresh(self.p_track); p.append(self._run("Shirin Alapati, San José State University", 22)); self._append(p)
        self._append(self._fresh(self.p_body))

    def h1(self, text):
        text = re.sub(r"^\d+(\.\d+)?\.?\s+", "", text)  # the template auto-numbers headings (1., 1.1.)
        self.section = text
        p = self._fresh(self.p_h1); p.append(self._run(text, 32, bold=True)); el = self._append(p)
        docx.text.paragraph.Paragraph(el, self.doc._body).paragraph_format.keep_with_next = True

    def h2(self, text):
        text = re.sub(r"^\d+(\.\d+)?\.?\s+", "", text)
        self.section = text
        p = self._fresh(self.p_h2); p.append(self._run(text, 24, bold=True)); el = self._append(p)
        docx.text.paragraph.Paragraph(el, self.doc._body).paragraph_format.keep_with_next = True

    def unnumbered(self, text, page_break=False):
        if page_break:
            self.page_break()
        p = self._fresh(self.p_refhead); p.append(self._run(text, 32, bold=True)); self._append(p)

    def para(self, text, size=22, align=None, keep_next=False, indent=None, space_after=None):
        p = self._fresh(self.p_body); self._rich(p, text, size); el = self._append(p)
        para = docx.text.paragraph.Paragraph(el, self.doc._body)
        if align: para.alignment = align
        if keep_next: para.paragraph_format.keep_with_next = True
        if indent is not None: para.paragraph_format.left_indent = Inches(indent)
        if space_after is not None: para.paragraph_format.space_after = Pt(space_after)
        return para

    def bullets(self, items, size=22):
        last = None
        for it in items:
            last = self.para("•  " + it, size=size, indent=0.25, space_after=3)
            last.paragraph_format.first_line_indent = Inches(-0.17)
        if last is not None:
            last.paragraph_format.space_after = Pt(11)

    def equation(self, key):
        self.eq_n += 1
        self.eq_num[key] = self.eq_n
        t = copy.deepcopy(self.t_eq)
        for bm in t.findall(".//" + qn("w:bookmarkStart")) + t.findall(".//" + qn("w:bookmarkEnd")):
            bm.getparent().remove(bm)
        om = t.find(".//" + qn("m:oMath"))
        for ch in list(om):
            om.remove(ch)
        for ch in parse_xml(f"<m:oMath {MNS}>{EQ[key]}</m:oMath>"):
            om.append(ch)
        seen_sep = False
        for r in t.findall(".//" + qn("w:r")):
            fc = r.find(qn("w:fldChar"))
            if fc is not None and fc.get(qn("w:fldCharType")) == "separate":
                seen_sep = True; continue
            if seen_sep and r.find(qn("w:t")) is not None:
                r.find(qn("w:t")).text = str(self.eq_n); break
        self._append(t)
        return self.eq_n

    def page_break(self):
        p = self._fresh(self.p_body); r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); p.append(r); self._append(p)

    def figure(self, png, caption, width=6.5):
        self.fig_n += 1
        if not png.startswith(f"fig{self.fig_n}_"):
            raise ValueError(f"figure order mismatch: {png} inserted as Figure {self.fig_n}")
        self.doc.add_picture(str(FIGS / png), width=Inches(width))
        pic = self.doc.paragraphs[-1]; pic.alignment = WD_ALIGN_PARAGRAPH.CENTER; pic.paragraph_format.keep_with_next = True
        p = self._fresh(self.p_body); p.append(self._run(f"Figure {self.fig_n}. ", 20, bold=True)); self._rich(p, caption, 20); self._append(p)
        return self.fig_n

    def table(self, df: pd.DataFrame, caption: str, widths, font=16, note=None, keep_together=True):
        self.tab_n += 1
        cap = self._fresh(self.p_body); cap.append(self._run(f"Table {self.tab_n}. ", 20, bold=True)); self._rich(cap, caption, 20); el = self._append(cap)
        docx.text.paragraph.Paragraph(el, self.doc._body).paragraph_format.keep_with_next = True
        tbl = self.doc.add_table(rows=len(df) + 1, cols=len(df.columns))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER; tbl.autofit = False
        tblPr = tbl._tbl.tblPr
        borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:color="444444"/><w:bottom w:val="single" w:sz="8" w:color="444444"/>'
                            f'<w:insideH w:val="single" w:sz="2" w:color="D0D0D0"/></w:tblBorders>')
        anchor = next((tblPr.find(qn(t)) for t in ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption") if tblPr.find(qn(t)) is not None), None)
        if anchor is not None:
            anchor.addprevious(borders)
        else:
            tblPr.append(borders)
        for j, col in enumerate(df.columns):
            for i in range(len(df) + 1):
                cell = tbl.cell(i, j); cell.width = Inches(widths[j])
                txt = str(col) if i == 0 else str(df.iloc[i - 1, j])
                cp = cell.paragraphs[0]; cp.paragraph_format.space_after = Pt(0)
                if i == 0:
                    cp._p.append(self._run(txt, font, bold=True))
                    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="EFEFEC"/>'))
                else:
                    self._rich(cp._p, txt, font)
        tr = tbl.rows[0]._tr; trPr = tr.get_or_add_trPr(); trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for i, row in enumerate(tbl.rows):
            row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            if keep_together and len(df) <= 15 and i < len(tbl.rows) - 1:
                for cell in row.cells:
                    for cp in cell.paragraphs:
                        cp.paragraph_format.keep_with_next = True
        if note:
            self.para(note, size=18)
        else:
            self._append(self._fresh(self.p_body))
        return self.tab_n

    def references(self, bib: dict):
        self.unnumbered("References", page_break=True)
        missing = [k for k in self.ref_order if k not in bib]
        if missing:
            raise KeyError(f"citations without a verified bibliography entry: {missing}")
        for i, k in enumerate(self.ref_order, 1):
            p = self._fresh(self.p_body); p.append(self._run(f"[{i}] ", 20)); self._rich(p, bib[k], 20); el = self._append(p)
            pf = docx.text.paragraph.Paragraph(el, self.doc._body).paragraph_format
            pf.space_after = Pt(4); pf.left_indent = Inches(0.35); pf.first_line_indent = Inches(-0.35)

    def save(self, path):
        cp = self.doc.core_properties
        cp.author = "" if self.blind else "Shirin Alapati"
        cp.last_modified_by = ""
        cp.title = "One Metric, Different Jobs"
        cp.comments = ""
        cp.keywords = ""
        cp.subject = ""
        self.doc.save(str(path))
        _scrub_app_xml(path)


def _scrub_app_xml(path):
    """Drop the template's stale page/word counts from docProps/app.xml (Word recomputes them on save)."""
    import re as _re
    import shutil
    import tempfile
    import zipfile
    tmp = Path(tempfile.mkstemp(suffix=".docx")[1])
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                txt = data.decode("utf-8")
                for tag in ("Pages", "Words", "Characters", "Lines", "Paragraphs", "CharactersWithSpaces", "TotalTime"):
                    txt = _re.sub(rf"<{tag}>[^<]*</{tag}>", "", txt)
                data = txt.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(str(tmp), str(path))
