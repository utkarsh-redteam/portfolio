#!/usr/bin/env python3
"""Generate self-hosted fonts, social/hero/certificate images, icons, and résumé metadata.

Committed outputs are what the site serves. Re-run from the repo root if a source
asset changes. Does not alter visible résumé page content.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pikepdf
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ROOT / "fonts"
CERT_OUT = ASSETS / "certificates"

ROLE = "QA Automation Architect | AI-Driven Quality Engineering Leader"

# Google Fonts latin range, plus the decorative glyphs the site actually draws.
UNICODE = (
    list(range(0x0000, 0x00FF + 1))
    + [0x0131, 0x0152, 0x0153, 0x02BB, 0x02BC, 0x02C6, 0x02DA, 0x02DC, 0x0304, 0x0308, 0x0329]
    + list(range(0x2000, 0x206F + 1))
    + [0x20AC, 0x2122, 0x2191, 0x2193, 0x2212, 0x2215, 0xFEFF, 0xFFFD]
    + [0x25A0, 0x25B2, 0x25B8, 0x25C6, 0x25C7, 0x2605, 0x2713]
)

# (source, output, family, subfamily, weight). Mac installs split some weights
# into their own family names; CSS expects one family plus usWeightClass.
FONT_JOBS = [
    ("/usr/share/fonts/truetype/macos/Inter-Regular.ttf", "inter-latin-400.woff2", "Inter", "Regular", 400),
    ("/usr/share/fonts/truetype/macos/Inter-Medium.ttf", "inter-latin-500.woff2", "Inter", "Medium", 500),
    ("/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf", "inter-latin-600.woff2", "Inter", "SemiBold", 600),
    ("/usr/share/fonts/truetype/macos/Inter-Bold.ttf", "inter-latin-700.woff2", "Inter", "Bold", 700),
    ("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf", "jetbrains-mono-latin-400.woff2", "JetBrains Mono", "Regular", 400),
    ("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf", "jetbrains-mono-latin-700.woff2", "JetBrains Mono", "Bold", 700),
    ("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf", "jetbrains-mono-latin-800.woff2", "JetBrains Mono", "ExtraBold", 800),
]

CERT_JOBS = [
    ("UTKARSH_SINHA_certificate20260210-453-tej3xh.jpg", "pg-ai-for-leaders"),
    ("SA RPA.png", "uipath-solution-architect-training"),
    ("BA RPA.png", "uipath-business-analyst-training"),
    ("DEV RPA.png", "uipath-rpa-developer"),
    ("csm.png", "csm-scrum-alliance"),
]


def stamp_font_names(font: TTFont, family: str, subfamily: str, weight: int) -> None:
    full = f"{family} {subfamily}"
    ps = f"{family}-{subfamily}".replace(" ", "")
    table = font["name"]
    for name_id, value in ((1, family), (2, subfamily), (4, full), (6, ps), (16, family), (17, subfamily)):
        table.setName(value, name_id, 3, 1, 0x409)
        table.setName(value, name_id, 1, 0, 0)
    os2 = font["OS/2"]
    os2.usWeightClass = weight
    flags = os2.fsSelection & ~0x60
    if weight == 400:
        flags |= 0x40
    elif weight == 700:
        flags |= 0x20
    os2.fsSelection = flags


def subset_font(src: str, dest: Path, family: str, subfamily: str, weight: int) -> None:
    font = TTFont(src)
    options = Options()
    options.layout_features = ["kern", "liga", "calt"]
    options.hinting = True
    options.desubroutinize = True
    options.flavor = "woff2"
    options.with_zopfli = False
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=UNICODE)
    subsetter.subset(font)
    stamp_font_names(font, family, subfamily, weight)
    font.flavor = "woff2"
    dest.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(dest))


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def rounded_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def draw_mark(size: int) -> Image.Image:
    """Dark rounded tile with a geometric >_ mark, matching favicon.svg."""
    scale = 4 if size < 256 else 1
    canvas = size * scale
    radius = max(2, int(canvas * 0.18))
    tile = Image.new("RGB", (canvas, canvas), "#0a0e14")
    face = Image.new("RGB", (canvas, canvas), "#0d1117")
    mask = Image.new("L", (canvas, canvas), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, canvas - 1, canvas - 1), radius=radius, fill=255)
    img = Image.composite(face, tile, mask)
    draw = ImageDraw.Draw(img)
    stroke = max(2 * scale, round(canvas * 0.075))
    color = "#58a6ff"
    cx, cy = canvas / 2, canvas / 2
    arm = canvas * 0.16
    tip_x = cx - canvas * 0.02
    left_x = tip_x - canvas * 0.20
    draw.line((left_x, cy - arm, tip_x, cy), fill=color, width=stroke)
    draw.line((left_x, cy + arm, tip_x, cy), fill=color, width=stroke)
    bar_y = cy + arm
    draw.line((tip_x + canvas * 0.06, bar_y, tip_x + canvas * 0.28, bar_y), fill=color, width=stroke)
    if scale != 1:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def save_webp(img: Image.Image, path: Path, quality: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="WEBP", quality=quality, method=6)


def to_rgb(img: Image.Image) -> Image.Image:
    if img.mode == "RGB":
        return img
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, "#ffffff")
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


def fit_width(img: Image.Image, width: int) -> Image.Image:
    if img.width <= width:
        return img
    height = round(img.height * (width / img.width))
    return img.resize((width, height), Image.Resampling.LANCZOS)


# Latin variable fonts currently served by Google Fonts for this exact stack.
# One file per family; the wght axis covers every weight the CSS uses.
VARIABLE_FONTS = {
    "inter-latin.woff2": "https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2",
    "jetbrains-mono-latin.woff2": "https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwgknk-4.woff2",
}


def build_fonts() -> None:
    import urllib.request

    FONTS.mkdir(parents=True, exist_ok=True)
    lic = Path("/tmp/fontlic")
    if (lic / "OFL-Inter.txt").exists():
        shutil.copy(lic / "OFL-Inter.txt", FONTS / "OFL-Inter.txt")
    if (lic / "OFL-JetBrainsMono.txt").exists():
        shutil.copy(lic / "OFL-JetBrainsMono.txt", FONTS / "OFL-JetBrainsMono.txt")
    for name, url in VARIABLE_FONTS.items():
        dest = FONTS / name
        urllib.request.urlretrieve(url, dest)
        print(f"font {name} {dest.stat().st_size} bytes")
    for stale in FONTS.glob("*-latin-*.woff2"):
        # static per-weight subsets from an earlier pass
        if stale.name not in VARIABLE_FONTS:
            stale.unlink()
            print(f"removed {stale.name}")


def build_hero() -> None:
    src = Image.open(ASSETS / "profile.jpg")
    rgb = to_rgb(src)
    for size, quality in ((96, 78), (192, 82), (288, 82)):
        img = rgb.resize((size, size), Image.Resampling.LANCZOS)
        save_webp(img, ASSETS / f"profile-{size}.webp", quality)
        print(f"profile-{size}.webp { (ASSETS / f'profile-{size}.webp').stat().st_size}")
    jpg = rgb.resize((192, 192), Image.Resampling.LANCZOS)
    jpg.save(ASSETS / "profile-192.jpg", format="JPEG", quality=82, optimize=True, progressive=True)
    print(f"profile-192.jpg {(ASSETS / 'profile-192.jpg').stat().st_size}")


def build_certificates() -> None:
    old = ASSETS / "certfificates"
    if not old.exists():
        print("certificate sources already converted; leaving assets/certificates/")
        return
    if CERT_OUT.exists():
        shutil.rmtree(CERT_OUT)
    CERT_OUT.mkdir(parents=True)
    for filename, slug in CERT_JOBS:
        img = to_rgb(Image.open(old / filename))
        full = fit_width(img, 1600)
        thumb = fit_width(img, 800)
        save_webp(full, CERT_OUT / f"{slug}.webp", 82)
        save_webp(thumb, CERT_OUT / f"{slug}-thumb.webp", 72)
        full_path = CERT_OUT / f"{slug}.webp"
        thumb_path = CERT_OUT / f"{slug}-thumb.webp"
        print(
            f"{slug} full {full.size} {full_path.stat().st_size}B "
            f"thumb {thumb.size} {thumb_path.stat().st_size}B"
        )


def build_icons() -> None:
    sizes = (16, 32, 48)
    frames = [draw_mark(size) for size in sizes]
    frames[-1].save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=frames[:-1],
    )
    draw_mark(180).save(ROOT / "apple-touch-icon.png", format="PNG", optimize=True)
    draw_mark(192).save(ROOT / "icon-192.png", format="PNG", optimize=True)
    draw_mark(512).save(ROOT / "icon-512.png", format="PNG", optimize=True)
    for name in ("favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png"):
        print(f"{name} {(ROOT / name).stat().st_size}")


def build_og() -> None:
    w, h = 1200, 627
    bg = Image.new("RGB", (w, h), "#0a0e14")
    glow = Image.new("RGB", (w, h), "#0a0e14")
    g = ImageDraw.Draw(glow)
    g.ellipse((900, -120, 1400, 380), fill="#102033")
    g.ellipse((-180, 380, 420, 860), fill="#0d2218")
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    img = Image.blend(bg, glow, 0.85)
    draw = ImageDraw.Draw(img)

    # Terminal card
    card = (64, 56, 1136, 571)
    draw.rounded_rectangle(card, radius=18, fill="#10161f", outline="#1e2731", width=2)
    draw.rectangle((64, 56, 1136, 112), fill="#131a24")
    draw.line((64, 112, 1136, 112), fill="#1e2731", width=2)
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        cx = 96 + i * 28
        draw.ellipse((cx, 74, cx + 16, 90), fill=color)

    mono = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
    mono_bold = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
    inter_bold = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
    inter = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
    draw.text((168, 70), "utkarsh@career: ~", font=font(mono, 18), fill="#8b949e")

    draw.text((104, 150), "$ whoami", font=font(mono, 28), fill="#39d353")
    draw.text((104, 210), "Utkarsh Sinha", font=font(inter_bold, 72), fill="#ffffff")
    draw.text((104, 310), "QA Automation Architect", font=font(inter, 32), fill="#c9d1d9")
    draw.text((104, 358), "AI-Driven Quality Engineering Leader", font=font(inter, 32), fill="#8b949e")

    stats = "18+ years   ·   Gurgaon, India   ·   AI test automation"
    draw.text((104, 470), stats, font=font(mono, 22), fill="#58a6ff")

    # Circular profile
    photo = to_rgb(Image.open(ASSETS / "profile.jpg")).resize((210, 210), Image.Resampling.LANCZOS)
    mask = rounded_mask(210)
    ring = Image.new("RGBA", (230, 230), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, 229, 229), outline="#58a6ff", width=4)
    img.paste(photo, (860, 200), mask)
    img.paste(ring, (850, 190), ring)

    out = ASSETS / "og-image.png"
    img.save(out, format="PNG", optimize=True)
    print(f"og-image.png {img.size} {out.stat().st_size}")


def decoded_contents(pdf: pikepdf.Pdf) -> list[bytes]:
    blobs = []
    for page in pdf.pages:
        contents = page.get("/Contents")
        if isinstance(contents, pikepdf.Array):
            blobs.append(b"".join(part.read_bytes() for part in contents))
        else:
            blobs.append(contents.read_bytes())
    return blobs


def build_pdf() -> None:
    src = ASSETS / "UTKARSH_SINHA_18_Years_AI_Expert_Technical_QA_Manager.pdf"
    before = pikepdf.open(src)
    before_streams = decoded_contents(before)
    before_size = src.stat().st_size

    info = before.docinfo
    for key in ("/Producer", "/Creator", "/ecv-data"):
        if key in info:
            del info[key]
    info["/Title"] = f"Utkarsh Sinha — {ROLE}"
    info["/Author"] = f"Utkarsh Sinha, {ROLE}"
    info["/Subject"] = ROLE
    info["/Keywords"] = ROLE
    info["/ModDate"] = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")

    tmp = src.with_suffix(".tmp.pdf")
    before.save(
        tmp,
        compress_streams=True,
        recompress_flate=True,
        object_stream_mode=pikepdf.ObjectStreamMode.generate,
        linearize=True,
    )
    after = pikepdf.open(tmp)
    after_streams = decoded_contents(after)
    if before_streams != after_streams:
        raise SystemExit("PDF page content changed; refusing to overwrite the résumé")
    blob = " ".join(str(after.docinfo.get(k, "")) for k in ("/Title", "/Author", "/Subject", "/Keywords", "/Producer", "/Creator"))
    if "Enhancv" in blob or "enhancv" in blob.lower():
        raise SystemExit(f"Enhancv text still in Info dict: {blob}")
    if "/ecv-data" in after.docinfo:
        raise SystemExit("ecv-data still present")
    tmp.replace(src)
    print(f"pdf {before_size} -> {src.stat().st_size}")
    print("title", after.docinfo.get("/Title"))
    print("author", after.docinfo.get("/Author"))
    print("producer", after.docinfo.get("/Producer"))


def main() -> None:
    build_fonts()
    build_hero()
    build_certificates()
    build_icons()
    build_og()
    build_pdf()


if __name__ == "__main__":
    main()
