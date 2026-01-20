PRIVATE_USE_AREA = (0xE000, 0xF900)

FONT_EM = 1000
FONT_ASCENDER = 800
FONT_DESCENDER = FONT_ASCENDER - FONT_EM


FONT_TOP_PAD = 100
FONT_BOTTOM_PAD = 100

FONT_ACTUAL_ASCENDER = FONT_ASCENDER + FONT_TOP_PAD
FONT_ACTUAL_DESCENDER = FONT_DESCENDER - FONT_BOTTOM_PAD
FONT_ACTUAL_HEIGHT = FONT_ACTUAL_ASCENDER - FONT_ACTUAL_DESCENDER

# This value is used to space out lines.
# Love2D adds this value to the height.
# The the gap is inserted at the top of each line above the characters
FONT_LINE_GAP = 0

#
# Glyphs typically live between the ascender and descender but these are just convention and aren't real.
# Love2d only cares about the OS2/HHead metrics which is why there's an actual ascender and descender.
#
#                           -----------------
#                           ^               ^
#                           line gap        |
#                           v               |
#       actual ascender     ------------    |
#                           top pad         |
# 800   ascender            ------------    |
#                                           love2d's font height
#                                           |
#                                           |
# 0     baseline            ------------    |
#                                           |
# -200  descender           ------------    |
#                           bottom pad      v
#       actual descender    -----------------
#
