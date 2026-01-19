from fontTools.misc import transform
from ufoLib2 import Font
from ufoLib2.objects import Glyph, Contour, Point
from ufo2ft import compileTTF
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPointPen
from fontTools.misc.transform import Identity
import json
from glyph_overrides import overrides
from constants import *


def utf8str2ord(s: str) -> int:
    integer = int(s, 16)
    length = (integer.bit_length() + 7) // 8
    return ord(integer.to_bytes(length=length, byteorder="big").decode("utf-8"))


def ord2utf8str(i: int) -> str:
    b = chr(i).encode("utf-8")
    return b.hex()


# Create font
font: Font = Font()
font.info.familyName = "Open Pentagon"
font.info.styleName = "Regular"
font.info.unitsPerEm = FONT_EM
font.info.ascender = FONT_ACTUAL_ASCENDER
font.info.descender = FONT_ACTUAL_DESCENDER
font.info.openTypeOS2TypoLineGap = FONT_LINE_GAP

next_private_codepoint = 0xE000
font_lut = {}

sq_font = TTFont("OpenSquare.ttf")
sq_head = sq_font["head"]
sq_units_per_em = sq_head.unitsPerEm
sq_glyph_set = sq_font.getGlyphSet()
sq_cmap = sq_font.getBestCmap() or {}
sq_scale = FONT_EM / sq_units_per_em

overrides_dir = vars(overrides)
for codepoint, name in sq_cmap.items():
    if name in overrides_dir:
        overrides_dir[name](font.newGlyph(name))
    else:
        dst = font.newGlyph(name)
        src_width, _ = sq_font["hmtx"][name]
        dst.width = src_width * sq_scale

        dst_pen = dst.getPointPen()
        transform = Identity.scale(sq_scale, sq_scale)
        dst_pen2 = TransformPointPen(dst_pen, transform)
        sq_glyph_set[name].drawPoints(dst_pen2)

    font[name].unicodes.append(codepoint)

sq_font.close()

with open("bootstrap-icons.json", "r") as f:
    bs_original_lut = json.load(f)
bs_ord2codename: dict[int, str] = {
    utf8str2ord(value): key for key, value in bs_original_lut.items()
}

bs_font = TTFont("bootstrap-icons.ttf")
bs_head = bs_font["head"]
bs_units_per_em = bs_head.unitsPerEm
bs_glyph_set = bs_font.getGlyphSet()
bs_cmap = bs_font.getBestCmap() or {}

BS_ICON_SIZE = 880
BS_PREFIX = "bs-"  # used only in case of name collision
bs_scale = BS_ICON_SIZE / bs_units_per_em


for codepoint, name in bs_cmap.items():
    glyph_name = name
    if glyph_name in font:
        glyph_name = BS_PREFIX + glyph_name
        if glyph_name in font:
            print("bootstrap name collision", glyph_name)
            continue

    dst = font.newGlyph(glyph_name)
    # icons must be square or weird pixel aligment stuff happens
    dst.width = FONT_ACTUAL_HEIGHT

    dst_pen = dst.getPointPen()
    transform = Identity.scale(bs_scale, bs_scale).translate(
        (dst.width - BS_ICON_SIZE) / 2 / bs_scale,
        (FONT_DESCENDER + (FONT_EM - BS_ICON_SIZE) / 2) / bs_scale,
    )
    dst_pen2 = TransformPointPen(dst_pen, transform)
    bs_glyph_set[name].drawPoints(dst_pen2)

    font[glyph_name].unicodes.append(next_private_codepoint)
    font_lut[glyph_name] = ord2utf8str(next_private_codepoint)
    next_private_codepoint += 1

bs_font.close()


with open("promptfont-glyphs.json", "r") as f:
    pf_original_list = json.load(f)
pf_ord2codename: dict[int, str] = {
    d["codepoint"]: d["code-name"] for d in pf_original_list
}

pf_font = TTFont("promptfont.ttf")
pf_head = pf_font["head"]
pf_units_per_em = pf_head.unitsPerEm
pf_glyph_set = pf_font.getGlyphSet()
pf_cmap = pf_font.getBestCmap() or {}

PF_PREFIX = "pf-"  # used only in case of name collision

for codepoint, name in pf_cmap.items():
    glyph_name = pf_ord2codename.get(codepoint) or name
    if glyph_name in font:
        glyph_name = PF_PREFIX + glyph_name
        if glyph_name in font:
            print("bootstrap name collision", glyph_name)
            continue

    dst = font.newGlyph(glyph_name)
    src_width, _ = pf_font["hmtx"][name]
    dst.width = src_width

    dst_pen = dst.getPointPen()
    pf_glyph_set[name].drawPoints(dst_pen)

    font[glyph_name].unicodes.append(next_private_codepoint)
    font_lut[glyph_name] = ord2utf8str(next_private_codepoint)
    next_private_codepoint += 1

pf_font.close()

# Compile and save as TTF
ttf = compileTTF(font)
ttf.save("open-pentagon.ttf")

# Save the new lut
with open("open-pentagon.json", "w+") as f:
    f.write(json.dumps(font_lut, indent=4))
