"""Dessine le calendrier des contributions de la dernière année en SVG."""
import json
import sys
import urllib.request
from datetime import date

UTILISATEUR = sys.argv[1]
SORTIE = sys.argv[2]

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
        "juil.", "août", "sept.", "oct.", "nov.", "déc."]
# Même dégradé que le portfolio : vide, puis 30 %, 55 %, 80 %, 100 % de la couleur principale
NIVEAUX = ["#161b22", "#1E90FF4D", "#1E90FF8C", "#1E90FFCC", "#1E90FF"]
CASE, PAS = 11, 14
MARGE_G, MARGE_H = 40, 50


def niveau(n, maxi):
    if n == 0:
        return 0
    r = n / maxi
    return 1 if r < .12 else 2 if r < .3 else 3 if r < .55 else 4


url = f"https://github-contributions-api.jogruber.de/v4/{UTILISATEUR}?y=last"
with urllib.request.urlopen(url, timeout=30) as rep:
    donnees = json.load(rep)

jours = donnees["contributions"]
total = donnees["total"]["lastYear"]
maxi = max([j["count"] for j in jours] + [1])

# Colonnes de 7 jours, la semaine commence le dimanche comme sur GitHub
decalage = (date.fromisoformat(jours[0]["date"]).weekday() + 1) % 7
cases = [None] * decalage + jours
semaines = [cases[i:i + 7] for i in range(0, len(cases), 7)]

largeur = MARGE_G + len(semaines) * PAS + 20
hauteur = MARGE_H + 7 * PAS + 40
total_txt = f"{total:,}".replace(",", " ")

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{hauteur}" '
       f'viewBox="0 0 {largeur} {hauteur}" font-family="Segoe UI, Ubuntu, sans-serif">',
       '<style>.c{opacity:0;transform-box:fill-box;transform-origin:center;'
       'animation:pop .5s cubic-bezier(.2,.8,.3,1.4) forwards}'
       '@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}'
       '.t{animation:fade 1s ease-out both}@keyframes fade{from{opacity:0}to{opacity:1}}</style>',
       f'<rect width="100%" height="100%" rx="6" fill="#0d1117"/>',
       f'<text x="{MARGE_G}" y="26" fill="#1E90FF" font-size="16" font-weight="600" class="t">'
       f'{total_txt} contributions sur la dernière année</text>']

mois_prec, derniere_col = -1, -10
for col, semaine in enumerate(semaines):
    premier = next((j for j in semaine if j), None)
    if premier:
        m = date.fromisoformat(premier["date"]).month - 1
        if m != mois_prec and col - derniere_col > 2:
            svg.append(f'<text x="{MARGE_G + col * PAS}" y="{MARGE_H - 8}" fill="#8b949e" '
                       f'font-size="10">{MOIS[m]}</text>')
            derniere_col = col
        mois_prec = m
    for lig, jour in enumerate(semaine):
        if not jour:
            continue
        n = jour["count"]
        svg.append(f'<rect x="{MARGE_G + col * PAS}" y="{MARGE_H + lig * PAS}" width="{CASE}" '
                   f'height="{CASE}" rx="3" fill="{NIVEAUX[niveau(n, maxi)]}" class="c" '
                   f'style="animation-delay:{col * 25 + lig * 35}ms">'
                   f'<title>{n} contribution{"s" if n > 1 else ""} · {jour["date"]}</title></rect>')

for lig, nom in ((1, "lun"), (3, "mer"), (5, "ven")):
    svg.append(f'<text x="10" y="{MARGE_H + lig * PAS + 9}" fill="#8b949e" font-size="10">{nom}</text>')

# Légende « Moins … Plus » en bas à droite
y = MARGE_H + 7 * PAS + 14
x = largeur - 20 - 5 * PAS - 34
svg.append(f'<text x="{x - 36}" y="{y + 9}" fill="#8b949e" font-size="10">Moins</text>')
for i, c in enumerate(NIVEAUX):
    svg.append(f'<rect x="{x + i * PAS}" y="{y}" width="{CASE}" height="{CASE}" rx="3" fill="{c}"/>')
svg.append(f'<text x="{x + 5 * PAS + 4}" y="{y + 9}" fill="#8b949e" font-size="10">Plus</text>')
svg.append('</svg>')

with open(SORTIE, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
