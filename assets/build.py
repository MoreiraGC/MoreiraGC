"""Builds the profile header (assets/header-dark.svg, assets/header-light.svg).

GitHub shows SVGs as images: no web fonts and no scripts, but CSS animation inside the file plays.
So the text is drawn as outlines from the portfolio's own fonts (Archivo, JetBrains Mono), and the
black hole moves with plain CSS, which stops under prefers-reduced-motion.

    python3 assets/build.py [path/to/Portfolio/public/fonts]
"""
import random
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / 'www/Coddez/Portfolio/public/fonts')
OUT = Path(__file__).parent
W, H = 1600, 520


def load(name, axes=None):
    font = TTFont(FONTS / name)
    return instantiateVariableFont(font, axes) if axes else font


def text(font, s, size, x, y, track=0.0):
    """One SVG path for a line of text, baseline at y. Kerning is not applied."""
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
    scale = size / font['head'].unitsPerEm
    pen = SVGPathPen(glyphs, ntos=lambda n: f'{n:.1f}'.rstrip('0').rstrip('.'))
    cx = x
    for ch in s:
        name = cmap.get(ord(ch))
        if name is None:
            raise SystemExit(f'missing glyph {ch!r} in {font}')
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        cx += hmtx[name][0] * scale + track
    return pen.getCommands(), cx


ARCHIVO_BOLD = load('archivo-100_900-normal.woff2', {'wght': 700, 'wdth': 100})
ARCHIVO = load('archivo-100_900-normal.woff2', {'wght': 450, 'wdth': 100})
MONO = load('jetbrains-mono-400-normal.woff2')

THEMES = {
    'dark': dict(bg='#050507', ink='#ece8e1', muted='#8f8b86', accent='#ff7a3c', hot='#ffb35c', ring='#ffe2bd', hole='#000', star=0.55, glow=1.0),
    'light': dict(bg='#ece8e1', ink='#050507', muted='#55524d', accent='#d9531a', hot='#ff7a3c', ring='#ffb35c', hole='#050507', star=0.0, glow=0.55),
}

# The black hole: a disk seen nearly edge on, its far side lensed into an arc over the hole.
CX, CY, R, RX, RY, TILT = 1236, 262, 112, 300, 58, -7


def header(t):
    rnd = random.Random(7)
    stars = ''.join(
        f'<circle class="s s{i % 3}" cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.uniform(0.6, 1.7):.1f}"/>'
        for i in range(90)
    )
    lines = [
        (MONO, 'GMOREIRA.DEV', 19, 160, 3.4, t['accent']),
        (ARCHIVO_BOLD, 'Guilherme Moreira', 86, 252, -1.2, t['ink']),
        (ARCHIVO, 'Frontend-focused full-stack engineer', 31, 312, -0.2, t['ink']),
        (MONO, 'TypeScript · React · React Native', 21, 362, 0.4, t['muted']),
        (MONO, 'Remote from Goiânia, Brazil · open to full-time and contract roles', 17, 424, 0.2, t['muted']),
    ]
    words = ''
    for font, s, size, y, track, fill in lines:
        d, end = text(font, s, size, 96, y, track)
        assert end < CX - RX - 30 or y > CY + RY + 40, f'text runs into the black hole: {s!r} ends at {end:.0f}'
        words += f'<path fill="{fill}" d="{d}"/>'
    near = f'M{CX - RX},{CY} A{RX},{RY} 0 0 0 {CX + RX},{CY}'  # the half of the disk in front of the hole
    # The far side of the disk, lensed over the top: an arc around the hole that starts and ends where
    # the disk's far edge passes behind it.
    lr = R + 14
    ey = RY * (1 - (lr / RX) ** 2) ** 0.5
    ax = (lr ** 2 - ey ** 2) ** 0.5
    arc = f'M{CX - ax:.1f},{CY - ey:.1f} A{lr},{lr} 0 0 1 {CX + ax:.1f},{CY - ey:.1f}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Guilherme Moreira, frontend-focused full-stack engineer. TypeScript, React, React Native.">
<style>
  .s {{ fill: {t['ink']}; opacity: {t['star']}; animation: tw 5s ease-in-out infinite; }}
  .s1 {{ animation-delay: -1.7s; }} .s2 {{ animation-delay: -3.3s; }}
  .flow {{ stroke-dasharray: 26 70; opacity: 0.55; animation: flow 4.5s linear infinite; }}
  .arc {{ animation: breathe 6s ease-in-out infinite; }}
  .ring {{ animation: breathe 6s ease-in-out infinite reverse; }}
  @keyframes tw {{ 50% {{ opacity: {t['star'] * 0.25:.2f}; }} }}
  @keyframes flow {{ to {{ stroke-dashoffset: -250; }} }}
  @keyframes breathe {{ 50% {{ opacity: 0.72; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<defs>
  <linearGradient id="disk" x1="0" x2="1">
    <stop offset="0" stop-color="{t['accent']}" stop-opacity="0.15"/>
    <stop offset="0.35" stop-color="{t['hot']}"/>
    <stop offset="0.65" stop-color="{t['hot']}"/>
    <stop offset="1" stop-color="{t['accent']}" stop-opacity="0.15"/>
  </linearGradient>
  <filter id="glow" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="{10 * t['glow']:.1f}"/></filter>
  <filter id="soft" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="{3 * t['glow']:.1f}"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<g>{stars}</g>
<g transform="rotate({TILT} {CX} {CY})">
  <ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="url(#disk)" stroke-width="30" opacity="{0.55 * t['glow'] + 0.2:.2f}" filter="url(#glow)"/>
  <ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="url(#disk)" stroke-width="7"/>
  <path class="arc" d="{arc}" fill="none" stroke="{t['hot']}" stroke-width="26" opacity="{0.6 * t['glow'] + 0.2:.2f}" filter="url(#glow)"/>
  <path class="arc" d="{arc}" fill="none" stroke="{t['hot']}" stroke-width="10" stroke-linecap="round"/>
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="{t['hole']}"/>
  <circle class="ring" cx="{CX}" cy="{CY}" r="{R + 3}" fill="none" stroke="{t['ring']}" stroke-width="3" filter="url(#soft)"/>
  <circle cx="{CX}" cy="{CY}" r="{R + 3}" fill="none" stroke="{t['ring']}" stroke-width="1.5"/>
  <path d="{near}" fill="none" stroke="url(#disk)" stroke-width="30" opacity="{0.55 * t['glow'] + 0.2:.2f}" filter="url(#glow)"/>
  <path d="{near}" fill="none" stroke="url(#disk)" stroke-width="9"/>
  <path class="flow" d="{near}" fill="none" stroke="{t['ring']}" stroke-width="4" stroke-linecap="round" filter="url(#soft)"/>
</g>
{words}
</svg>
'''


for name, t in THEMES.items():
    (OUT / f'header-{name}.svg').write_text(header(t))
    print('wrote', OUT / f'header-{name}.svg', f"{(OUT / f'header-{name}.svg').stat().st_size // 1024} KB")
