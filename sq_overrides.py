from glyph_tools import *
from types import SimpleNamespace as Namespace

sq_overrides = Namespace()

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

sq_overrides.space = get_glyph_generator([], C_GLYPH_WIDTH)
sq_overrides.exclam = get_glyph_generator(
    [
        dot(*C2, C_LINE_WIDTH),
        *solidify_lines(C_LINE_WIDTH, [C8, t(C2, 0, C_LINE_WIDTH * 2)]),
    ],
    C_GLYPH_WIDTH,
)
quotedbl_dist = C_LINE_WIDTH
sq_overrides.quotedbl = short_get_glyph_generator(
    [t(C8, -quotedbl_dist, 0), t(C8, -quotedbl_dist, -C_LINE_WIDTH)],
    [t(C8, quotedbl_dist, 0), t(C8, quotedbl_dist, -C_LINE_WIDTH)],
)
numbersign_shear = 40
sq_overrides.numbersign = short_get_glyph_generator(
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
sq_overrides.dollar = get_glyph_generator(
    contour_union(
        *solidify_lines(
            C_LINE_WIDTH,
            [B8, B2],
        ),
        *S_contour,
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.percent = short_get_glyph_generator(
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
sq_overrides.ampersand = get_glyph_generator(ampersand_contour, C_GLYPH_WIDTH)
sq_overrides.quotesingle = short_get_glyph_generator([C8, t(C8, 0, -C_LINE_WIDTH)])
paren_chamfer = dist(B7, B8)
sq_overrides.parenleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, *chamfer_13(B7, paren_chamfer), *chamfer_04(B1, paren_chamfer), B3],
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.parenright = get_glyph_generator(
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
sq_overrides.asterisk = get_glyph_generator(
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
sq_overrides.plus = get_glyph_generator(
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
sq_overrides.comma = get_glyph_generator([comma_contour], C_GLYPH_WIDTH)
sq_overrides.hyphen = get_glyph_generator(hyphen_contour, C_GLYPH_WIDTH)
sq_overrides.period = get_glyph_generator([period_contour], C_GLYPH_WIDTH)
slash_clip = rect(
    BC7[0] - C_HALF_LINE_WIDTH,
    BC7[1] + C_HALF_LINE_WIDTH,
    BC3[0] + C_HALF_LINE_WIDTH,
    BC3[1] - C_HALF_LINE_WIDTH,
)
sq_overrides.slash = get_glyph_generator(
    contour_intersection(
        slash_clip,
        *solidify_lines(C_LINE_WIDTH, [lerp(BC1, BC9, -1), lerp(BC1, BC9, 2)]),
    ),
    C_GLYPH_WIDTH,
)

# endregion

# region NUMBERS

sq_overrides.zero = get_glyph_generator(
    contour_union(*O_contour, *solidify_lines(C_LINE_WIDTH, [C1, C9], et=ET_OPENBUTT)),
    C_GLYPH_WIDTH,
)
sq_overrides.one = short_get_glyph_generator([C7, C8, C2], [C1, C3])
sq_overrides.two = short_get_glyph_generator([C7, C9, C6, C4, C1, C3])
sq_overrides.three = short_get_glyph_generator([C7, C9, C3, C1], [C6, midpoint(C4, C5)])
sq_overrides.four = short_get_glyph_generator([C7, C4, C6], [C9, C3])
sq_overrides.five = short_get_glyph_generator([C9, C7, C4, C6, C3, C1])
sq_overrides.six = short_get_glyph_generator([C9, C7, C1, C3, C6, C4])
sq_overrides.seven = short_get_glyph_generator([C7, C9, C3], [C5, C6])
sq_overrides.eight = get_glyph_generator(
    contour_union(*O_contour, *solidify_lines(C_LINE_WIDTH, [C4, C6])),
    C_GLYPH_WIDTH,
)
sq_overrides.nine = short_get_glyph_generator([C1, C3, C9, C7, C4, C6])

# endregion

# region 0x3A - 0x40

sq_overrides.colon = get_glyph_generator(
    [period_contour, top_dot_contour], C_GLYPH_WIDTH
)
sq_overrides.semicolon = get_glyph_generator(
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
sq_overrides.less = get_glyph_generator([less_contour], C_GLYPH_WIDTH)
equal_spacing = C_LINE_WIDTH
sq_overrides.equal = get_glyph_generator(
    [
        contour_translate(*hyphen_contour, 0, -equal_spacing),
        contour_translate(*hyphen_contour, 0, equal_spacing),
    ],
    C_GLYPH_WIDTH,
)
greater_contour = contour_translate(
    contour_scale(contour_translate(less_contour, *s(C5, -1, -1)), -1, 1), *C5
)
sq_overrides.greater = get_glyph_generator([greater_contour], C_GLYPH_WIDTH)
sq_overrides.question = get_glyph_generator(
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
sq_overrides.at = short_get_glyph_generator(
    [C2, C5, C4, C1, C3, C9, C7, midpoint(C7, C4)], et=ET_OPENBUTT
)

# endregion

# region CAPITAL LETTERS

sq_overrides.A = short_get_glyph_generator([C1, C7, C9, C6, C3, C6, C4])
sq_overrides.B = short_get_glyph_generator(
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
sq_overrides.C = short_get_glyph_generator([C9, C7, C1, C3])
D_offset = dist(midpoint(C2, C3), C3)
sq_overrides.D = short_get_glyph_generator(
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
sq_overrides.E = short_get_glyph_generator([C9, C7, C4, midpoint(C5, C6), C4, C1, C3])
sq_overrides.F = short_get_glyph_generator([C9, C7, C4, midpoint(C5, C6), C4, C1])
sq_overrides.G = short_get_glyph_generator([C9, C7, C1, C3, C6, C5])
sq_overrides.H = short_get_glyph_generator([C1, C7, C4, C6, C9, C3])
sq_overrides.I = short_get_glyph_generator([C7, C9, C8, C2, C1, C3])
sq_overrides.J = short_get_glyph_generator([C8, C9, C3, C1, midpoint(C1, C4)])
sq_overrides.K = short_get_glyph_generator(
    [C7, C1, C4, lerp(C4, C9, 2), C4, lerp(C4, C3, 2)]
)
sq_overrides.L = short_get_glyph_generator([C7, C1, C3])
sq_overrides.M = get_glyph_generator(
    M_contour,
    C_GLYPH_WIDTH,
)
sq_overrides.N = get_glyph_generator(
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
sq_overrides.O = get_glyph_generator(O_contour, C_GLYPH_WIDTH)
sq_overrides.P = short_get_glyph_generator([C1, C7, C9, C6, C4])
sq_overrides.Q = get_glyph_generator(
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
sq_overrides.R = short_get_glyph_generator([C1, C7, C9, C6, C4, C5, lerp(C5, C3, 2)])
sq_overrides.S = get_glyph_generator(S_contour, C_GLYPH_WIDTH)
sq_overrides.T = short_get_glyph_generator([C7, C9, C8, C2])
sq_overrides.U = short_get_glyph_generator([C7, C1, C3, C9])


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
sq_overrides.V = get_glyph_generator(V_contour, C_GLYPH_WIDTH)
sq_overrides.W = get_glyph_generator(W_contour, C_GLYPH_WIDTH)
sq_overrides.X = short_get_glyph_generator(
    [lerp(C7, C3, -1), lerp(C7, C3, 2)], [lerp(C9, C1, -1), lerp(C9, C1, 2)]
)
sq_overrides.Y = short_get_glyph_generator(
    [lerp(C5, C7, 2), C5, C2, C5, lerp(C5, C9, 2)]
)
sq_overrides.Z = get_glyph_generator(
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

sq_overrides.bracketleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, B7, B1, B3],
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.backslash = get_glyph_generator(
    contour_intersection(
        slash_clip,
        *solidify_lines(C_LINE_WIDTH, [lerp(BC7, BC3, -1), lerp(BC7, BC3, 2)]),
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.bracketright = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B1, B3, B9, B7],
    ),
    C_GLYPH_WIDTH,
)
asciicircum_size = 200
sq_overrides.asciicircum = get_glyph_generator(
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
sq_overrides.underscore = short_get_glyph_generator([C1, C3])
sq_overrides.grave = get_glyph_generator(
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
sq_overrides.a = short_get_glyph_generator([X1, X3, C3, C1, W1, W3])
sq_overrides.b = short_get_glyph_generator([C7, C1, C3, X3, X1])
sq_overrides.c = short_get_glyph_generator([X3, X1, C1, C3])
sq_overrides.d = short_get_glyph_generator([C9, C3, C1, X1, X3])
sq_overrides.e = short_get_glyph_generator([C3, C1, X1, X3, W3, W1])
f_cross_y_offset = -40
sq_overrides.f = short_get_glyph_generator(
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
sq_overrides.g = short_get_glyph_generator([D1, D3, X3, X1, C1, C3], clip=None)
sq_overrides.h = short_get_glyph_generator([C7, C1], [X1, X3, C3])
ij_dot_location = t(X2, 0, C_LINE_WIDTH * 0.65 + C_LINE_WIDTH / 2 + C_TITTLE_SIZE / 2)
i_vbar_offset = (C_TITTLE_SIZE - C_LINE_WIDTH) / 2
sq_overrides.i = get_glyph_generator(
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
sq_overrides.j = get_glyph_generator(
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
sq_overrides.k = get_glyph_generator(
    contour_union(
        *solidify_lines(C_LINE_WIDTH, [C7, C1]),
        *contour_intersection(
            C_LOWERCASE_O_OUTLINE,
            *solidify_lines(C_LINE_WIDTH, [lerp(W1, X3, 2), W1, lerp(W1, C3, 2)]),
        ),
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.l = short_get_glyph_generator(
    [C7, C8, *chamfer_04(C2, chamfer_distance), C3]
)
sq_overrides.m = short_get_glyph_generator([C1, X1, X3, C3], [X2, C2])
sq_overrides.n = short_get_glyph_generator([C1, X1, X3, C3])
sq_overrides.o = short_get_glyph_generator([C1, X1, X3, C3, C1])
sq_overrides.p = short_get_glyph_generator([D1, X1, X3, C3, C1], clip=None)
sq_overrides.q = short_get_glyph_generator([D3, X3, X1, C1, C3], clip=None)
sq_overrides.r = short_get_glyph_generator([C1, X1, X3])
sq_overrides.s = short_get_glyph_generator([C1, C3, W3, W1, X1, X3])
t_C3_chf = chamfer_31(C3, chamfer_distance)
sq_overrides.t = get_glyph_generator(
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
sq_overrides.u = short_get_glyph_generator([X1, C1, C3, X3])
v_contour, a, b = Vv_contour_generator(X_HEIGHT)
sq_overrides.v = get_glyph_generator(v_contour, C_GLYPH_WIDTH)
sq_overrides.w = short_get_glyph_generator([X1, C1, C3, X3], [X2, C2])
sq_overrides.x = short_get_glyph_generator(
    [lerp(X1, C3, -1), lerp(X1, C3, 2)],
    [lerp(C1, X3, -1), lerp(C1, X3, 2)],
    clip=C_LOWERCASE_O_OUTLINE,
)
sq_overrides.y = get_glyph_generator(
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
sq_overrides.z = get_glyph_generator(
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

sq_overrides.braceleft = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B9, *chamfer_13(B7, paren_chamfer), B5, *chamfer_04(B1, paren_chamfer), B3],
        [t(C5, C_LINE_WIDTH / -2, 0), t(C5, -dist(B7, B9), 0)],
    ),
    C_GLYPH_WIDTH,
)
sq_overrides.bar = get_glyph_generator(
    solidify_lines(C_LINE_WIDTH, [B8, B2]),
    C_GLYPH_WIDTH,
)
sq_overrides.braceright = get_glyph_generator(
    solidify_lines(
        C_LINE_WIDTH,
        [B1, *chamfer_31(B3, paren_chamfer), B5, *chamfer_22(B9, paren_chamfer), B7],
        [t(C5, C_LINE_WIDTH / 2, 0), t(C5, dist(B7, B9), 0)],
    ),
    C_GLYPH_WIDTH,
)
tilde_spacing = C_LINE_WIDTH / 2
sq_overrides.asciitilde = short_get_glyph_generator(
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

sq_overrides.sterling = short_get_glyph_generator(
    [C3, C1, midpoint(C1, C2), midpoint(C7, C8), midpoint(C8, C9)],
    [C4, midpoint(C5, C6)],
)

# endregion
