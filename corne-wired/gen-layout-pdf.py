#!/usr/bin/env python3
"""Generate layout.pdf from the current keymap, matching layout.txt.

Renders an HTML page that headless Chrome converts to layout.pdf (next to this
script). Run after editing the keymap:  python3 gen-layout-pdf.py

The layer data below is the source the PDF is drawn from; keep it in sync with
keymap.c / layout.txt by hand (same as those two are kept in sync with each
other). keymap.c remains the firmware source of truth.
"""
import html
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c) or shutil.which(c):
            return c
    return None

# Each key cell = (main, [sub lines...]). "" = blank cell, "TRNS"/"NOOP"/"ACT" special.
TR = "▽"   # transparent
NO = "∅"   # no-op
ACT = "ACTIVE"  # layer-active-from-here marker

def cell(main, *subs):
    return (main, list(subs))

# Mod sub-labels for the standard bottom-row mod row (left then right halves)
LMOD = ["", "Shift", "Ctrl", "Alt", "Gui", ""]
RMOD = ["", "Gui", "Alt", "Ctrl", "Shift", ""]

def trns_mod_row():
    L = [cell(TR, m) if m else cell(TR) for m in LMOD]
    R = [cell(TR, m) if m else cell(TR) for m in RMOD]
    return L, R

LAYERS = []

# ---- Layer 0 — Base (Cyan) ----
L0L = [
    [cell("Tab"), cell("Q"), cell("W"), cell("E"), cell("R"), cell("T")],
    [cell("Esc"), cell("A"), cell("S"), cell("D"), cell("F"), cell("G")],
    [cell("Shift"), cell("Z","Shift"), cell("X","Ctrl"), cell("C","Alt"), cell("V","Gui"), cell("B")],
]
L0R = [
    [cell("Y"), cell("U"), cell("I"), cell("O"), cell("P"), cell("\\")],
    [cell("H"), cell("J"), cell("K"), cell("L"), cell(";"), cell("'")],
    [cell("N"), cell("M","Gui"), cell(",","Alt"), cell(".","Ctrl"), cell("/","Shift"), cell("Shift")],
]
L0LT = [cell("MO(1)"), cell("MO(2)"), cell("Bksp")]
L0RT = [cell("Enter"), cell("Space"), cell("MO(4)")]
LAYERS.append(dict(title="Layer 0 — Base (Cyan)", act="", L=L0L, R=L0R, LT=L0LT, RT=L0RT, note=""))

# ---- Layer 1 — Numbers (Blue) ----
L1L = [
    [cell(TR), cell("1"), cell("2"), cell("3"), cell("4"), cell("5")],
    [cell(TR), cell("Esc"), cell("Tab"), cell("["), cell("]"), cell("<")],
    trns_mod_row()[0],
]
L1R = [
    [cell("6"), cell("7"), cell("8"), cell("9"), cell("0"), cell(TR)],
    [cell(">"), cell("{"), cell("}"), cell("("), cell(")"), cell(TR)],
    trns_mod_row()[1],
]
LAYERS.append(dict(title="Layer 1 — Numbers (Blue)", act="Activate: hold left thumb MO(1)",
                   L=L1L, R=L1R, LT=[cell(ACT), cell(TR), cell(TR)], RT=[cell(TR), cell(TR), cell("MO(3)")],
                   note="MO(1)+MO(3) = Layer 3"))

# ---- Layer 2 — Symbols (Magenta) ----
L2L = [
    [cell(TR), cell("`"), cell("~"), cell("\\"), cell("|"), cell(NO)],
    [cell(TR), cell("!"), cell("@"), cell("#"), cell("$"), cell("%")],
    trns_mod_row()[0],
]
L2R = [
    [cell(NO), cell("-"), cell("_"), cell("+"), cell("="), cell(TR)],
    [cell("^"), cell("&"), cell("*"), cell("'"), cell('"'), cell(TR)],
    trns_mod_row()[1],
]
LAYERS.append(dict(title="Layer 2 — Symbols (Magenta)", act="Activate: hold left thumb MO(2)",
                   L=L2L, R=L2R, LT=[cell(TR), cell(ACT), cell(TR)], RT=[cell(TR), cell(TR), cell(TR)],
                   note="∅ = no-op · < and > live on Layer 1 home"))

# ---- Layer 3 — Function Keys (Green) ----
L3L = [
    [cell(TR), cell("F1"), cell("F2"), cell("F3"), cell("F4"), cell("F5")],
    [cell(TR), cell("F11"), cell("F12"), cell("F13"), cell("F14"), cell("F15")],
    trns_mod_row()[0],
]
L3R = [
    [cell("F6"), cell("F7"), cell("F8"), cell("F9"), cell("F10"), cell(TR)],
    [cell("F16"), cell("F17"), cell("F18"), cell("F19"), cell("F20"), cell(TR)],
    [cell("DF(5)"), cell(TR,"Gui"), cell(TR,"Alt"), cell(TR,"Ctrl"), cell(TR,"Shift"), cell(TR)],
]
LAYERS.append(dict(title="Layer 3 — Function Keys (Green)", act="Activate: MO(1) + MO(3) or MO(4) + MO(3)",
                   L=L3L, R=L3R, LT=[cell(TR), cell(TR), cell(TR)], RT=[cell(TR), cell(TR), cell(TR)],
                   note="DF(5) = switch to RGB layer (right index, bottom row)"))

# ---- Layer 4 — Nav & Chords (Orange) ----
L4L = [
    [cell(TR), cell(""), cell(""), cell("⌘⇧5","shot","menu"), cell("⌘⇧3","shot","full"), cell("")],
    [cell(TR), cell("⌃⌘Spc","emoji","picker"), cell("⌘⇧.","hidden","files"),
     cell("⌘⇧4","shot","region"), cell("⌘⌥⇧V","paste-","match"), cell("⌃⌘Q","lock","screen")],
    trns_mod_row()[0],
]
L4R = [
    [cell(""), cell(""), cell(""), cell(""), cell(""), cell(TR)],
    [cell("←"), cell("↓"), cell("↑"), cell("→"), cell(""), cell(TR)],
    trns_mod_row()[1],
]
LAYERS.append(dict(title="Layer 4 — Nav & Chords (Orange)", act="Activate: hold right thumb MO(4)",
                   L=L4L, R=L4R, LT=[cell("MO(3)"), cell(TR), cell(TR)], RT=[cell(TR), cell(TR), cell(ACT)],
                   note="Left = chords · Right = vim arrows · MO(4)+MO(3) = Layer 3 · ⌘⌥⇧V = paste & match style"))

# ---- Layer 5 — System & Media (Red) ----
L5L = [
    [cell(""), cell("BOOT","flash"), cell("RGB","Tog"), cell("Mode","cycle"), cell("Hue+"), cell("Brt+")],
    [cell(""), cell(""), cell(""), cell("Hue-"), cell("Brt-"), cell("")],
    [cell(""), cell(""), cell(""), cell(""), cell(""), cell("")],
]
L5R = [
    [cell("☼ -","dim"), cell("☼ +","bright"), cell("⏮","prev"), cell("⏯","play"), cell("⏭","next"), cell("")],
    [cell("Mute"), cell("Vol-"), cell("Vol+"), cell(""), cell(""), cell("")],
    [cell(""), cell(""), cell(""), cell(""), cell(""), cell("")],
]
LAYERS.append(dict(title="Layer 5 — System & Media (Red)", act="Activate: DF(5) from Layer 3",
                   L=L5L, R=L5R, LT=[cell("DF(0)"), cell("DF(0)"), cell("DF(0)")], RT=[cell(""), cell(""), cell("")],
                   note="RGB slimmed to 6 controls · media + screen brightness fill the freed space · all three left thumbs return to base"))


def render_cell(c):
    main, subs = c
    if main == "":
        return '<td class="blank"></td>'
    cls = "k"
    if main == ACT:
        return '<td class="k act"></td>'
    if main in (TR, NO):
        cls += " dim"
    inner = f'<div class="m">{html.escape(main)}</div>'
    for s in subs:
        inner += f'<div class="s">{html.escape(s)}</div>'
    return f'<td class="{cls}">{inner}</td>'


def render_half(rows):
    out = '<table class="grid">'
    for row in rows:
        out += "<tr>" + "".join(render_cell(c) for c in row) + "</tr>"
    out += "</table>"
    return out


def render_thumb(thumbs, side):
    # left thumbs offset under inner 3 cols; right thumbs start at left edge
    pad = '<td class="pad"></td>' * 3 if side == "L" else ""
    out = '<table class="grid thumb">'
    out += "<tr>" + pad + "".join(render_cell(c) for c in thumbs) + "</tr>"
    out += "</table>"
    return out


def render_layer(ly, page_break=False):
    pb = ' style="break-before:page"' if page_break else ""
    h = f'<div class="layer"{pb}>'
    h += '<div class="ltitle"><span class="lt">' + html.escape(ly["title"]) + "</span>"
    if ly["act"]:
        h += '<span class="act-l">' + html.escape(ly["act"]) + "</span>"
    h += "</div>"
    h += '<div class="halves">'
    h += '<div class="half">' + render_half(ly["L"]) + render_thumb(ly["LT"], "L") + "</div>"
    h += '<div class="gap"></div>'
    h += '<div class="half">' + render_half(ly["R"]) + render_thumb(ly["RT"], "R") + "</div>"
    h += "</div>"
    if ly["note"]:
        h += '<div class="note">' + html.escape(ly["note"]) + "</div>"
    h += "</div>"
    return h


LEGEND = """
<div class="legend">
<div class="ltitle"><span class="lt">Legend</span></div>
<div class="legtext">
&#9661; = transparent (falls through to layer below)<br>
&#8709; = no-op (dead key, nothing happens)<br>
&#9618;&#9618; = layer is active from this key (held)<br>
Brt = brightness (value) &nbsp; Hue = color &nbsp; Mode = cycle RGB effect<br>
BOOT = enter bootloader for flashing &nbsp; Tog = toggle RGB on/off<br>
&#9788; -/&#9788; + = screen brightness &nbsp; &#9198; &#9199; &#9197; = media prev/play/next<br>
<br>
Bottom row mod-taps (Layer 0): hold for modifier, tap for letter.<br>
On transparent layers, bottom row mods fall through from Layer 0.<br>
<br>
RGB settings (brightness, saturation, effects) persist across all layers.<br>
Only the hue changes per layer.
</div>
<div class="ltitle" style="margin-top:18px"><span class="lt">36-key migration (in progress)</span></div>
<div class="legtext">
Goal: drop the outer pinky column on each side (3x6+3 &rarr; 3x5+3).<br>
Outer-column base keys are already re-homed so nothing is stranded:<br>
&nbsp;&nbsp;Tab, Esc &rarr; Layer 1 &nbsp; &middot; &nbsp; \\ &rarr; Layer 2 &nbsp; &middot; &nbsp; ' and " &rarr; Layer 2<br>
&nbsp;&nbsp;Left/Right Shift &rarr; bottom-row mod-taps on Z and /<br>
Layers 1&ndash;5 are now clear of the outer columns (Layer 5 RGB was rebuilt onto<br>
inner keys, so the outer-column RGB Toggle/Twinkle blockers are gone).<br>
Still to relocate before switching to LAYOUT_split_3x5_3:<br>
&nbsp;&nbsp;Base layer outer columns (rebuilt when the macro changes).
</div>
</div>
"""

CSS = """
@page { size: letter; margin: 14mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Courier New", monospace; color: #111; margin: 0; }
.head { font-size: 13px; }
.title { font-size: 15px; font-weight: bold; border-bottom: 2px solid #111;
         display: inline-block; padding-bottom: 2px; margin-bottom: 6px; }
.sub { font-size: 11px; color: #222; margin: 2px 0; }
.layer { margin-top: 14px; }
.ltitle { margin-bottom: 5px; display: flex; justify-content: space-between; align-items: baseline; }
.lt { font-size: 12.5px; border-bottom: 1px solid #111; padding-bottom: 1px; }
.act-l { font-size: 10.5px; color: #222; }
.halves { display: flex; align-items: flex-start; }
.gap { width: 26px; }
.half { display: inline-block; }
table.grid { border-collapse: collapse; }
table.thumb { margin-top: -1px; }
td.k { width: 50px; height: 40px; border: 1px solid #111; text-align: center;
       vertical-align: top; padding: 2px 1px; line-height: 1.05; }
td.k .m { font-size: 11px; }
td.k .s { font-size: 8px; color: #333; }
td.k.dim .m { color: #555; }
td.k.act { background-image: repeating-linear-gradient(45deg,#bbb 0 2px,#fff 2px 4px); }
td.blank { width: 50px; height: 40px; border: none; }
td.pad { width: 50px; height: 40px; border: none; }
.note { font-size: 10px; color: #222; text-align: center; margin-top: 6px; }
.legend { margin-top: 16px; }
.legtext { font-size: 11px; line-height: 1.45; }
"""

def main():
    body = '<div class="head">'
    body += '<div class="title">Corne (crkbd/rev1) — Kiron\'s Layout</div>'
    body += '<div class="sub">3x6+3 split keyboard · 6 layers · bottom row mods</div>'
    body += '<div class="sub">Hold a bottom row key for the modifier, tap for the letter.<br>'
    body += 'MO(n) = hold to activate layer n · DF(n) = switch default layer to n</div>'
    body += "</div>"
    for i, ly in enumerate(LAYERS):
        body += render_layer(ly, page_break=(i == 4))  # Layer 4 starts page 2
    body += LEGEND
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"

    chrome = find_chrome()
    if not chrome:
        sys.exit("Could not find Google Chrome / Chromium to render the PDF. "
                 "Install it or add its path to CHROME_CANDIDATES.")

    pdf_path = os.path.join(HERE, "layout.pdf")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(doc)
        html_path = f.name
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={pdf_path}", html_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    finally:
        os.unlink(html_path)
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
