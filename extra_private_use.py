from glyph_tools import *

extra_private_use = {}

extra_private_use["debug-full-mono-character-block"] = get_glyph_generator(
    [rect(0, FONT_ASCENDER, C_GLYPH_WIDTH, FONT_DESCENDER)], C_GLYPH_WIDTH
)
