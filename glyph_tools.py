from ufoLib2.objects import Glyph, Contour, Point
import pyclipper
from pyclipper import (
    ET_CLOSEDLINE,
    ET_CLOSEDPOLYGON,
    ET_OPENBUTT,
    ET_OPENROUND,
    ET_OPENSQUARE,
)
from pyclipper import JT_MITER, JT_ROUND, JT_SQUARE
from constants import *
import math


def rect(l, t, r, b):
    return [[l, b], [r, b], [r, t], [l, t]]


def middle(n1, n2):
    return (n1 + n2) / 2


def t(p, x, y):
    return [p[0] + x, p[1] + y]


def s(p, sx, sy):
    return [p[0] * sx, p[1] * sy]


def r(p, R):
    x, y = p[0], p[1]
    cos, sin = math.cos(R), math.sin(R)
    return [x * cos - y * sin, x * sin + y * cos]


def contour_translate(c, x, y):
    return [t(p, x, y) for p in c]


def contour_scale(c, sx, sy):
    return [s(p, sx, sy) for p in c]


def contour_rotate(c, R):
    return [r(p, R) for p in c]


def midpoint(p1, p2):
    return [middle(p1[0], p2[0]), middle(p1[1], p2[1])]


def dist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def lerp(p0, p1, t):
    return [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t]


def sgn(n):
    if n < 0:
        return -1
    if n > 0:
        return 1
    return 0


# 04 -> 45 degree
# 13 -> 135 degree
# 22 -> 225 degree
# 31 -> 315 degree


def chamfer_04(p, d, flip=False):
    return ([t(p, 0, d), t(p, d, 0)])[:: -1 if flip else 1]


def chamfer_13(p, d, flip=False):
    return ([t(p, d, 0), t(p, 0, -d)])[:: -1 if flip else 1]


def chamfer_22(p, d, flip=False):
    return ([t(p, 0, -d), t(p, -d, 0)])[:: -1 if flip else 1]


def chamfer_31(p, d, flip=False):
    return ([t(p, -d, 0), t(p, 0, d)])[:: -1 if flip else 1]


contour_t = list[list[int]]
contour_list_t = list[list[list[int]]]


def solidify_lines(
    thickness,
    *lines: contour_t,
    jt=JT_MITER,
    et=ET_OPENSQUARE,
) -> contour_list_t:
    pco = pyclipper.PyclipperOffset()
    pco.AddPaths(lines, jt, et)
    offset = pco.Execute(thickness / 2)

    pc = pyclipper.Pyclipper()
    pc.AddPaths(offset, pyclipper.PT_SUBJECT, True)
    return pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)


def find_solution(contour_generator, search_parameters, max_iter=1000, debug=False):
    param_values = [p["start"] for p in search_parameters]
    if max_iter == 0:
        contour = contour_generator(*param_values)
        print(contour)
        return contour

    for _ in range(max_iter):
        contour = contour_generator(*param_values)
        param_has_changed = False
        differences = [p["fn"](contour) for p in search_parameters]
        if debug:
            print(differences)
        for i, difference in enumerate(differences):
            if difference != 0:
                param_has_changed = True
            param_values[i] += sgn(difference)
        if not param_has_changed:
            for v, result in zip(param_values, search_parameters):
                result["result"] = v
            return contour

    print("warning: could not find solution", param_values)
    for v, result in zip(param_values, search_parameters):
        result["result"] = v
    return contour


def contour_union(*contours: contour_t) -> contour_list_t:
    pc = pyclipper.Pyclipper()
    pc.AddPaths(contours, pyclipper.PT_SUBJECT, True)
    return pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)


def contour_intersection(clip: contour_t, *subjects: contour_t) -> contour_list_t:
    pc = pyclipper.Pyclipper()
    pc.AddPaths(subjects, pyclipper.PT_SUBJECT, True)
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    return pc.Execute(
        pyclipper.CT_INTERSECTION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO
    )


def dot(x, y, size) -> contour_t:
    h = size / 2
    return [
        [x - h, y - h],
        [x - h, y + h],
        [x + h, y + h],
        [x + h, y - h],
    ]


def get_glyph_generator(contours: contour_list_t, width):
    def gen(glyph: Glyph):
        glyph.width = width
        pen = glyph.getPointPen()
        for cont in contours:
            pen.beginPath()
            for x, y in cont:
                pen.addPoint((x, y), segmentType="line", smooth=False)
            pen.endPath()

    return gen


C_LEFT_PAD = 60
C_RIGHT_PAD = 60
C_CHAR_WIDTH = 480
C_CHAR_HEIGHT = 640
C_LINE_WIDTH = 110
C_HALF_LINE_WIDTH = C_LINE_WIDTH / 2
C_GLYPH_WIDTH = C_LEFT_PAD + C_RIGHT_PAD + C_CHAR_WIDTH
C_LEFT = C_LEFT_PAD
C_TOP = C_CHAR_HEIGHT
C_RIGHT = C_LEFT_PAD + C_CHAR_WIDTH
C_BOTTOM = 0
C_OUTLINE = rect(C_LEFT, C_TOP, C_RIGHT, C_BOTTOM)
C_TITTLE_SIZE = C_LINE_WIDTH * 1.25
C_DOT_SIZE = C_LINE_WIDTH * 1.5

pco = pyclipper.PyclipperOffset()
pco.AddPath(C_OUTLINE, JT_MITER, ET_CLOSEDPOLYGON)
solution = pco.Execute(C_LINE_WIDTH / -2)
assert len(solution) == 1
assert len(solution[0]) == 4
solution = solution[0]

# C7   C8   C9
# X1   X2   X3 x-height
# C4   C5   C6
# W1   W2   W3 half x-height
# C1   C2   C3
# D1   D2   D3 descent

C1 = solution[2]
C3 = solution[3]
C7 = solution[1]
C9 = solution[0]
C4 = midpoint(C1, C7)
C6 = midpoint(C3, C9)
C2 = midpoint(C1, C3)
C8 = midpoint(C7, C9)
C5 = midpoint(C2, C8)
dist_C1_C3 = dist(C1, C3)
X_HEIGHT = dist_C1_C3 + C_LINE_WIDTH
X1 = t(C1, 0, dist_C1_C3)
X2 = t(C2, 0, dist_C1_C3)
X3 = t(C3, 0, dist_C1_C3)
W1 = midpoint(X1, C1)
W2 = midpoint(X2, C2)
W3 = midpoint(X3, C3)
D1 = t(C1, 0, FONT_DESCENDER)
D2 = t(C2, 0, FONT_DESCENDER)
D3 = t(C3, 0, FONT_DESCENDER)

C_LOWERCASE_O_OUTLINE = rect(C_LEFT, X_HEIGHT, C_RIGHT, C_BOTTOM)

C_BRACKET_OVERSHOOT = 80

# Bracket grid
# BC7 B7 B8 B9 BC9
#     B4 B5 B6
# BC1 B1 B2 B3 BC3

BC1 = t(C1, 0, -C_BRACKET_OVERSHOOT)
BC3 = t(C3, 0, -C_BRACKET_OVERSHOOT)
BC7 = t(C7, 0, C_BRACKET_OVERSHOOT)
BC9 = t(C9, 0, C_BRACKET_OVERSHOOT)

B1 = t(midpoint(C1, C2), 0, -C_BRACKET_OVERSHOOT)
B3 = t(midpoint(C2, C3), 0, -C_BRACKET_OVERSHOOT)
B7 = t(midpoint(C7, C8), 0, C_BRACKET_OVERSHOOT)
B9 = t(midpoint(C8, C9), 0, C_BRACKET_OVERSHOOT)
B4 = midpoint(B1, B7)
B6 = midpoint(B3, B9)
B2 = midpoint(B1, B3)
B8 = midpoint(B7, B9)
B5 = midpoint(B2, B8)


def short_get_glyph_generator(
    *points: contour_list_t, jt=JT_MITER, et=ET_OPENSQUARE, clip=C_OUTLINE
):
    contours = solidify_lines(C_LINE_WIDTH, *points, jt=jt, et=et)
    if clip is not None:
        contours = contour_intersection(clip, *contours)
    return get_glyph_generator(contours, C_GLYPH_WIDTH)
