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
from types import SimpleNamespace as Namespace


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


overrides = Namespace()

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


# region COMMON CONTOURS

M_contour = find_solution(
    lambda a, b: solidify_lines(
        C_LINE_WIDTH,
        [
            C1,
            C7,
            t(C7, a, 0),
            t(C5, -b, 0),
            t(C5, b, 0),
            t(C9, -a, 0),
            C9,
            C3,
        ],
    ),
    [
        {
            "start": 30,
            "fn": lambda contour: -(
                contour[0][9][0] - contour[0][10][0] - C_LINE_WIDTH
            ),
        },
        {
            "start": 10,
            "fn": lambda contour: -(contour[0][2][0] - contour[0][1][0] - C_LINE_WIDTH),
        },
    ],
)

W_contour = [[[p[0], -p[1] + 640] for p in M_contour[0]]]

S_contour = solidify_lines(
    C_LINE_WIDTH,
    [midpoint(C6, C9), C9, C7, C4, C6, C3, C1, midpoint(C1, C4)],
    et=ET_OPENBUTT,
)

O_contour = solidify_lines(C_LINE_WIDTH, [C7, C9, C3, C1, C7])

hyphen_half_width = 200
hyphen_contour = solidify_lines(
    C_LINE_WIDTH,
    [t(C5, -hyphen_half_width, 0), t(C5, hyphen_half_width, 0)],
    et=ET_OPENBUTT,
)

period_contour = dot(middle(C_LEFT, C_RIGHT), C_BOTTOM + C_DOT_SIZE / 2, C_DOT_SIZE)
top_dot_contour = dot(*X2, C_DOT_SIZE)
comma_contour = [
    period_contour[1],
    period_contour[2],
    t(period_contour[3], -100, -100),
    t(period_contour[0], -40, -100),
]

# endregion

# region 0x20 - 0x2F

overrides.space = get_glyph_generator([], C_GLYPH_WIDTH)
overrides.exclam = get_glyph_generator(
    [
        dot(*C2, C_LINE_WIDTH),
        *solidify_lines(C_LINE_WIDTH, [C8, t(C2, 0, C_LINE_WIDTH * 2)]),
    ],
    C_GLYPH_WIDTH,
)
quotedbl_dist = C_LINE_WIDTH
overrides.quotedbl = short_get_glyph_generator(
    [t(C8, -quotedbl_dist, 0), t(C8, -quotedbl_dist, -C_LINE_WIDTH)],
    [t(C8, quotedbl_dist, 0), t(C8, quotedbl_dist, -C_LINE_WIDTH)],
)
numbersign_shear = 40
overrides.numbersign = short_get_glyph_generator(
    [
        t(midpoint(C7, C8), numbersign_shear, 10),
        t(midpoint(C1, C2), -numbersign_shear, -10),
    ],
    [
        t(midpoint(C8, C9), numbersign_shear, 10),
        t(midpoint(C2, C3), -numbersign_shear, -10),
    ],
    [midpoint(C7, C4), midpoint(C9, C6)],
    [midpoint(C4, C1), midpoint(C6, C3)],
)
overrides.dollar = get_glyph_generator(
    contour_union(
        *solidify_lines(
            C_LINE_WIDTH,
            [B8, B2],
        ),
        *S_contour,
    ),
    C_GLYPH_WIDTH,
)
overrides.percent = short_get_glyph_generator(
    [C7, C8, C5, C4, C7], [lerp(C1, C9, -1), lerp(C1, C9, 2)], [C5, C6, C3, C2, C5]
)


ampersand_contour7 = contour_intersection(
    C_OUTLINE,
    *find_solution(
        lambda a: solidify_lines(
            C_LINE_WIDTH,
            [midpoint(C8, C9), C7, t(C7, 0, -a), lerp(t(C7, 0, -a), C3, 2)],
            et=ET_OPENBUTT,
        ),
        [
            {
                "start": 0,
                "fn": lambda contour: -(
                    contour[0][4][1] - contour[0][5][1] - C_LINE_WIDTH
                ),
            }
        ],
    ),
)
ampersand_contour = find_solution(
    lambda a, b: contour_union(
        *contour_intersection(
            rect(
                C_LEFT,
                middle(C_TOP, C_BOTTOM) + C_LINE_WIDTH / 2,
                C_RIGHT,
                C_BOTTOM,
            ),
            *solidify_lines(
                C_LINE_WIDTH,
                [C5, C4, C1, t(C2, a, 0), t(lerp(C2, C6, 2), b, 0)],
                et=ET_OPENBUTT,
            ),
        ),
        *ampersand_contour7,
    ),
    [
        {"start": 0, "fn": lambda c: c[1][3][0] - c[1][0][0]},
        {"start": -40, "fn": lambda c: c[0][1][0] - c[0][7][0]},
    ],
)
overrides.ampersand = get_glyph_generator(ampersand_contour, C_GLYPH_WIDTH)
overrides.quotesingle = short_get_glyph_generator([C8, t(C8, 0, -C_LINE_WIDTH)])
paren_chamfer = dist(B7, B8)
overrides.parenleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, *chamfer_13(B7, paren_chamfer), *chamfer_04(B1, paren_chamfer), B3],
    ),
    C_GLYPH_WIDTH,
)
overrides.parenright = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B1, *chamfer_31(B3, paren_chamfer), *chamfer_22(B9, paren_chamfer), B7],
    ),
    C_GLYPH_WIDTH,
)
asterisk_spoke_count = 5
asterisk_spoke = solidify_lines(
    C_LINE_WIDTH, [[0, 0], [0, hyphen_half_width]], et=ET_OPENBUTT
)[0]
overrides.asterisk = get_glyph_generator(
    [
        contour_translate(
            contour_union(
                *[
                    contour_rotate(
                        asterisk_spoke, 2 * math.pi * (i / asterisk_spoke_count)
                    )
                    for i in range(asterisk_spoke_count)
                ]
            )[0],
            *C5,
        )
    ],
    C_GLYPH_WIDTH,
)
overrides.plus = get_glyph_generator(
    contour_union(
        *hyphen_contour,
        contour_translate(
            contour_rotate(
                contour_translate(*hyphen_contour, *s(C5, -1, -1)), math.pi / 2
            ),
            *C5,
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.comma = get_glyph_generator([comma_contour], C_GLYPH_WIDTH)
overrides.hyphen = get_glyph_generator(hyphen_contour, C_GLYPH_WIDTH)
overrides.period = get_glyph_generator([period_contour], C_GLYPH_WIDTH)
slash_clip = rect(
    BC7[0] - C_HALF_LINE_WIDTH,
    BC7[1] + C_HALF_LINE_WIDTH,
    BC3[0] + C_HALF_LINE_WIDTH,
    BC3[1] - C_HALF_LINE_WIDTH,
)
overrides.slash = get_glyph_generator(
    contour_intersection(
        slash_clip,
        *solidify_lines(C_LINE_WIDTH, [lerp(BC1, BC9, -1), lerp(BC1, BC9, 2)]),
    ),
    C_GLYPH_WIDTH,
)

# endregion

# region NUMBERS

overrides.zero = get_glyph_generator(
    contour_union(*O_contour, *solidify_lines(C_LINE_WIDTH, [C1, C9], et=ET_OPENBUTT)),
    C_GLYPH_WIDTH,
)
overrides.one = short_get_glyph_generator([C7, C8, C2], [C1, C3])
overrides.two = short_get_glyph_generator([C7, C9, C6, C4, C1, C3])
overrides.three = short_get_glyph_generator([C7, C9, C3, C1], [C6, midpoint(C4, C5)])
overrides.four = short_get_glyph_generator([C7, C4, C6], [C9, C3])
overrides.five = short_get_glyph_generator([C9, C7, C4, C6, C3, C1])
overrides.six = short_get_glyph_generator([C9, C7, C1, C3, C6, C4])
overrides.seven = short_get_glyph_generator([C7, C9, C3], [C5, C6])
overrides.eight = get_glyph_generator(
    contour_union(*O_contour, *solidify_lines(C_LINE_WIDTH, [C4, C6])),
    C_GLYPH_WIDTH,
)
overrides.nine = short_get_glyph_generator([C1, C3, C9, C7, C4, C6])

# endregion

# region 0x3A - 0x40

overrides.colon = get_glyph_generator([period_contour, top_dot_contour], C_GLYPH_WIDTH)
overrides.semicolon = get_glyph_generator(
    [comma_contour, top_dot_contour], C_GLYPH_WIDTH
)
less_size = 190
less_contour = contour_intersection(
    C_OUTLINE,
    *solidify_lines(
        C_LINE_WIDTH,
        [lerp(C4, t(C6, 0, less_size), 2), C4, lerp(C4, t(C6, 0, -less_size), 2)],
    ),
)[0]
overrides.less = get_glyph_generator([less_contour], C_GLYPH_WIDTH)
equal_spacing = C_LINE_WIDTH
overrides.equal = get_glyph_generator(
    [
        contour_translate(*hyphen_contour, 0, -equal_spacing),
        contour_translate(*hyphen_contour, 0, equal_spacing),
    ],
    C_GLYPH_WIDTH,
)
greater_contour = contour_translate(contour_scale(contour_translate(less_contour, *s(C5, -1, -1)), -1, 1), *C5)
overrides.greater = get_glyph_generator([greater_contour], C_GLYPH_WIDTH)
overrides.question = get_glyph_generator(
    contour_union(
        dot(size=C_LINE_WIDTH, *C2),
        *solidify_lines(
            C_LINE_WIDTH,
            [midpoint(C7, C4), C7, C9, C6, C5, midpoint(C5, C2)],
            et=ET_OPENBUTT,
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.at = short_get_glyph_generator(
    [C2, C5, C4, C1, C3, C9, C7, midpoint(C7, C4)], et=ET_OPENBUTT
)

# endregion

# region CAPITAL LETTERS

overrides.A = short_get_glyph_generator([C1, C7, C9, C6, C3, C6, C4])
overrides.B = short_get_glyph_generator(
    [
        C4,
        C6,
        C3,
        C1,
        C7,
        t(C9, -C_LINE_WIDTH, 0),
        t(C6, -C_LINE_WIDTH, 0),
    ]
)
overrides.C = short_get_glyph_generator([C9, C7, C1, C3])
D_offset = dist(midpoint(C2, C3), C3)
overrides.D = short_get_glyph_generator(
    [
        C7,
        C1,
        t(C3, -D_offset, 0),
        t(C3, 0, D_offset),
        t(C9, 0, -D_offset),
        t(C9, -D_offset, 0),
        C7,
    ]
)
overrides.E = short_get_glyph_generator([C9, C7, C4, midpoint(C5, C6), C4, C1, C3])
overrides.F = short_get_glyph_generator([C9, C7, C4, midpoint(C5, C6), C4, C1])
overrides.G = short_get_glyph_generator([C9, C7, C1, C3, C6, C5])
overrides.H = short_get_glyph_generator([C1, C7, C4, C6, C9, C3])
overrides.I = short_get_glyph_generator([C7, C9, C8, C2, C1, C3])
overrides.J = short_get_glyph_generator([C8, C9, C3, C1, midpoint(C1, C4)])
overrides.K = short_get_glyph_generator(
    [C7, C1, C4, lerp(C4, C9, 2), C4, lerp(C4, C3, 2)]
)
overrides.L = short_get_glyph_generator([C7, C1, C3])
overrides.M = get_glyph_generator(
    M_contour,
    C_GLYPH_WIDTH,
)
overrides.N = get_glyph_generator(
    find_solution(
        lambda a: solidify_lines(
            C_LINE_WIDTH,
            [
                C1,
                C7,
                t(C7, a, 0),
                t(C3, -a, 0),
                C3,
                C9,
            ],
        ),
        [
            {
                "start": 50,
                "fn": lambda contour: -(
                    contour[0][2][0] - contour[0][1][0] - C_LINE_WIDTH
                ),
            }
        ],
    ),
    C_GLYPH_WIDTH,
)
overrides.O = get_glyph_generator(O_contour, C_GLYPH_WIDTH)
overrides.P = short_get_glyph_generator([C1, C7, C9, C6, C4])
overrides.Q = get_glyph_generator(
    contour_union(
        *O_contour,
        *contour_intersection(
            rect(
                middle(C_RIGHT, C_LEFT) - 30,
                C_BOTTOM + middle(C_RIGHT, C_LEFT) - C_LEFT + 30,
                C_RIGHT,
                C_BOTTOM,
            ),
            *solidify_lines(C_LINE_WIDTH, [t(C3, -9999, 9999), C3], et=ET_OPENBUTT),
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.R = short_get_glyph_generator([C1, C7, C9, C6, C4, C5, lerp(C5, C3, 2)])
overrides.S = get_glyph_generator(S_contour, C_GLYPH_WIDTH)
overrides.T = short_get_glyph_generator([C7, C9, C8, C2])
overrides.U = short_get_glyph_generator([C7, C1, C3, C9])


def Vv_contour_generator(height):
    pa = {
        "start": -50,
        "fn": lambda contour: contour[0][0][0] - contour[0][4][0] - (C_RIGHT - C_LEFT),
    }
    pb = {
        "start": 0,
        # the -2 is needed to prevent it from oscillating forever
        "fn": lambda contour: -(
            contour[0][6][0]
            - contour[0][5][0]
            - (contour[0][0][0] - contour[0][1][0] - 2)
        ),
    }
    sol = find_solution(
        lambda a, b: contour_intersection(
            rect(-9999, height, 9999, 0),
            *solidify_lines(
                C_LINE_WIDTH,
                [
                    t(C7, a, 50),
                    t(C2, -b, 0),
                    t(C2, b, 0),
                    t(C9, -a, 50),
                ],
            ),
        ),
        [pa, pb],
    )
    return sol, pa["result"], pb["result"]


V_contour, _, _ = Vv_contour_generator(C_TOP)
overrides.V = get_glyph_generator(V_contour, C_GLYPH_WIDTH)
overrides.W = get_glyph_generator(W_contour, C_GLYPH_WIDTH)
overrides.X = short_get_glyph_generator(
    [lerp(C7, C3, -1), lerp(C7, C3, 2)], [lerp(C9, C1, -1), lerp(C9, C1, 2)]
)
overrides.Y = short_get_glyph_generator([lerp(C5, C7, 2), C5, C2, C5, lerp(C5, C9, 2)])
overrides.Z = get_glyph_generator(
    contour_union(
        *find_solution(
            lambda a: solidify_lines(
                C_LINE_WIDTH, [C7, C9, t(C9, 0, -a), t(C1, 0, a), C1, C3]
            ),
            [
                {
                    "start": 0,
                    "fn": lambda contour: -(
                        contour[0][3][1] - contour[0][2][1] - C_LINE_WIDTH
                    ),
                }
            ],
        ),
        *solidify_lines(C_LINE_WIDTH, [C4, C6], et=ET_OPENBUTT),
    ),
    C_GLYPH_WIDTH,
)

# endregion

# region 0x5B - 0x60

overrides.bracketleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, B7, B1, B3],
    ),
    C_GLYPH_WIDTH,
)
overrides.backslash = get_glyph_generator(
    contour_intersection(
        slash_clip,
        *solidify_lines(C_LINE_WIDTH, [lerp(BC7, BC3, -1), lerp(BC7, BC3, 2)]),
    ),
    C_GLYPH_WIDTH,
)
overrides.bracketright = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B1, B3, B9, B7],
    ),
    C_GLYPH_WIDTH,
)
asciicircum_size = 200
overrides.asciicircum = get_glyph_generator(
    contour_intersection(
        rect(
            C8[0] - asciicircum_size,
            FONT_ASCENDER,
            C8[0] + asciicircum_size,
            C8[1] - asciicircum_size,
        ),
        *solidify_lines(C_LINE_WIDTH, [t(C8, -999, -999), C8, t(C8, 999, -999)]),
    ),
    C_GLYPH_WIDTH,
)
overrides.underscore = short_get_glyph_generator([C1, C3])
overrides.grave = get_glyph_generator(
    [
        contour_translate(
            *contour_intersection(
                rect(-9999, 110, 9999, -110),
                *solidify_lines(C_LINE_WIDTH, [[-9999, 9999], [9999, -9999]]),
            ),
            *t(C8, 0, -35),
        )
    ],
    C_GLYPH_WIDTH,
)

# endregion

# region LOWER CASE LETTERS

chamfer_distance = 70
overrides.a = short_get_glyph_generator([X1, X3, C3, C1, W1, W3])
overrides.b = short_get_glyph_generator([C7, C1, C3, X3, X1])
overrides.c = short_get_glyph_generator([X3, X1, C1, C3])
overrides.d = short_get_glyph_generator([C9, C3, C1, X1, X3])
overrides.e = short_get_glyph_generator([C3, C1, X1, X3, W3, W1])
f_cross_y_offset = -40
overrides.f = short_get_glyph_generator(
    [
        C9,
        *chamfer_13(t(C7, C_LINE_WIDTH, 0), chamfer_distance),
        t(C1, C_LINE_WIDTH, 0),
    ],
    [
        t(X1, 0, f_cross_y_offset),
        t(X1, C_LINE_WIDTH * 2.5, f_cross_y_offset),
    ],
)
overrides.g = short_get_glyph_generator([D1, D3, X3, X1, C1, C3], clip=None)
overrides.h = short_get_glyph_generator([C7, C1], [X1, X3, C3])
ij_dot_location = t(X2, 0, C_LINE_WIDTH * 0.65 + C_LINE_WIDTH / 2 + C_TITTLE_SIZE / 2)
i_vbar_offset = (C_TITTLE_SIZE - C_LINE_WIDTH) / 2
overrides.i = get_glyph_generator(
    [
        dot(*ij_dot_location, C_TITTLE_SIZE),
        *solidify_lines(
            C_LINE_WIDTH,
            [X1, t(X2, i_vbar_offset, 0), t(C2, i_vbar_offset, 0)],
            [C1, C3],
        ),
    ],
    C_GLYPH_WIDTH,
)
overrides.j = get_glyph_generator(
    [
        dot(*t(ij_dot_location, C_LINE_WIDTH * 0.5, 0), C_TITTLE_SIZE),
        *solidify_lines(
            C_LINE_WIDTH,
            [
                t(X1, C_LINE_WIDTH, 0),
                X3,
                *chamfer_31(D3, dist(D2, D3), flip=True),
                D1,
            ],
        ),
    ],
    C_GLYPH_WIDTH,
)
overrides.k = get_glyph_generator(
    contour_union(
        *solidify_lines(C_LINE_WIDTH, [C7, C1]),
        *contour_intersection(
            C_LOWERCASE_O_OUTLINE,
            *solidify_lines(C_LINE_WIDTH, [lerp(W1, X3, 2), W1, lerp(W1, C3, 2)]),
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.l = short_get_glyph_generator([C7, C8, *chamfer_04(C2, chamfer_distance), C3])
overrides.m = short_get_glyph_generator([C1, X1, X3, C3], [X2, C2])
overrides.n = short_get_glyph_generator([C1, X1, X3, C3])
overrides.o = short_get_glyph_generator([C1, X1, X3, C3, C1])
overrides.p = short_get_glyph_generator([D1, X1, X3, C3, C1], clip=None)
overrides.q = short_get_glyph_generator([D3, X3, X1, C1, C3], clip=None)
overrides.r = short_get_glyph_generator([C1, X1, X3])
overrides.s = short_get_glyph_generator([C1, C3, W3, W1, X1, X3])
t_C3_chf = chamfer_31(C3, chamfer_distance)
overrides.t = get_glyph_generator(
    contour_union(
        *find_solution(
            lambda a: contour_intersection(
                [
                    [C_RIGHT, C_BOTTOM],
                    [C_LEFT, C_BOTTOM],
                    [C_LEFT, C_TOP],
                    [C_RIGHT - 200, C_TOP],
                    [C_RIGHT - 200, a],
                    [C_RIGHT, a],
                ],
                *solidify_lines(
                    C_LINE_WIDTH,
                    [
                        t(C7, C_LINE_WIDTH, 0),
                        *chamfer_04(t(C1, C_LINE_WIDTH, 0), chamfer_distance),
                        t_C3_chf[0],
                        lerp(t_C3_chf[0], t_C3_chf[1], 2),
                    ],
                ),
            ),
            [
                {
                    "start": 120,
                    "fn": lambda c: (c[0][1][0] - c[0][2][0])
                    - (c[0][1][1] - c[0][0][1]),
                }
            ],
        ),
        *solidify_lines(
            C_LINE_WIDTH,
            [
                t(X1, 0, 0),
                t(X1, C_LINE_WIDTH * 2.5, 0),
            ],
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.u = short_get_glyph_generator([X1, C1, C3, X3])
v_contour, a, b = Vv_contour_generator(X_HEIGHT)
overrides.v = get_glyph_generator(v_contour, C_GLYPH_WIDTH)
overrides.w = short_get_glyph_generator([X1, C1, C3, X3], [X2, C2])
overrides.x = short_get_glyph_generator(
    [lerp(X1, C3, -1), lerp(X1, C3, 2)],
    [lerp(C1, X3, -1), lerp(C1, X3, 2)],
    clip=C_LOWERCASE_O_OUTLINE,
)
overrides.y = get_glyph_generator(
    contour_intersection(
        rect(-9999, X_HEIGHT, 9999, FONT_DESCENDER),
        *solidify_lines(
            C_LINE_WIDTH,
            [
                t(C7, a, 50),
                t(C2, -b, 0),
                t(C2, b, 0),
                t(C9, -a, 50),
                lerp(t(C9, -a, 50), t(C2, b, 0), 2),
            ],
        ),
    ),
    C_GLYPH_WIDTH,
)
overrides.z = get_glyph_generator(
    contour_union(
        *find_solution(
            lambda a: solidify_lines(
                C_LINE_WIDTH, [X1, X3, t(X3, 0, -a), t(C1, 0, a), C1, C3]
            ),
            [
                {
                    "start": 0,
                    "fn": lambda contour: -(
                        contour[0][3][1] - contour[0][2][1] - C_LINE_WIDTH
                    ),
                }
            ],
        )
    ),
    C_GLYPH_WIDTH,
)

# endregion

# region 0x7B - 0x7F

overrides.braceleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, *chamfer_13(B7, paren_chamfer), B5, *chamfer_04(B1, paren_chamfer), B3],
        [t(C5, C_LINE_WIDTH / -2, 0), t(C5, -dist(B7, B9), 0)],
    ),
    C_GLYPH_WIDTH,
)
overrides.bar = get_glyph_generator(
    solidify_lines(C_LINE_WIDTH, [B8, B2]),
    C_GLYPH_WIDTH,
)
overrides.braceright = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B1, *chamfer_31(B3, paren_chamfer), B5, *chamfer_22(B9, paren_chamfer), B7],
        [t(C5, C_LINE_WIDTH / 2, 0), t(C5, dist(B7, B9), 0)],
    ),
    C_GLYPH_WIDTH,
)
tilde_spacing = C_LINE_WIDTH / 2
overrides.asciitilde = short_get_glyph_generator(
    [
        t(C4, 0, -tilde_spacing),
        t(C4, 0, tilde_spacing),
        t(C5, 0, tilde_spacing),
        t(C5, 0, -tilde_spacing),
        t(C6, 0, -tilde_spacing),
        t(C6, 0, tilde_spacing),
    ],
    jt=JT_SQUARE,
)

overrides.sterling = short_get_glyph_generator(
    [C3, C1, midpoint(C1, C2), midpoint(C7, C8), midpoint(C8, C9)],
    [C4, midpoint(C5, C6)],
)

# endregion


overrides.section=get_glyph_generator([rect(0, FONT_ASCENDER, C_GLYPH_WIDTH, FONT_DESCENDER)], C_GLYPH_WIDTH)