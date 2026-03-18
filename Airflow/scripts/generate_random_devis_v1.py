import os
import re
import random
import unicodedata
from io import BytesIO
from dataclasses import dataclass
from datetime import datetime, timedelta

from faker import Faker
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


fake = Faker("fr_FR")


# ============================================================
# OUTILS
# ============================================================

def money(value):
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "entreprise"


def maybe(probability: float) -> bool:
    return random.random() < probability


def pick(*values):
    return random.choice(values)


def safe_filename(company_name: str) -> str:
    return f"{slugify(company_name)}_devis.pdf"


# ============================================================
# THÈMES
# ============================================================

@dataclass
class VisualTheme:
    name: str
    primary: object
    secondary: object
    light_bg: object
    border: object
    title_font: str
    body_font: str
    compact: bool
    margins_mm: tuple[int, int, int, int]
    title_size: int
    body_size: int
    use_accent_line: bool


def random_theme() -> VisualTheme:
    return random.choice([
        VisualTheme(
            name="classic_grey",
            primary=colors.HexColor("#333333"),
            secondary=colors.HexColor("#D9D9D9"),
            light_bg=colors.HexColor("#F7F7F7"),
            border=colors.black,
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=False,
            margins_mm=(14, 14, 12, 12),
            title_size=18,
            body_size=9,
            use_accent_line=False,
        ),
        VisualTheme(
            name="blue_modern",
            primary=colors.HexColor("#1F4E79"),
            secondary=colors.HexColor("#DCE6F1"),
            light_bg=colors.HexColor("#F8FBFE"),
            border=colors.HexColor("#1E1E1E"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=False,
            margins_mm=(12, 12, 10, 10),
            title_size=18,
            body_size=9,
            use_accent_line=True,
        ),
        VisualTheme(
            name="green_business",
            primary=colors.HexColor("#385723"),
            secondary=colors.HexColor("#E2EFDA"),
            light_bg=colors.HexColor("#FBFDF9"),
            border=colors.HexColor("#1A1A1A"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=True,
            margins_mm=(10, 10, 9, 9),
            title_size=16,
            body_size=8,
            use_accent_line=True,
        ),
        VisualTheme(
            name="dark_clean",
            primary=colors.HexColor("#2B2B2B"),
            secondary=colors.HexColor("#CCCCCC"),
            light_bg=colors.HexColor("#F2F2F2"),
            border=colors.HexColor("#111111"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=True,
            margins_mm=(10, 10, 9, 9),
            title_size=16,
            body_size=8,
            use_accent_line=False,
        ),
    ])


# ============================================================
# PROFIL DOCUMENT
# ============================================================

def generate_document_profile():
    doc_type = random.choices(
        population=["devis_strict", "devis_cabinet", "mini_devis"],
        weights=[0.35, 0.40, 0.25],
        k=1
    )[0]

    if doc_type == "mini_devis":
        return {
            "doc_type": doc_type,
            "with_cover_page": False,
            "with_company_box": True,
            "with_client_box": True,
            "with_reference_block": True,
            "with_signature_block": maybe(0.45),
            "with_payment_terms": maybe(0.60),
            "with_conditions_block": maybe(0.50),
            "with_notes_page": False,
            "with_narrative_intro": maybe(0.25),
            "with_discount_column": maybe(0.20),
            "with_tva_column": maybe(0.50),
            "with_remise_globale": maybe(0.20),
            "with_acompte": maybe(0.35),
            "with_scan_degradation": maybe(0.30),
            "show_zeros": False,
            "line_count": random.randint(4, 9),
        }

    if doc_type == "devis_strict":
        return {
            "doc_type": doc_type,
            "with_cover_page": maybe(0.20),
            "with_company_box": True,
            "with_client_box": True,
            "with_reference_block": True,
            "with_signature_block": maybe(0.75),
            "with_payment_terms": True,
            "with_conditions_block": True,
            "with_notes_page": maybe(0.35),
            "with_narrative_intro": maybe(0.30),
            "with_discount_column": maybe(0.40),
            "with_tva_column": True,
            "with_remise_globale": maybe(0.35),
            "with_acompte": maybe(0.50),
            "with_scan_degradation": maybe(0.45),
            "show_zeros": maybe(0.20),
            "line_count": random.randint(6, 16),
        }

    return {
        "doc_type": doc_type,
        "with_cover_page": maybe(0.45),
        "with_company_box": True,
        "with_client_box": True,
        "with_reference_block": True,
        "with_signature_block": maybe(0.80),
        "with_payment_terms": maybe(0.85),
        "with_conditions_block": maybe(0.75),
        "with_notes_page": maybe(0.45),
        "with_narrative_intro": maybe(0.55),
        "with_discount_column": maybe(0.55),
        "with_tva_column": maybe(0.70),
        "with_remise_globale": maybe(0.40),
        "with_acompte": maybe(0.55),
        "with_scan_degradation": maybe(0.30),
        "show_zeros": maybe(0.25),
        "line_count": random.randint(8, 20),
    }


# ============================================================
# DONNÉES SOCIÉTÉ / CLIENT
# ============================================================

def generate_company():
    return {
        "name": fake.company().upper(),
        "slug": slugify(fake.company()),
        "legal_form": pick("SARL", "SAS", "SASU", "EURL", "SA", "EI"),
        "siren": fake.siren(),
        "siret": f"{fake.siren()}00015",
        "ape": f"{random.randint(1000, 9999)}{pick('A', 'B', 'C', 'D', 'Z')}",
        "tva_intracom": f"FR{random.randint(10,99)}{fake.siren()}",
        "address": fake.address().replace("\n", ", "),
        "email": fake.company_email(),
        "phone": fake.phone_number(),
        "cabinet_name": pick(
            f"{fake.last_name().upper()} CONSEIL",
            f"{fake.last_name().upper()} SOLUTIONS",
            f"{fake.city().upper()} SERVICES",
            f"{fake.last_name().upper()} EXPERTISE",
        ),
        "header_variant": pick("classic", "modern", "institutional", "simple"),
    }


def generate_client():
    is_company = maybe(0.75)

    if is_company:
        return {
            "name": fake.company().upper(),
            "contact": fake.name(),
            "address": fake.address().replace("\n", ", "),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
        }

    return {
        "name": fake.name().upper(),
        "contact": fake.name(),
        "address": fake.address().replace("\n", ", "),
        "email": fake.email(),
        "phone": fake.phone_number(),
    }


# ============================================================
# LIGNES DE DEVIS
# ============================================================

SERVICE_CATALOG = [
    ("Audit infrastructure", "journée", (450, 1200), [20]),
    ("Déploiement solution SaaS", "forfait", (1200, 8500), [20]),
    ("Prestation de conseil", "heure", (80, 250), [20]),
    ("Maintenance préventive", "forfait", (300, 2500), [20]),
    ("Développement spécifique", "jour", (400, 900), [20]),
    ("Formation utilisateurs", "jour", (500, 1400), [20]),
    ("Accompagnement projet IA", "jour", (700, 1800), [20]),
    ("Intégration API", "forfait", (900, 6000), [20]),
    ("Étude technique", "forfait", (450, 3000), [20]),
    ("Support premium", "mois", (150, 900), [20]),
    ("Licence logicielle", "unité", (60, 650), [20]),
    ("Matériel bureautique", "unité", (45, 1200), [20]),
    ("Routeur / équipement réseau", "unité", (90, 1500), [20]),
    ("Transport / déplacement", "forfait", (30, 600), [10, 20]),
    ("Frais de livraison", "forfait", (15, 180), [20]),
    ("Impression / reprographie", "forfait", (20, 250), [20]),
]


def generate_quote_meta():
    base_date = fake.date_between(start_date="-120d", end_date="+20d")
    validity_days = pick(15, 30, 45, 60, 90)
    return {
        "quote_number": f"DV-{base_date.strftime('%Y')}-{random.randint(1000, 9999)}",
        "date": base_date.strftime("%d/%m/%Y"),
        "valid_until": (base_date + timedelta(days=validity_days)).strftime("%d/%m/%Y"),
        "object": pick(
            "Proposition commerciale",
            "Devis de prestation",
            "Devis de fourniture et services",
            "Offre commerciale",
            "Chiffrage projet",
        ),
        "site_reference": pick(
            "Ref. projet",
            "Référence dossier",
            "Référence client",
            "Réf. commerciale",
        ),
        "reference_value": f"{fake.bothify(text='??-#####').upper()}",
    }


def generate_quote_lines(profile):
    lines = []
    line_count = profile["line_count"]

    for _ in range(line_count):
        label_txt, unit, price_range, tva_choices = random.choice(SERVICE_CATALOG)
        qty = pick(
            random.randint(1, 3),
            random.randint(1, 5),
            round(random.uniform(1, 10), 1),
            round(random.uniform(0.5, 3), 1),
        )
        unit_price = round(random.uniform(price_range[0], price_range[1]), 2)
        discount_pct = pick(0, 0, 0, 5, 10, 15) if profile["with_discount_column"] else 0
        tva_pct = random.choice(tva_choices)
        description = pick(
            label_txt,
            f"{label_txt} - {fake.sentence(nb_words=4)}",
            f"{label_txt} ({fake.word().capitalize()})",
            label_txt,
        )

        total_ht = round(qty * unit_price * (1 - discount_pct / 100), 2)
        total_tva = round(total_ht * (tva_pct / 100), 2)
        total_ttc = round(total_ht + total_tva, 2)

        lines.append({
            "description": description,
            "unit": unit,
            "qty": qty,
            "unit_price": unit_price,
            "discount_pct": discount_pct,
            "tva_pct": tva_pct,
            "total_ht": total_ht,
            "total_tva": total_tva,
            "total_ttc": total_ttc,
        })

    return lines


def compute_totals(lines, profile):
    total_ht = round(sum(line["total_ht"] for line in lines), 2)
    total_tva = round(sum(line["total_tva"] for line in lines), 2)
    total_ttc = round(sum(line["total_ttc"] for line in lines), 2)

    remise_globale_pct = pick(0, 0, 0, 3, 5, 8) if profile["with_remise_globale"] else 0
    remise_globale = round(total_ht * remise_globale_pct / 100, 2)
    total_ht_after = round(total_ht - remise_globale, 2)
    total_tva_after = round(total_tva * (0 if total_ht == 0 else total_ht_after / total_ht), 2)
    total_ttc_after = round(total_ht_after + total_tva_after, 2)

    acompte_pct = pick(0, 0, 20, 30, 40, 50) if profile["with_acompte"] else 0
    acompte_amount = round(total_ttc_after * acompte_pct / 100, 2)

    return {
        "subtotal_ht": total_ht,
        "total_tva": total_tva,
        "total_ttc": total_ttc,
        "remise_globale_pct": remise_globale_pct,
        "remise_globale": remise_globale,
        "total_ht_after": total_ht_after,
        "total_tva_after": total_tva_after,
        "total_ttc_after": total_ttc_after,
        "acompte_pct": acompte_pct,
        "acompte_amount": acompte_amount,
    }


# ============================================================
# STYLES REPORTLAB
# ============================================================

def build_styles(theme: VisualTheme):
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName=theme.title_font,
        fontSize=theme.title_size,
        leading=theme.title_size + 3,
        alignment=TA_CENTER,
        textColor=theme.primary,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="SubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10 if not theme.compact else 9,
        alignment=TA_CENTER,
        textColor=theme.primary,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName=theme.body_font,
        fontSize=theme.body_size,
        leading=theme.body_size + 2,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="BodyRight",
        parent=styles["Normal"],
        fontName=theme.body_font,
        fontSize=theme.body_size,
        leading=theme.body_size + 2,
        alignment=TA_RIGHT,
    ))

    styles.add(ParagraphStyle(
        name="BodyCenter",
        parent=styles["Normal"],
        fontName=theme.body_font,
        fontSize=theme.body_size,
        leading=theme.body_size + 2,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=theme.body_size,
        leading=theme.body_size + 2,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="BodyBoldRight",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=theme.body_size,
        leading=theme.body_size + 2,
        alignment=TA_RIGHT,
    ))

    styles.add(ParagraphStyle(
        name="Tiny",
        parent=styles["Normal"],
        fontName=theme.body_font,
        fontSize=max(7, theme.body_size - 1),
        leading=max(9, theme.body_size + 1),
        alignment=TA_LEFT,
        textColor=colors.HexColor("#555555"),
    ))

    return styles


def P(text, style):
    return Paragraph(str(text), style)


# ============================================================
# BLOCS
# ============================================================

def apply_table_style(table, theme, compact=False):
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (-1, 0), theme.secondary),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3 if compact else 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 if compact else 5),
    ]))


def build_header(company, theme, styles):
    variant = company["header_variant"]

    if variant == "modern":
        left = f"<b>{company['cabinet_name']}</b><br/>Solutions & accompagnement"
        right = f"{company['name']}<br/>{company['email']}<br/>{company['phone']}"
    elif variant == "institutional":
        left = "DOCUMENT COMMERCIAL"
        right = f"{company['legal_form']} {company['name']}<br/>SIREN {company['siren']}"
    elif variant == "simple":
        left = company["name"]
        right = f"{company['phone']}<br/>{company['email']}"
    else:
        left = f"<b>{company['cabinet_name']}</b>"
        right = f"{company['name']}<br/>{company['address']}"

    logo_text = pick(company["cabinet_name"][:14], company["name"][:12], "DV", "QUOTE", "PRO")

    t = Table([[
        P(f"<b>{logo_text}</b>", styles["BodyCenter"]),
        P(left, styles["Body"]),
        P(right, styles["BodyRight"]),
    ]], colWidths=[25 * mm, 75 * mm, 75 * mm])

    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (0, 0), theme.secondary),
        ("BACKGROUND", (1, 0), (-1, 0), theme.light_bg),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def build_company_and_client_boxes(company, client, theme, styles):
    left = Table([
        [P("<b>Émetteur</b>", styles["BodyBold"])],
        [P(company["name"], styles["Body"])],
        [P(company["address"], styles["Body"])],
        [P(f"SIREN : {company['siren']}", styles["Body"])],
        [P(f"SIRET : {company['siret']}", styles["Body"])],
        [P(f"TVA : {company['tva_intracom']}", styles["Body"])],
        [P(company["email"], styles["Body"])],
        [P(company["phone"], styles["Body"])],
    ], colWidths=[85 * mm])

    right = Table([
        [P("<b>Client</b>", styles["BodyBold"])],
        [P(client["name"], styles["Body"])],
        [P(f"Contact : {client['contact']}", styles["Body"])],
        [P(client["address"], styles["Body"])],
        [P(client["email"], styles["Body"])],
        [P(client["phone"], styles["Body"])],
    ], colWidths=[85 * mm])

    for t in (left, right):
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
            ("BACKGROUND", (0, 0), (-1, 0), theme.secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

    big = Table([[left, right]], colWidths=[88 * mm, 88 * mm])
    big.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return big


def build_reference_block(meta, theme, styles):
    rows = [
        [P("<b>Devis n°</b>", styles["Body"]), P(meta["quote_number"], styles["Body"])],
        [P("<b>Date</b>", styles["Body"]), P(meta["date"], styles["Body"])],
        [P("<b>Validité</b>", styles["Body"]), P(meta["valid_until"], styles["Body"])],
        [P(f"<b>{meta['site_reference']}</b>", styles["Body"]), P(meta["reference_value"], styles["Body"])],
        [P("<b>Objet</b>", styles["Body"]), P(meta["object"], styles["Body"])],
    ]
    t = Table(rows, colWidths=[35 * mm, 60 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (0, -1), theme.secondary),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_intro_paragraph(styles):
    text = pick(
        "Nous vous remercions de votre intérêt et vous prions de trouver ci-dessous notre meilleure proposition commerciale.",
        "Suite à nos échanges, veuillez trouver notre devis détaillé correspondant à votre besoin.",
        "Conformément à votre demande, nous vous adressons le présent chiffrage pour validation.",
        "Nous vous prions de bien vouloir trouver notre offre de prix détaillée ci-après.",
    )
    return P(text, styles["Body"])


def build_lines_table(lines, theme, styles, profile):
    with_discount = profile["with_discount_column"]
    with_tva = profile["with_tva_column"]

    headers = [
        P("Description", styles["BodyBold"]),
        P("Qté", styles["BodyBoldRight"]),
        P("Unité", styles["BodyBold"]),
        P("PU HT", styles["BodyBoldRight"]),
    ]
    col_widths = [80 * mm, 18 * mm, 22 * mm, 24 * mm]

    if with_discount:
        headers.append(P("Remise %", styles["BodyBoldRight"]))
        col_widths.append(18 * mm)

    if with_tva:
        headers.append(P("TVA %", styles["BodyBoldRight"]))
        col_widths.append(16 * mm)

    headers.append(P("Total HT", styles["BodyBoldRight"]))
    col_widths.append(24 * mm)

    rows = [headers]

    for line in lines:
        row = [
            P(line["description"], styles["Body"]),
            P(str(line["qty"]).replace(".", ","), styles["BodyRight"]),
            P(line["unit"], styles["Body"]),
            P(money(line["unit_price"]), styles["BodyRight"]),
        ]

        if with_discount:
            row.append(P(str(line["discount_pct"]), styles["BodyRight"]))

        if with_tva:
            row.append(P(str(line["tva_pct"]), styles["BodyRight"]))

        row.append(P(money(line["total_ht"]), styles["BodyRight"]))
        rows.append(row)

    table = Table(rows, colWidths=col_widths, repeatRows=1)
    apply_table_style(table, theme, compact=theme.compact)
    return table


def build_totals_table(totals, theme, styles, profile):
    rows = [
        [P("Sous-total HT", styles["Body"]), P(money(totals["subtotal_ht"]), styles["BodyRight"])],
    ]

    if totals["remise_globale_pct"] > 0:
        rows.append([
            P(f"Remise globale ({totals['remise_globale_pct']}%)", styles["Body"]),
            P(f"- {money(totals['remise_globale'])}", styles["BodyRight"]),
        ])
        rows.append([
            P("Total HT après remise", styles["Body"]),
            P(money(totals["total_ht_after"]), styles["BodyRight"]),
        ])
    else:
        rows.append([
            P("Total HT", styles["Body"]),
            P(money(totals["total_ht_after"]), styles["BodyRight"]),
        ])

    rows.append([
        P("TVA", styles["Body"]),
        P(money(totals["total_tva_after"]), styles["BodyRight"]),
    ])
    rows.append([
        P("TOTAL TTC", styles["BodyBold"]),
        P(money(totals["total_ttc_after"]), styles["BodyBoldRight"]),
    ])

    if totals["acompte_pct"] > 0:
        rows.append([
            P(f"Acompte demandé ({totals['acompte_pct']}%)", styles["BodyBold"]),
            P(money(totals["acompte_amount"]), styles["BodyBoldRight"]),
        ])

    t = Table(rows, colWidths=[55 * mm, 35 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (0, -1), theme.secondary),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_payment_terms(styles):
    lines = [
        f"Mode de règlement : {pick('virement bancaire', 'chèque', 'CB', 'virement ou chèque')}",
        f"Délai de règlement : {pick('à réception', '30 jours fin de mois', '30 jours nets', '15 jours')}",
        f"Validité de l'offre : {pick('15 jours', '30 jours', '45 jours', '60 jours')}",
        f"Délai d'exécution estimé : {pick('5 jours ouvrés', '10 jours ouvrés', '2 semaines', '3 semaines', '1 mois')}",
    ]
    return [P(line, styles["Body"]) for line in lines]


def build_conditions_block(styles):
    lines = [
        "Le présent devis est établi sur la base des éléments communiqués à ce jour.",
        "Toute prestation supplémentaire fera l'objet d'un avenant ou d'un devis complémentaire.",
        "Les prix s'entendent hors prestations non explicitement mentionnées.",
        "La signature du devis vaut acceptation pleine et entière des conditions proposées.",
    ]
    return [P(line, styles["Tiny"]) for line in lines]


def build_signature_block(theme, styles):
    rows = [[
        P("<b>Bon pour accord</b><br/><br/>Nom / Cachet / Signature", styles["BodyCenter"]),
        P("<b>Date et signature</b><br/><br/>Précédé de la mention manuscrite", styles["BodyCenter"]),
    ]]
    t = Table(rows, colWidths=[85 * mm, 85 * mm], rowHeights=[30 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def build_notes_page(styles):
    notes = [
        "Détail des hypothèses de chiffrage",
        "Pré-requis techniques du client",
        "Exclusions de périmètre",
        "Calendrier prévisionnel et jalons",
        "Hypothèses d'installation ou de livraison",
    ]
    blocks = [P("<b>Annexe / Notes complémentaires</b>", styles["BodyBold"]), Spacer(1, 3 * mm)]
    for _ in range(random.randint(3, 6)):
        blocks.append(P(f"• {random.choice(notes)} : {fake.sentence(nb_words=12)}", styles["Body"]))
        blocks.append(Spacer(1, 2 * mm))
    return blocks


# ============================================================
# DÉGRADATION SCAN
# ============================================================

def _add_noise(image: Image.Image, amount: int = 10) -> Image.Image:
    noise = Image.effect_noise(image.size, amount)
    noise = noise.convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(1.8)
    return Image.blend(image.convert("L"), noise, alpha=0.08).convert("RGB")


def _degrade_page(img: Image.Image) -> Image.Image:
    angle = random.uniform(-1.1, 1.1)
    img = img.rotate(angle, expand=True, fillcolor="white")

    if maybe(0.55):
        img = ImageOps.grayscale(img).convert("RGB")

    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.9, 1.15))
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.96, 1.04))

    if maybe(0.40):
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.2, 0.6)))

    if maybe(0.75):
        img = _add_noise(img, amount=random.randint(6, 14))

    draw = ImageDraw.Draw(img)
    w, h = img.size
    if maybe(0.60):
        shade = random.randint(220, 245)
        draw.rectangle([0, 0, w, random.randint(8, 18)], fill=(shade, shade, shade))
        draw.rectangle([0, h - random.randint(8, 18), w, h], fill=(shade, shade, shade))

    if maybe(0.40):
        img = ImageOps.expand(img, border=random.randint(8, 16), fill=(240, 240, 240))

    return img


def degrade_pdf_to_scanned(pdf_path: str):
    if fitz is None:
        print("PyMuPDF non installé : scan dégradé ignoré.")
        return

    temp_path = pdf_path.replace(".pdf", "_scan_tmp.pdf")
    doc = fitz.open(pdf_path)
    out_pdf = fitz.open()

    try:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = _degrade_page(img)

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            rect = fitz.Rect(0, 0, img.width, img.height)
            new_page = out_pdf.new_page(width=img.width, height=img.height)
            new_page.insert_image(rect, stream=buf.getvalue())

        out_pdf.save(temp_path)

    finally:
        out_pdf.close()
        doc.close()

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    os.replace(temp_path, pdf_path)


# ============================================================
# DÉCORATION PAGE
# ============================================================

def draw_page_decorations(canvas_obj, doc, theme: VisualTheme, company: dict):
    page_num = canvas_obj.getPageNumber()
    canvas_obj.saveState()

    if theme.use_accent_line:
        canvas_obj.setStrokeColor(theme.primary)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(doc.leftMargin, A4[1] - doc.topMargin + 4, A4[0] - doc.rightMargin, A4[1] - doc.topMargin + 4)

    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(doc.leftMargin, 8 * mm, company["name"][:60])
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, 8 * mm, f"Page {page_num}")
    canvas_obj.restoreState()


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

def generate_random_devis(OUTPUT_DIR_JSON="output_test_devis"):
    os.makedirs(OUTPUT_DIR_JSON, exist_ok=True)

    theme = random_theme()
    profile = generate_document_profile()
    company = generate_company()
    client = generate_client()
    meta = generate_quote_meta()
    lines = generate_quote_lines(profile)
    totals = compute_totals(lines, profile)
    styles = build_styles(theme)

    filename = safe_filename(company["name"])
    output_path = os.path.join(OUTPUT_DIR_JSON, filename)

    left, right, top, bottom = theme.margins_mm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=left * mm,
        rightMargin=right * mm,
        topMargin=top * mm,
        bottomMargin=bottom * mm,
    )

    story = []

    if profile["with_cover_page"]:
        story.append(Spacer(1, 20 * mm))
        story.append(P(company["cabinet_name"], styles["DocTitle"]))
        story.append(P("Offre commerciale / Devis", styles["SubTitle"]))
        story.append(Spacer(1, 8 * mm))
        story.append(build_header(company, theme, styles))
        story.append(Spacer(1, 8 * mm))
        story.append(P(client["name"], styles["DocTitle"]))
        story.append(P(f"Devis n° {meta['quote_number']}", styles["SubTitle"]))
        story.append(PageBreak())

    story.append(P("DEVIS", styles["DocTitle"]))
    story.append(P(f"N° {meta['quote_number']} • {meta['date']}", styles["SubTitle"]))
    story.append(Spacer(1, 3 * mm))

    story.append(build_header(company, theme, styles))
    story.append(Spacer(1, 4 * mm))

    if profile["with_reference_block"]:
        story.append(build_reference_block(meta, theme, styles))
        story.append(Spacer(1, 4 * mm))
        story.append(build_company_and_client_boxes(company, client, theme, styles))
    else:
        story.append(build_company_and_client_boxes(company, client, theme, styles))

    story.append(Spacer(1, 4 * mm))

    if profile["with_narrative_intro"]:
        story.append(build_intro_paragraph(styles))
        story.append(Spacer(1, 4 * mm))

    story.append(build_lines_table(lines, theme, styles, profile))
    story.append(Spacer(1, 4 * mm))

    right_table = build_totals_table(totals, theme, styles, profile)
    totals_wrapper = Table([[Spacer(1, 1), right_table]], colWidths=[85 * mm, 90 * mm])
    totals_wrapper.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(totals_wrapper)
    story.append(Spacer(1, 4 * mm))

    if profile["with_payment_terms"]:
        story.append(P("<b>Conditions de règlement</b>", styles["BodyBold"]))
        for line in build_payment_terms(styles):
            story.append(line)
        story.append(Spacer(1, 4 * mm))

    if profile["with_conditions_block"]:
        story.append(P("<b>Conditions particulières</b>", styles["BodyBold"]))
        for line in build_conditions_block(styles):
            story.append(line)
        story.append(Spacer(1, 4 * mm))

    if profile["with_signature_block"]:
        story.append(build_signature_block(theme, styles))

    if profile["with_notes_page"]:
        story.append(PageBreak())
        story.extend(build_notes_page(styles))

    story.append(Spacer(1, 3 * mm))
    story.append(P(
        "Document fictif généré automatiquement pour tests d'extraction, OCR et classification.",
        styles["Tiny"],
    ))

    def _draw(canvas_obj, doc_obj):
        draw_page_decorations(canvas_obj, doc_obj, theme, company)

    doc.build(story, onFirstPage=_draw, onLaterPages=_draw)

    if profile["with_scan_degradation"]:
        degrade_pdf_to_scanned(output_path)

    print(f"PDF généré : {output_path}")
    print(f"Type : {profile['doc_type']}")
    print(f"Thème : {theme.name}")
    print(f"Lignes : {len(lines)}")
    print(f"Dégradé scan : {profile['with_scan_degradation']}")

    return output_path


if __name__ == "__main__":
    generate_random_devis()