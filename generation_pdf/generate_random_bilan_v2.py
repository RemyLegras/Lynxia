import os
import re
import math
import random
import unicodedata
from io import BytesIO
from dataclasses import dataclass
from datetime import datetime

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
# OUTILS GÉNÉRAUX
# ============================================================

def money(value: int | float | None) -> str:
    if value is None:
        return ""
    return f"{int(round(value)):,.0f}".replace(",", " ")


def money_signed(value: int | float | None) -> str:
    if value is None:
        return ""
    sign = "-" if value < 0 else ""
    return f"{sign}{money(abs(value))}"


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


def random_date_label():
    return pick(
        "Exercice clos le",
        "Clôture au",
        "Arrêté des comptes au",
        "Situation arrêtée au",
    )


def pct(base: int, low: float, high: float) -> int:
    return int(base * random.uniform(low, high))


def split_n_n1(value: int, variance=0.30) -> tuple[int, int]:
    n = value
    factor = random.uniform(1 - variance, 1 + variance)
    n1 = int(round(value / factor)) if value != 0 else 0
    return n, n1


def safe_filename(company_name: str) -> str:
    return f"{slugify(company_name)}_bilan.pdf"


# ============================================================
# THÈMES VISUELS
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
    margins_mm: tuple[int, int, int, int]  # left, right, top, bottom
    title_size: int
    body_size: int
    use_accent_lines: bool


def random_theme() -> VisualTheme:
    themes = [
        VisualTheme(
            name="grey_classic",
            primary=colors.HexColor("#333333"),
            secondary=colors.HexColor("#D9D9D9"),
            light_bg=colors.HexColor("#F5F5F5"),
            border=colors.black,
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=False,
            margins_mm=(15, 15, 12, 12),
            title_size=17,
            body_size=9,
            use_accent_lines=False,
        ),
        VisualTheme(
            name="blue_firm",
            primary=colors.HexColor("#1F4E79"),
            secondary=colors.HexColor("#DCE6F1"),
            light_bg=colors.HexColor("#F8FBFE"),
            border=colors.HexColor("#1A1A1A"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=False,
            margins_mm=(14, 14, 10, 12),
            title_size=18,
            body_size=9,
            use_accent_lines=True,
        ),
        VisualTheme(
            name="green_office",
            primary=colors.HexColor("#385723"),
            secondary=colors.HexColor("#E2EFDA"),
            light_bg=colors.HexColor("#FBFDF9"),
            border=colors.HexColor("#222222"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=True,
            margins_mm=(12, 12, 10, 10),
            title_size=16,
            body_size=8,
            use_accent_lines=True,
        ),
        VisualTheme(
            name="dark_modern",
            primary=colors.HexColor("#2D2D2D"),
            secondary=colors.HexColor("#CFCFCF"),
            light_bg=colors.HexColor("#F3F3F3"),
            border=colors.HexColor("#111111"),
            title_font="Helvetica-Bold",
            body_font="Helvetica",
            compact=True,
            margins_mm=(10, 10, 9, 9),
            title_size=16,
            body_size=8,
            use_accent_lines=False,
        ),
    ]
    return random.choice(themes)


# ============================================================
# ENTREPRISE / CABINET
# ============================================================

def generate_company():
    end_date = fake.date_between(start_date="-3y", end_date="today")
    year_n = int(end_date.strftime("%Y"))
    company = fake.company().upper()
    legal_form = pick("SARL", "SAS", "SASU", "EURL", "SA")

    return {
        "name": company,
        "slug": slugify(company),
        "legal_form": legal_form,
        "capital_social": pick(1000, 5000, 10000, 15000, 30000, 50000, 80000, 120000),
        "siren": fake.siren(),
        "siret": f"{fake.siren()}00015",
        "ape": f"{random.randint(1000, 9999)}{pick('A', 'B', 'C', 'D', 'Z')}",
        "rcs_city": fake.city().upper(),
        "address": fake.address().replace("\n", ", "),
        "closing_date": end_date.strftime("%d/%m/%Y"),
        "exercise_n": str(year_n),
        "exercise_n1": str(year_n - 1),
        "cabinet_name": pick(
            f"Cabinet {fake.last_name().upper()} & Associés",
            f"{fake.last_name().upper()} Expertise",
            f"{fake.last_name().upper()} Audit Conseil",
            f"AGC {fake.city().upper()}",
            f"{fake.last_name().upper()} Comptabilité",
        ),
        "cabinet_tagline": pick(
            "Expertise comptable • Audit • Conseil",
            "Cabinet d'expertise comptable",
            "Comptabilité, social et fiscal",
            "Audit • Comptabilité • Gestion",
        ),
        "header_variant": pick(
            "registres",
            "cabinet",
            "simple",
            "institutional",
        ),
    }


# ============================================================
# DONNÉES COMPTABLES
# ============================================================

def generate_accounting_data():
    # Actif
    imm_incorp = pick(0, 0, 800, 1500, 2500, 4000, 8000, 12000)
    imm_corp = random.randint(12000, 280000)
    imm_fin = pick(0, 0, 0, 1000, 2500, 6000, 12000, 25000)

    stocks = pick(0, 0, 0, 2500, 5000, 8000, 12000, 20000)
    creances_clients = random.randint(0, 90000)
    autres_creances = random.randint(0, 30000)
    vmp = pick(0, 0, 0, 1500, 5000, 10000)
    disponibilites_banque = random.randint(2000, 120000)
    disponibilites_caisse = pick(0, 0, 50, 100, 200, 350, 500)
    cca = pick(0, 0, 0, 500, 1000, 1800, 2500)

    total_immobilise = imm_incorp + imm_corp + imm_fin
    total_circulant = (
            stocks + creances_clients + autres_creances + vmp
            + disponibilites_banque + disponibilites_caisse + cca
    )
    total_actif = total_immobilise + total_circulant

    # Passif
    capital = pick(1000, 5000, 10000, 15000, 30000, 50000, 100000)
    reserve_legale = pick(0, 500, 1000, 2000, 5000, 8000)
    autres_reserves = random.randint(0, 50000)
    report_nouveau = random.randint(-10000, 35000)

    # Compte de résultat
    ca_marchandises = pick(0, 0, 0, random.randint(20000, 250000))
    ca_services = random.randint(40000, 1500000)
    chiffre_affaires = ca_marchandises + ca_services

    production_stockee = pick(0, 0, 0, 500, 1500, 4000)
    autres_produits = pick(0, 0, 500, 1200, 3000, 8000)
    produits_financiers = pick(0, 0, 0, 100, 250, 500, 1200)
    produits_exceptionnels = pick(0, 0, 0, 600, 1500, 5000, 12000)

    achats = pct(chiffre_affaires, 0.10, 0.38)
    variation_stock = pick(-800, -300, 0, 0, 0, 300, 900)
    charges_externes = pct(chiffre_affaires, 0.08, 0.25)
    impots_taxes = pct(chiffre_affaires, 0.01, 0.05)
    salaires = pct(chiffre_affaires, 0.06, 0.28)
    charges_sociales = pct(salaires, 0.28, 0.52)
    dot_amort = pick(500, 1200, 2500, 5000, 9000, 15000)
    dot_prov = pick(0, 0, 0, 200, 800, 1800)
    autres_charges = pick(0, 0, 300, 800, 1500, 5000)
    charges_financieres = pick(0, 0, 0, 100, 300, 900, 2500)
    charges_exceptionnelles = pick(0, 0, 0, 300, 1200, 2500, 7000)

    total_produits = (
            chiffre_affaires + production_stockee + autres_produits
            + produits_financiers + produits_exceptionnels
    )
    total_charges = (
            achats + variation_stock + charges_externes + impots_taxes
            + salaires + charges_sociales + dot_amort + dot_prov
            + autres_charges + charges_financieres + charges_exceptionnelles
    )
    resultat = total_produits - total_charges

    total_capitaux_propres = capital + reserve_legale + autres_reserves + report_nouveau + resultat

    remaining = total_actif - total_capitaux_propres
    if remaining < 1000:
        autres_reserves = max(0, autres_reserves - (1000 - remaining))
        total_capitaux_propres = capital + reserve_legale + autres_reserves + report_nouveau + resultat
        remaining = total_actif - total_capitaux_propres

    emprunts = int(remaining * random.uniform(0.18, 0.55))
    dettes_fournisseurs = int((remaining - emprunts) * random.uniform(0.18, 0.45))
    dettes_fiscales_sociales = int((remaining - emprunts - dettes_fournisseurs) * random.uniform(0.18, 0.55))
    autres_dettes = remaining - emprunts - dettes_fournisseurs - dettes_fiscales_sociales

    total_dettes = emprunts + dettes_fournisseurs + dettes_fiscales_sociales + autres_dettes
    total_passif = total_capitaux_propres + total_dettes

    diff = total_actif - total_passif
    autres_dettes += diff
    total_dettes = emprunts + dettes_fournisseurs + dettes_fiscales_sociales + autres_dettes
    total_passif = total_capitaux_propres + total_dettes

    actif = {
        "immobilisations_incorporelles": imm_incorp,
        "immobilisations_corporelles": imm_corp,
        "immobilisations_financieres": imm_fin,
        "total_immobilise": total_immobilise,
        "stocks": stocks,
        "creances_clients": creances_clients,
        "autres_creances": autres_creances,
        "valeurs_mobilieres_placement": vmp,
        "disponibilites_banque": disponibilites_banque,
        "disponibilites_caisse": disponibilites_caisse,
        "charges_constatees_avance": cca,
        "total_circulant": total_circulant,
        "total_actif": total_actif,
    }

    passif = {
        "capital": capital,
        "reserve_legale": reserve_legale,
        "autres_reserves": autres_reserves,
        "report_nouveau": report_nouveau,
        "resultat": resultat,
        "total_capitaux_propres": total_capitaux_propres,
        "emprunts": emprunts,
        "dettes_fournisseurs": dettes_fournisseurs,
        "dettes_fiscales_sociales": dettes_fiscales_sociales,
        "autres_dettes": autres_dettes,
        "total_dettes": total_dettes,
        "total_passif": total_passif,
    }

    resultat_data = {
        "ca_marchandises": ca_marchandises,
        "ca_services": ca_services,
        "chiffre_affaires": chiffre_affaires,
        "production_stockee": production_stockee,
        "autres_produits": autres_produits,
        "produits_financiers": produits_financiers,
        "produits_exceptionnels": produits_exceptionnels,
        "achats": achats,
        "variation_stock": variation_stock,
        "charges_externes": charges_externes,
        "impots_taxes": impots_taxes,
        "salaires": salaires,
        "charges_sociales": charges_sociales,
        "dotations_amortissements": dot_amort,
        "dotations_provisions": dot_prov,
        "autres_charges": autres_charges,
        "charges_financieres": charges_financieres,
        "charges_exceptionnelles": charges_exceptionnelles,
        "total_produits": total_produits,
        "total_charges": total_charges,
        "benefice_ou_perte": resultat,
    }

    return {
        "actif": actif,
        "passif": passif,
        "resultat": resultat_data,
    }


# ============================================================
# PROFIL DOCUMENT
# ============================================================

def generate_document_profile():
    doc_type = random.choices(
        population=["dgfip_strict", "cabinet_report", "mini_bilan"],
        weights=[0.35, 0.40, 0.25],
        k=1
    )[0]

    if doc_type == "mini_bilan":
        return {
            "doc_type": doc_type,
            "with_cover_page": maybe(0.15),
            "with_header_box": True,
            "with_footer_note": maybe(0.70),
            "with_annexes": False,
            "with_immobilisations": False,
            "with_amortissements": False,
            "with_provisions": False,
            "with_echeances": False,
            "with_detail_exceptionnel": False,
            "with_n1_column": maybe(0.40),
            "show_codes": False,
            "show_zeros": maybe(0.25),
            "degrade_scan": maybe(0.35),
            "section_order": ["bilan", "resultat"],
            "title_variant": pick("BILAN COMPTABLE", "COMPTES ANNUELS", "BILAN - ACTIF / PASSIF"),
        }

    if doc_type == "dgfip_strict":
        order = ["bilan", "resultat", "immobilisations", "amortissements", "echeances"]
        if maybe(0.45):
            order.append("provisions")
        if maybe(0.30):
            order.append("detail_exceptionnel")
        return {
            "doc_type": doc_type,
            "with_cover_page": maybe(0.40),
            "with_header_box": True,
            "with_footer_note": maybe(0.90),
            "with_annexes": True,
            "with_immobilisations": True,
            "with_amortissements": True,
            "with_provisions": maybe(0.55),
            "with_echeances": True,
            "with_detail_exceptionnel": maybe(0.40),
            "with_n1_column": maybe(0.90),
            "show_codes": maybe(0.75),
            "show_zeros": maybe(0.20),
            "degrade_scan": maybe(0.45),
            "section_order": order,
            "title_variant": pick("LIASSE FISCALE", "COMPTES ANNUELS", "BILAN - ACTIF / PASSIF"),
        }

    # cabinet_report
    order_options = [
        ["bilan", "resultat", "immobilisations", "echeances"],
        ["resultat", "bilan", "amortissements", "detail_exceptionnel"],
        ["bilan", "resultat", "provisions", "immobilisations"],
        ["bilan", "resultat"],
    ]
    return {
        "doc_type": doc_type,
        "with_cover_page": maybe(0.65),
        "with_header_box": maybe(0.85),
        "with_footer_note": maybe(0.90),
        "with_annexes": maybe(0.75),
        "with_immobilisations": maybe(0.65),
        "with_amortissements": maybe(0.55),
        "with_provisions": maybe(0.40),
        "with_echeances": maybe(0.50),
        "with_detail_exceptionnel": maybe(0.35),
        "with_n1_column": maybe(0.70),
        "show_codes": maybe(0.35),
        "show_zeros": maybe(0.35),
        "degrade_scan": maybe(0.30),
        "section_order": random.choice(order_options),
        "title_variant": pick("RAPPORT COMPTABLE", "DOCUMENTS COMPTABLES", "COMPTES ANNUELS"),
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
        leading=theme.title_size + 4,
        alignment=TA_CENTER,
        textColor=theme.primary,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10 if not theme.compact else 9,
        leading=12,
        alignment=TA_CENTER,
        textColor=theme.primary,
        spaceAfter=4,
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
# EN-TÊTES / LOGO
# ============================================================

def build_header_block(company, theme, styles, profile):
    variant = company["header_variant"]

    if variant == "cabinet":
        left = f"<b>{company['cabinet_name']}</b><br/>{company['cabinet_tagline']}"
        right = (
            f"<b>{company['name']}</b><br/>"
            f"SIREN : {company['siren']}<br/>"
            f"Clôture : {company['closing_date']}"
        )
    elif variant == "registres":
        left = "REGISTRE DU COMMERCE ET DES SOCIÉTÉS"
        right = (
            f"{company['name']}<br/>"
            f"RCS {company['rcs_city']} • {company['siren']}"
        )
    elif variant == "institutional":
        left = "DOCUMENTS COMPTABLES ANNUELS"
        right = (
            f"{company['legal_form']} {company['name']}<br/>"
            f"SIRET : {company['siret']}"
        )
    else:
        left = company["cabinet_name"]
        right = f"{company['name']}<br/>{company['closing_date']}"

    logo_text = pick(
        company["cabinet_name"][:18],
        company["name"][:16],
        "EC",
        "AC",
        "CABINET",
    )

    data = [
        [
            P(f"<b>{logo_text}</b>", styles["BodyCenter"]),
            P(left, styles["Body"]),
            P(right, styles["BodyRight"]),
        ]
    ]

    t = Table(data, colWidths=[25 * mm, 75 * mm, 75 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (0, 0), theme.secondary),
        ("BACKGROUND", (1, 0), (-1, 0), theme.light_bg),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_company_box(company, theme, styles, profile):
    rows = [
        [
            P(f"<b>Dénomination :</b> {company['name']}", styles["Body"]),
            P(f"<b>Forme :</b> {company['legal_form']}", styles["Body"]),
        ],
        [
            P(f"<b>SIREN :</b> {company['siren']}", styles["Body"]),
            P(f"<b>SIRET :</b> {company['siret']}", styles["Body"]),
        ],
        [
            P(f"<b>Adresse :</b> {company['address']}", styles["Body"]),
            P(f"<b>Code APE :</b> {company['ape']}", styles["Body"]),
        ],
        [
            P(f"<b>RCS :</b> {company['rcs_city']}", styles["Body"]),
            P(f"<b>Capital social :</b> {money(company['capital_social'])} €", styles["Body"]),
        ],
    ]
    t = Table(rows, colWidths=[100 * mm, 75 * mm])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (-1, -1), theme.light_bg),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ============================================================
# LIBELLÉS ALTERNATIFS
# ============================================================

LABEL_VARIANTS = {
    "immobilisations_incorporelles": ["Immobilisations incorporelles", "Immobilisations incorp."],
    "immobilisations_corporelles": ["Immobilisations corporelles", "Immobilisations corp."],
    "immobilisations_financieres": ["Immobilisations financières", "Immobilisations fin."],
    "stocks": ["Stocks", "Stocks et en-cours"],
    "creances_clients": ["Créances clients", "Clients et comptes rattachés"],
    "autres_creances": ["Autres créances", "Autres créances d'exploitation"],
    "valeurs_mobilieres_placement": ["Valeurs mobilières de placement", "V.M.P."],
    "disponibilites_banque": ["Disponibilités en banque", "Banques"],
    "disponibilites_caisse": ["Disponibilités en caisse", "Caisse"],
    "charges_constatees_avance": ["Charges constatées d'avance", "CCA"],
    "reserve_legale": ["Réserve légale", "Réserve légale"],
    "autres_reserves": ["Autres réserves", "Réserves"],
    "report_nouveau": ["Report à nouveau", "Report à nouveau"],
    "emprunts": ["Emprunts", "Emprunts et dettes assimilées"],
    "dettes_fournisseurs": ["Dettes fournisseurs", "Fournisseurs et comptes rattachés"],
    "dettes_fiscales_sociales": ["Dettes fiscales et sociales", "Dettes fiscales / sociales"],
    "autres_dettes": ["Autres dettes", "Autres dettes d'exploitation"],
}


def label(key: str) -> str:
    return random.choice(LABEL_VARIANTS.get(key, [key]))


def maybe_amount(value: int, profile: dict) -> str:
    if value == 0 and not profile["show_zeros"]:
        return ""
    return money(value)


# ============================================================
# TABLES
# ============================================================

def style_for_table(t, theme, compact=False):
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (-1, 0), theme.secondary),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3 if compact else 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 if compact else 5),
    ]))


def build_bilan_table(data, theme, styles, profile, company):
    a = data["actif"]
    p = data["passif"]
    with_n1 = profile["with_n1_column"]

    if with_n1:
        headers = [
            P("ACTIF", styles["BodyBold"]),
            P(company["exercise_n"], styles["BodyBoldRight"]),
            P(company["exercise_n1"], styles["BodyBoldRight"]),
            P("PASSIF", styles["BodyBold"]),
            P(company["exercise_n"], styles["BodyBoldRight"]),
            P(company["exercise_n1"], styles["BodyBoldRight"]),
        ]
        rows = [headers]

        items_left = [
            ("immobilisations_incorporelles", a["immobilisations_incorporelles"]),
            ("immobilisations_corporelles", a["immobilisations_corporelles"]),
            ("immobilisations_financieres", a["immobilisations_financieres"]),
            ("stocks", a["stocks"]),
            ("creances_clients", a["creances_clients"]),
            ("autres_creances", a["autres_creances"]),
            ("valeurs_mobilieres_placement", a["valeurs_mobilieres_placement"]),
            ("disponibilites_banque", a["disponibilites_banque"]),
            ("disponibilites_caisse", a["disponibilites_caisse"]),
            ("charges_constatees_avance", a["charges_constatees_avance"]),
        ]
        items_right = [
            ("capital", p["capital"]),
            ("reserve_legale", p["reserve_legale"]),
            ("autres_reserves", p["autres_reserves"]),
            ("report_nouveau", p["report_nouveau"]),
            ("resultat", p["resultat"]),
            ("emprunts", p["emprunts"]),
            ("dettes_fournisseurs", p["dettes_fournisseurs"]),
            ("dettes_fiscales_sociales", p["dettes_fiscales_sociales"]),
            ("autres_dettes", p["autres_dettes"]),
        ]

        max_len = max(len(items_left), len(items_right))
        for i in range(max_len):
            left_row = items_left[i] if i < len(items_left) else ("", 0)
            right_row = items_right[i] if i < len(items_right) else ("", 0)

            ln, ln1 = split_n_n1(left_row[1])
            rn, rn1 = split_n_n1(right_row[1])

            rows.append([
                P(label(left_row[0]) if left_row[0] else "", styles["Body"]),
                P(maybe_amount(ln, profile) if left_row[0] else "", styles["BodyRight"]),
                P(maybe_amount(ln1, profile) if left_row[0] else "", styles["BodyRight"]),
                P(label(right_row[0]) if right_row[0] else "", styles["Body"]),
                P(maybe_amount(rn, profile) if right_row[0] else "", styles["BodyRight"]),
                P(maybe_amount(rn1, profile) if right_row[0] else "", styles["BodyRight"]),
            ])

        tot_act_n, tot_act_n1 = split_n_n1(a["total_actif"])
        tot_pas_n, tot_pas_n1 = split_n_n1(p["total_passif"])
        rows.append([
            P("TOTAL DE L'ACTIF", styles["BodyBold"]),
            P(money(tot_act_n), styles["BodyBoldRight"]),
            P(money(tot_act_n1), styles["BodyBoldRight"]),
            P("TOTAL DU PASSIF", styles["BodyBold"]),
            P(money(tot_pas_n), styles["BodyBoldRight"]),
            P(money(tot_pas_n1), styles["BodyBoldRight"]),
        ])

        t = Table(rows, colWidths=[51 * mm, 18 * mm, 18 * mm, 51 * mm, 18 * mm, 18 * mm])
        style_for_table(t, theme, compact=theme.compact)
        return t

    rows = [
        [
            P("ACTIF", styles["BodyBold"]),
            P("Montant", styles["BodyBoldRight"]),
            P("PASSIF", styles["BodyBold"]),
            P("Montant", styles["BodyBoldRight"]),
        ]
    ]

    left_items = [
        ("immobilisations_incorporelles", a["immobilisations_incorporelles"]),
        ("immobilisations_corporelles", a["immobilisations_corporelles"]),
        ("immobilisations_financieres", a["immobilisations_financieres"]),
        ("stocks", a["stocks"]),
        ("creances_clients", a["creances_clients"]),
        ("autres_creances", a["autres_creances"]),
        ("valeurs_mobilieres_placement", a["valeurs_mobilieres_placement"]),
        ("disponibilites_banque", a["disponibilites_banque"]),
        ("disponibilites_caisse", a["disponibilites_caisse"]),
        ("charges_constatees_avance", a["charges_constatees_avance"]),
    ]
    right_items = [
        ("capital", p["capital"]),
        ("reserve_legale", p["reserve_legale"]),
        ("autres_reserves", p["autres_reserves"]),
        ("report_nouveau", p["report_nouveau"]),
        ("resultat", p["resultat"]),
        ("emprunts", p["emprunts"]),
        ("dettes_fournisseurs", p["dettes_fournisseurs"]),
        ("dettes_fiscales_sociales", p["dettes_fiscales_sociales"]),
        ("autres_dettes", p["autres_dettes"]),
    ]

    max_len = max(len(left_items), len(right_items))
    for i in range(max_len):
        left = left_items[i] if i < len(left_items) else ("", 0)
        right = right_items[i] if i < len(right_items) else ("", 0)
        rows.append([
            P(label(left[0]) if left[0] else "", styles["Body"]),
            P(maybe_amount(left[1], profile) if left[0] else "", styles["BodyRight"]),
            P(label(right[0]) if right[0] else "", styles["Body"]),
            P(maybe_amount(right[1], profile) if right[0] else "", styles["BodyRight"]),
        ])

    rows.append([
        P("TOTAL DE L'ACTIF", styles["BodyBold"]),
        P(money(a["total_actif"]), styles["BodyBoldRight"]),
        P("TOTAL DU PASSIF", styles["BodyBold"]),
        P(money(p["total_passif"]), styles["BodyBoldRight"]),
    ])

    t = Table(rows, colWidths=[72 * mm, 22 * mm, 72 * mm, 22 * mm])
    style_for_table(t, theme, compact=theme.compact)
    return t


def build_resultat_table(data, theme, styles, profile, company):
    r = data["resultat"]
    with_n1 = profile["with_n1_column"]

    lines = [
        ("Ventes de marchandises", r["ca_marchandises"]),
        ("Prestations de services", r["ca_services"]),
        ("Production stockée", r["production_stockee"]),
        ("Chiffre d'affaires", r["chiffre_affaires"]),
        ("Autres produits", r["autres_produits"]),
        ("Produits financiers", r["produits_financiers"]),
        ("Produits exceptionnels", r["produits_exceptionnels"]),
        ("Achats", r["achats"]),
        ("Variation de stock", r["variation_stock"]),
        ("Charges externes", r["charges_externes"]),
        ("Impôts et taxes", r["impots_taxes"]),
        ("Salaires", r["salaires"]),
        ("Charges sociales", r["charges_sociales"]),
        ("Dotations aux amortissements", r["dotations_amortissements"]),
        ("Dotations aux provisions", r["dotations_provisions"]),
        ("Autres charges", r["autres_charges"]),
        ("Charges financières", r["charges_financieres"]),
        ("Charges exceptionnelles", r["charges_exceptionnelles"]),
        ("Total des produits", r["total_produits"]),
        ("Total des charges", r["total_charges"]),
        ("BÉNÉFICE / PERTE", r["benefice_ou_perte"]),
    ]

    if with_n1:
        rows = [[
            P("COMPTE DE RÉSULTAT", styles["BodyBold"]),
            P(company["exercise_n"], styles["BodyBoldRight"]),
            P(company["exercise_n1"], styles["BodyBoldRight"]),
        ]]
        for label_txt, value in lines:
            n, n1 = split_n_n1(value)
            rows.append([
                P(label_txt, styles["Body"]),
                P(money_signed(n), styles["BodyRight"]),
                P(money_signed(n1), styles["BodyRight"]),
            ])
        t = Table(rows, colWidths=[110 * mm, 32 * mm, 32 * mm])
    else:
        rows = [[
            P("COMPTE DE RÉSULTAT", styles["BodyBold"]),
            P("Montant", styles["BodyBoldRight"]),
        ]]
        for label_txt, value in lines:
            rows.append([
                P(label_txt, styles["Body"]),
                P(money_signed(value), styles["BodyRight"]),
            ])
        t = Table(rows, colWidths=[130 * mm, 45 * mm])

    style_for_table(t, theme, compact=theme.compact)
    return t


def build_simple_table(title, headers, rows, col_widths, theme):
    t = Table([[Paragraph(f"<b>{h}</b>", getSampleStyleSheet()["Normal"]) for h in headers]] + rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, theme.border),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, theme.border),
        ("BACKGROUND", (0, 0), (-1, 0), theme.secondary),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ============================================================
# PAGES
# ============================================================

def page_cover(company, theme, styles, profile):
    items = [Spacer(1, 20 * mm)]
    items.append(P(company["cabinet_name"], styles["DocTitle"]))
    items.append(P(company["cabinet_tagline"], styles["DocSubTitle"]))
    items.append(Spacer(1, 10 * mm))
    items.append(P(company["name"], styles["DocTitle"]))
    items.append(P(f"{random_date_label()} {company['closing_date']}", styles["DocSubTitle"]))
    items.append(Spacer(1, 10 * mm))
    items.append(build_company_box(company, theme, styles, profile))
    items.append(Spacer(1, 10 * mm))
    items.append(P(
        "Jeu de comptes annuels fictif généré pour des tests locaux d'ingestion documentaire, OCR et extraction de données.",
        styles["Body"],
    ))
    items.append(PageBreak())
    return items


def page_bilan(company, data, theme, styles, profile):
    items = []
    items.append(P(profile["title_variant"], styles["DocTitle"]))
    items.append(P(f"{random_date_label()} {company['closing_date']}", styles["DocSubTitle"]))
    items.append(Spacer(1, 3 * mm))

    if profile["with_header_box"]:
        items.append(build_header_block(company, theme, styles, profile))
        items.append(Spacer(1, 4 * mm))
        items.append(build_company_box(company, theme, styles, profile))
        items.append(Spacer(1, 4 * mm))

    items.append(build_bilan_table(data, theme, styles, profile, company))
    items.append(PageBreak())
    return items


def page_resultat(company, data, theme, styles, profile):
    items = []
    items.append(P("COMPTE DE RÉSULTAT", styles["DocTitle"]))
    items.append(P(f"Exercice {company['exercise_n']}", styles["DocSubTitle"]))
    items.append(Spacer(1, 3 * mm))
    if maybe(0.55):
        items.append(build_header_block(company, theme, styles, profile))
        items.append(Spacer(1, 4 * mm))
    items.append(build_resultat_table(data, theme, styles, profile, company))
    items.append(PageBreak())
    return items


def page_immobilisations(company, data, theme, styles, profile):
    a = data["actif"]
    rows = [
        [P("Immobilisations incorporelles", styles["Body"]), P(money(a["immobilisations_incorporelles"]), styles["BodyRight"])],
        [P("Immobilisations corporelles", styles["Body"]), P(money(a["immobilisations_corporelles"]), styles["BodyRight"])],
        [P("Immobilisations financières", styles["Body"]), P(money(a["immobilisations_financieres"]), styles["BodyRight"])],
        [P("TOTAL", styles["BodyBold"]), P(money(a["total_immobilise"]), styles["BodyBoldRight"])],
    ]
    t = Table(
        [[P("ÉTAT DES IMMOBILISATIONS", styles["BodyBold"]), P("Valeur brute", styles["BodyBoldRight"])]] + rows,
        colWidths=[130 * mm, 45 * mm]
    )
    style_for_table(t, theme, compact=theme.compact)
    return [P("ANNEXE - IMMOBILISATIONS", styles["DocTitle"]), Spacer(1, 3 * mm), t, PageBreak()]


def page_amortissements(company, data, theme, styles, profile):
    base = max(data["actif"]["immobilisations_corporelles"], 1000)
    debut = pct(base, 0.06, 0.35)
    dot = pct(base, 0.02, 0.10)
    fin = debut + dot

    a1 = int(fin * 0.40)
    a2 = int(fin * 0.35)
    a3 = fin - a1 - a2

    rows = [
        [P("Installations techniques", styles["Body"]), P(money(int(debut * 0.40)), styles["BodyRight"]), P(money(int(dot * 0.40)), styles["BodyRight"]), P(money(a1), styles["BodyRight"])],
        [P("Matériel bureau / informatique", styles["Body"]), P(money(int(debut * 0.35)), styles["BodyRight"]), P(money(int(dot * 0.35)), styles["BodyRight"]), P(money(a2), styles["BodyRight"])],
        [P("Mobilier et autres", styles["Body"]), P(money(debut - int(debut * 0.40) - int(debut * 0.35)), styles["BodyRight"]), P(money(dot - int(dot * 0.40) - int(dot * 0.35)), styles["BodyRight"]), P(money(a3), styles["BodyRight"])],
        [P("TOTAL", styles["BodyBold"]), P(money(debut), styles["BodyBoldRight"]), P(money(dot), styles["BodyBoldRight"]), P(money(fin), styles["BodyBoldRight"])],
    ]
    t = Table(
        [[P("Amortissements", styles["BodyBold"]), P("Début", styles["BodyBoldRight"]), P("Dotation", styles["BodyBoldRight"]), P("Fin", styles["BodyBoldRight"])]] + rows,
        colWidths=[82 * mm, 31 * mm, 31 * mm, 31 * mm]
    )
    style_for_table(t, theme, compact=theme.compact)
    return [P("TABLEAU DES AMORTISSEMENTS", styles["DocTitle"]), Spacer(1, 3 * mm), t, PageBreak()]


def page_provisions(company, data, theme, styles, profile):
    labels = [
        "Provisions pour litiges",
        "Provisions pour charges",
        "Provisions pour dépréciation clients",
        "Autres provisions",
    ]
    rows = [[
        P("Provisions", styles["BodyBold"]),
        P("Début", styles["BodyBoldRight"]),
        P("Dotation", styles["BodyBoldRight"]),
        P("Reprise", styles["BodyBoldRight"]),
        P("Fin", styles["BodyBoldRight"]),
    ]]
    td = tt = tr = tf = 0
    for label_txt in labels:
        d = pick(0, 0, 500, 1200, 2500, 6000)
        dot = pick(0, 0, 200, 500, 1200)
        rep = pick(0, 0, 100, 300, 800)
        f = max(0, d + dot - rep)
        td += d
        tt += dot
        tr += rep
        tf += f
        rows.append([
            P(label_txt, styles["Body"]),
            P(money(d) if d else "", styles["BodyRight"]),
            P(money(dot) if dot else "", styles["BodyRight"]),
            P(money(rep) if rep else "", styles["BodyRight"]),
            P(money(f) if f else "", styles["BodyRight"]),
        ])
    rows.append([
        P("TOTAL", styles["BodyBold"]),
        P(money(td), styles["BodyBoldRight"]),
        P(money(tt), styles["BodyBoldRight"]),
        P(money(tr), styles["BodyBoldRight"]),
        P(money(tf), styles["BodyBoldRight"]),
    ])
    t = Table(rows, colWidths=[75 * mm, 25 * mm, 25 * mm, 25 * mm, 25 * mm])
    style_for_table(t, theme, compact=theme.compact)
    return [P("ANNEXE - PROVISIONS", styles["DocTitle"]), Spacer(1, 3 * mm), t, PageBreak()]


def page_echeances(company, data, theme, styles, profile):
    a = data["actif"]
    p = data["passif"]

    rows_creances = [
        [P("Créances", styles["BodyBold"]), P("À 1 an", styles["BodyBoldRight"]), P("> 1 an", styles["BodyBoldRight"])],
        [P("Clients", styles["Body"]), P(money(int(a["creances_clients"] * 0.85)), styles["BodyRight"]), P(money(a["creances_clients"] - int(a["creances_clients"] * 0.85)), styles["BodyRight"])],
        [P("Autres créances", styles["Body"]), P(money(int(a["autres_creances"] * 0.65)), styles["BodyRight"]), P(money(a["autres_creances"] - int(a["autres_creances"] * 0.65)), styles["BodyRight"])],
    ]
    rows_dettes = [
        [P("Dettes", styles["BodyBold"]), P("À 1 an", styles["BodyBoldRight"]), P("> 1 an", styles["BodyBoldRight"])],
        [P("Emprunts", styles["Body"]), P(money(int(p["emprunts"] * 0.35)), styles["BodyRight"]), P(money(p["emprunts"] - int(p["emprunts"] * 0.35)), styles["BodyRight"])],
        [P("Fournisseurs", styles["Body"]), P(money(p["dettes_fournisseurs"]), styles["BodyRight"]), P("", styles["BodyRight"])],
        [P("Dettes fiscales / sociales", styles["Body"]), P(money(p["dettes_fiscales_sociales"]), styles["BodyRight"]), P("", styles["BodyRight"])],
    ]
    left = Table(rows_creances, colWidths=[75 * mm, 22 * mm, 22 * mm])
    right = Table(rows_dettes, colWidths=[75 * mm, 22 * mm, 22 * mm])
    style_for_table(left, theme, compact=theme.compact)
    style_for_table(right, theme, compact=theme.compact)

    big = Table([[left], [Spacer(1, 4 * mm)], [right]], colWidths=[119 * mm])
    return [P("ÉTAT DES ÉCHÉANCES", styles["DocTitle"]), Spacer(1, 3 * mm), big, PageBreak()]


def page_detail_exceptionnel(company, data, theme, styles, profile):
    rows = [[P("Libellé", styles["BodyBold"]), P("Montant", styles["BodyBoldRight"])]]
    total = 0
    for _ in range(random.randint(2, 4)):
        label_txt = pick(
            "Pénalités et amendes",
            "Régularisation exercice antérieur",
            "Produit exceptionnel sur cession",
            "Charge non récurrente",
            "Indemnité exceptionnelle",
        )
        amount = random.randint(150, 6000)
        total += amount
        rows.append([P(label_txt, styles["Body"]), P(money(amount), styles["BodyRight"])])
    rows.append([P("TOTAL", styles["BodyBold"]), P(money(total), styles["BodyBoldRight"])])

    t = Table(rows, colWidths=[130 * mm, 45 * mm])
    style_for_table(t, theme, compact=theme.compact)
    return [P("ANNEXE - DÉTAIL EXCEPTIONNEL", styles["DocTitle"]), Spacer(1, 3 * mm), t, PageBreak()]


# ============================================================
# PIED DE PAGE
# ============================================================

def draw_page_decorations(canvas_obj, doc, theme: VisualTheme, company: dict, profile: dict):
    page_num = canvas_obj.getPageNumber()
    canvas_obj.saveState()
    if theme.use_accent_lines:
        canvas_obj.setStrokeColor(theme.primary)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(doc.leftMargin, A4[1] - doc.topMargin + 4, A4[0] - doc.rightMargin, A4[1] - doc.topMargin + 4)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.black)
    canvas_obj.drawString(doc.leftMargin, 8 * mm, company["name"][:60])
    canvas_obj.drawRightString(A4[0] - doc.rightMargin, 8 * mm, f"Page {page_num}")
    canvas_obj.restoreState()


# ============================================================
# DÉGRADATION "FAUX SCAN"
# ============================================================

def _add_noise(image: Image.Image, amount: int = 10) -> Image.Image:
    noise = Image.effect_noise(image.size, amount)
    noise = noise.convert("L")
    noise = ImageEnhance.Contrast(noise).enhance(1.8)
    return Image.blend(image.convert("L"), noise, alpha=0.08).convert("RGB")


def _degrade_page(img: Image.Image) -> Image.Image:
    # rotation légère
    angle = random.uniform(-1.2, 1.2)
    img = img.rotate(angle, expand=True, fillcolor="white")

    # niveaux de gris partiels
    if maybe(0.55):
        img = ImageOps.grayscale(img).convert("RGB")

    # contraste / luminosité
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.9, 1.2))
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95, 1.05))

    # blur léger
    if maybe(0.45):
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.2, 0.7)))

    # bruit
    if maybe(0.75):
        img = _add_noise(img, amount=random.randint(6, 14))

    # vignette / ombres scan
    draw = ImageDraw.Draw(img)
    w, h = img.size
    if maybe(0.60):
        shade = random.randint(220, 245)
        draw.rectangle([0, 0, w, random.randint(8, 20)], fill=(shade, shade, shade))
        draw.rectangle([0, h - random.randint(8, 20), w, h], fill=(shade, shade, shade))

    # petite bordure grise
    if maybe(0.40):
        border = random.randint(8, 18)
        img = ImageOps.expand(img, border=border, fill=(240, 240, 240))

    return img


def degrade_pdf_to_scanned(pdf_path: str):
    if fitz is None:
        print("PyMuPDF non installé : scan dégradé ignoré.")
        return

    temp_path = pdf_path.replace(".pdf", "_scanned_tmp.pdf")

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

    # Remplacement du fichier original une fois tout fermé
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    os.replace(temp_path, pdf_path)


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

def generate_random_bilan_v2(OUTPUT_DIR_JSON="output_pdf"):
    os.makedirs(OUTPUT_DIR_JSON, exist_ok=True)

    theme = random_theme()
    company = generate_company()
    data = generate_accounting_data()
    profile = generate_document_profile()
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
        story.extend(page_cover(company, theme, styles, profile))

    section_builders = {
        "bilan": lambda: page_bilan(company, data, theme, styles, profile),
        "resultat": lambda: page_resultat(company, data, theme, styles, profile),
        "immobilisations": lambda: page_immobilisations(company, data, theme, styles, profile),
        "amortissements": lambda: page_amortissements(company, data, theme, styles, profile),
        "provisions": lambda: page_provisions(company, data, theme, styles, profile),
        "echeances": lambda: page_echeances(company, data, theme, styles, profile),
        "detail_exceptionnel": lambda: page_detail_exceptionnel(company, data, theme, styles, profile),
    }

    for section in profile["section_order"]:
        if section == "immobilisations" and not profile["with_immobilisations"]:
            continue
        if section == "amortissements" and not profile["with_amortissements"]:
            continue
        if section == "provisions" and not profile["with_provisions"]:
            continue
        if section == "echeances" and not profile["with_echeances"]:
            continue
        if section == "detail_exceptionnel" and not profile["with_detail_exceptionnel"]:
            continue
        story.extend(section_builders[section]())

    if profile["with_footer_note"]:
        story.append(P(
            "Document fictif généré automatiquement pour tests d'ingestion, OCR, parsing et classification.",
            styles["Tiny"]
        ))

    def _draw(canvas_obj, doc_obj):
        draw_page_decorations(canvas_obj, doc_obj, theme, company, profile)

    doc.build(story, onFirstPage=_draw, onLaterPages=_draw)

    if profile["degrade_scan"]:
        degrade_pdf_to_scanned(output_path)

    print(f"PDF généré : {output_path}")
    print(f"Entreprise : {company['name']}")
    print(f"Type : {profile['doc_type']}")
    print(f"Thème : {theme.name}")
    print(f"N/N-1 : {profile['with_n1_column']}")
    print(f"Dégradé scan : {profile['degrade_scan']}")
    print(f"Ordre sections : {profile['section_order']}")

    return output_path


if __name__ == "__main__":
    generate_random_bilan_v2()