"""ANSI COLOR CODES.

colors.bat: Sets specific color codes as ENV C... check using C_set C_, also see colors.py
https://en.wikipedia.org/wiki/ANSI_escape_code
https://ss64.com/nt/syntax-ansi.html
https://stackoverflow.com/questions/2048509/how-to-echo-with-different-colors-in-the-windows-command-line
https://gist.github.com/mlocati/fdabcaeb8071d5c75a2d51712db24011#file-win10colors-cmd
define a newline variable spaces need to be kept
https://stackoverflow.com/questions/132799/how-can-i-echo-a-newline-in-a-batch-file
https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
38;5;f is font color and 48;5;b background color with numbers from 16...231

"""

# Escape codes for ANSI colors (foreground)
ESC_CODE_WHITE = "\033[37m"
ESC_CODE_TITLE = "\033[38;5;45m"
ESC_CODE_RESET = "\033[0m"
COLOR_GROUPS = [
    "gray_and_black",
    "blue",
    "cyan",
    "green",
    "yellow",
    "orange",
    "red",
    "purple_violet_and_magenta",
    "pink",
    "white",
    "brown",
]

ANSI_COLOR = {
    0: {"index": 0, "names": ["black", "black_000"], "color_group": "gray_and_black"},
    1: {"index": 1, "names": ["maroon"], "color_group": "red"},
    2: {"index": 2, "names": ["office_green"], "color_group": "green"},
    3: {"index": 3, "names": ["yellow_003"], "color_group": "green"},
    4: {"index": 4, "names": ["blue_004"], "color_group": "blue"},
    5: {"index": 5, "names": ["patriarch"], "color_group": "purple_violet_and_magenta"},
    6: {"index": 6, "names": ["cyan_006"], "color_group": "cyan"},
    7: {"index": 7, "names": ["argent"], "color_group": "gray_and_black"},
    8: {"index": 8, "names": ["gray", "light_black"], "color_group": "gray_and_black"},
    9: {"index": 9, "names": ["light_red", "red"], "color_group": "red"},
    10: {"index": 10, "names": ["electric_green", "green", "light_green_010"], "color_group": "green"},
    11: {"index": 11, "names": ["light_yellow_011", "yellow"], "color_group": "yellow"},
    12: {"index": 12, "names": ["blue", "light_blue_012"], "color_group": "blue"},
    13: {"index": 13, "names": ["fuchsia", "light_magenta_013", "magenta"], "color_group": "pink"},
    14: {"index": 14, "names": ["aqua", "cyan", "light_cyan_014"], "color_group": "cyan"},
    15: {"index": 15, "names": ["light_white", "white"], "color_group": "white"},
    16: {"index": 16, "names": ["black", "black_000"], "color_group": "gray_and_black"},
    17: {"index": 17, "names": ["fuzzy_wuzzy", "stratos", "very_dark_blue"], "color_group": "blue"},
    18: {"index": 18, "names": ["dark_blue", "navy_blue"], "color_group": "blue"},
    19: {"index": 19, "names": ["carnation_pink", "duke_blue"], "color_group": "blue"},
    20: {"index": 20, "names": ["medium_blue"], "color_group": "blue"},
    21: {"index": 21, "names": ["blue", "light_blue_012"], "color_group": "blue"},
    22: {"index": 22, "names": ["camarone", "very_dark_lime_green"], "color_group": "green"},
    23: {
        "index": 23,
        "names": ["bangladesh_green", "blue_stone", "dark_slate_gray", "very_dark_cyan"],
        "color_group": "green",
    },
    24: {"index": 24, "names": ["orient", "sea_blue"], "color_group": "blue"},
    25: {"index": 25, "names": ["endeavour", "medium_persian_blue"], "color_group": "blue"},
    26: {"index": 26, "names": ["science_blue", "true_blue"], "color_group": "blue"},
    27: {"index": 27, "names": ["blue_ribbon", "brandeis_blue"], "color_group": "blue"},
    28: {"index": 28, "names": ["ao"], "color_group": "green"},
    29: {"index": 29, "names": ["deep_sea", "spanish_viridian"], "color_group": "green"},
    30: {"index": 30, "names": ["teal"], "color_group": "cyan"},
    31: {"index": 31, "names": ["deep_cerulean"], "color_group": "blue"},
    32: {"index": 32, "names": ["blue_cola", "lochmara", "strong_blue"], "color_group": "blue"},
    33: {"index": 33, "names": ["azure", "azure_radiance", "pure_blue"], "color_group": "blue"},
    34: {"index": 34, "names": ["dark_lime_green", "islamic_green", "japanese_laurel"], "color_group": "green"},
    35: {"index": 35, "names": ["go_green", "jade"], "color_group": "green"},
    36: {"index": 36, "names": ["dark_cyan", "persian_green"], "color_group": "green"},
    37: {"index": 37, "names": ["bondi_blue", "tiffany_blue"], "color_group": "cyan"},
    38: {"index": 38, "names": ["cerulean"], "color_group": "blue"},
    39: {"index": 39, "names": ["blue_bolt", "deep_sky_blue"], "color_group": "blue"},
    40: {"index": 40, "names": ["strong_lime_green"], "color_group": "green"},
    41: {"index": 41, "names": ["malachite"], "color_group": "green"},
    42: {"index": 42, "names": ["caribbean_green_042"], "color_group": "green"},
    43: {"index": 43, "names": ["caribbean_green", "strong_cyan"], "color_group": "green"},
    44: {"index": 44, "names": ["dark_turquoise", "robins_egg_blue"], "color_group": "cyan"},
    45: {"index": 45, "names": ["vivid_sky_blue"], "color_group": "blue"},
    46: {"index": 46, "names": ["electric_green", "green", "light_green_010"], "color_group": "green"},
    47: {"index": 47, "names": ["spring_green_047"], "color_group": "green"},
    48: {"index": 48, "names": ["guppie_green"], "color_group": "green"},
    49: {"index": 49, "names": ["medium_spring_green", "spring_green"], "color_group": "green"},
    50: {"index": 50, "names": ["bright_turquoise", "pure_cyan", "sea_green"], "color_group": "green"},
    51: {"index": 51, "names": ["aqua", "cyan", "light_cyan_014"], "color_group": "cyan"},
    52: {"index": 52, "names": ["blood_red", "rosewood", "very_dark_red"], "color_group": "red"},
    53: {
        "index": 53,
        "names": ["imperial_purple", "pompadour", "very_dark_magenta"],
        "color_group": "purple_violet_and_magenta",
    },
    54: {"index": 54, "names": ["metallic_violet", "pigment_indigo"], "color_group": "purple_violet_and_magenta"},
    55: {"index": 55, "names": ["chinese_purple", "dark_violet"], "color_group": "purple_violet_and_magenta"},
    56: {"index": 56, "names": ["electric_violet_056"], "color_group": "purple_violet_and_magenta"},
    57: {"index": 57, "names": ["electric_indigo"], "color_group": "purple_violet_and_magenta"},
    58: {
        "index": 58,
        "names": ["bronze_yellow", "verdun_green", "very_dark_yellow_olive_tone"],
        "color_group": "green",
    },
    59: {"index": 59, "names": ["scorpion"], "color_group": "gray_and_black"},
    60: {"index": 60, "names": ["comet", "mostly_desaturated_dark_blue", "ucla_blue"], "color_group": "blue"},
    61: {"index": 61, "names": ["dark_moderate_blue", "liberty", "scampi"], "color_group": "blue"},
    62: {"index": 62, "names": ["indigo", "slate_blue"], "color_group": "blue"},
    63: {"index": 63, "names": ["cornflower_blue"], "color_group": "blue"},
    64: {"index": 64, "names": ["avocado"], "color_group": "green"},
    65: {
        "index": 65,
        "names": ["glade_green", "mostly_desaturated_dark_lime_green", "russian_green"],
        "color_group": "green",
    },
    66: {"index": 66, "names": ["juniper", "mostly_desaturated_dark_cyan", "steel_teal"], "color_group": "cyan"},
    67: {"index": 67, "names": ["hippie_blue", "rackley", "steel_blue"], "color_group": "blue"},
    68: {"index": 68, "names": ["havelock_blue", "moderate_blue", "united_nations_blue"], "color_group": "blue"},
    69: {"index": 69, "names": ["blueberry", "light_blue"], "color_group": "blue"},
    70: {"index": 70, "names": ["dark_green", "kelly_green"], "color_group": "green"},
    71: {"index": 71, "names": ["dark_moderate_lime_green", "fern", "forest_green"], "color_group": "green"},
    72: {"index": 72, "names": ["polished_pine", "silver_tree"], "color_group": "green"},
    73: {"index": 73, "names": ["crystal_blue", "dark_moderate_cyan", "tradewind"], "color_group": "blue"},
    74: {"index": 74, "names": ["aqua_pearl", "carolina_blue", "shakespeare"], "color_group": "blue"},
    75: {"index": 75, "names": ["blue_jeans"], "color_group": "blue"},
    76: {"index": 76, "names": ["alien_armpit", "harlequin_green", "strong_green"], "color_group": "green"},
    77: {"index": 77, "names": ["moderate_lime_green"], "color_group": "green"},
    78: {"index": 78, "names": ["caribbean_green_pearl"], "color_group": "green"},
    79: {"index": 79, "names": ["downy", "eucalyptus"], "color_group": "green"},
    80: {"index": 80, "names": ["medium_turquoise", "moderate_cyan", "viking"], "color_group": "cyan"},
    81: {"index": 81, "names": ["maya_blue"], "color_group": "blue"},
    82: {"index": 82, "names": ["bright_green"], "color_group": "green"},
    83: {"index": 83, "names": ["light_lime_green"], "color_group": "green"},
    84: {"index": 84, "names": ["very_light_malachite_green"], "color_group": "green"},
    85: {"index": 85, "names": ["medium_aquamarine"], "color_group": "green"},
    86: {"index": 86, "names": ["aquamarine_086"], "color_group": "cyan"},
    87: {"index": 87, "names": ["aquamarine_087"], "color_group": "cyan"},
    88: {"index": 88, "names": ["deep_red"], "color_group": "red"},
    89: {"index": 89, "names": ["french_plum"], "color_group": "purple_violet_and_magenta"},
    90: {"index": 90, "names": ["fresh_eggplant", "mardi_gras"], "color_group": "purple_violet_and_magenta"},
    91: {"index": 91, "names": ["purple", "violet"], "color_group": "purple_violet_and_magenta"},
    92: {"index": 92, "names": ["french_violet", "strong_violet"], "color_group": "purple_violet_and_magenta"},
    93: {"index": 93, "names": ["electric_violet", "pure_violet"], "color_group": "purple_violet_and_magenta"},
    94: {"index": 94, "names": ["brown", "gamboge_orange"], "color_group": "brown"},
    95: {"index": 95, "names": ["copper_rose", "deep_taupe", "mostly_desaturated_dark_red"], "color_group": "brown"},
    96: {
        "index": 96,
        "names": ["chinese_violet", "mostly_desaturated_dark_magenta", "strikemaster"],
        "color_group": "purple_violet_and_magenta",
    },
    97: {
        "index": 97,
        "names": ["dark_moderate_violet", "deluge", "royal_purple"],
        "color_group": "purple_violet_and_magenta",
    },
    98: {"index": 98, "names": ["medium_purple", "moderate_violet"], "color_group": "purple_violet_and_magenta"},
    99: {"index": 99, "names": ["blueberry_099"], "color_group": "purple_violet_and_magenta"},
    100: {"index": 100, "names": ["dark_yellow_olive_tone", "olive"], "color_group": "green"},
    101: {"index": 101, "names": ["clay_creek", "mostly_desaturated_dark_yellow", "shadow"], "color_group": "green"},
    102: {"index": 102, "names": ["taupe_gray"], "color_group": "gray_and_black"},
    103: {"index": 103, "names": ["cool_grey", "dark_grayish_blue", "shadow_blue"], "color_group": "blue"},
    104: {"index": 104, "names": ["chetwode_blue", "ube"], "color_group": "blue"},
    105: {"index": 105, "names": ["violets_are_blue"], "color_group": "blue"},
    106: {"index": 106, "names": ["apple_green", "limeade"], "color_group": "green"},
    107: {"index": 107, "names": ["asparagus", "chelsea_cucumber", "dark_moderate_green"], "color_group": "green"},
    108: {"index": 108, "names": ["bay_leaf", "dark_grayish_lime_green", "dark_sea_green"], "color_group": "green"},
    109: {"index": 109, "names": ["dark_grayish_cyan", "gulf_stream", "pewter_blue"], "color_group": "cyan"},
    110: {
        "index": 110,
        "names": ["light_cobalt_blue", "polo_blue", "slightly_desaturated_blue"],
        "color_group": "blue",
    },
    111: {"index": 111, "names": ["french_sky_blue", "malibu"], "color_group": "blue"},
    112: {"index": 112, "names": ["pistachio"], "color_group": "green"},
    113: {"index": 113, "names": ["mantis"], "color_group": "green"},
    114: {"index": 114, "names": ["pastel_green", "slightly_desaturated_lime_green"], "color_group": "green"},
    115: {"index": 115, "names": ["pearl_aqua", "vista_blue"], "color_group": "cyan"},
    116: {"index": 116, "names": ["bermuda", "middle_blue_green", "slightly_desaturated_cyan"], "color_group": "cyan"},
    117: {"index": 117, "names": ["pale_cyan", "very_light_blue"], "color_group": "cyan"},
    118: {"index": 118, "names": ["chartreuse", "pure_green"], "color_group": "green"},
    119: {"index": 119, "names": ["light_green", "screamin_green"], "color_group": "green"},
    120: {"index": 120, "names": ["very_light_lime_green"], "color_group": "green"},
    121: {"index": 121, "names": ["mint_green_121"], "color_group": "green"},
    122: {"index": 122, "names": ["aquamarine", "lime_green"], "color_group": "cyan"},
    123: {"index": 123, "names": ["anakiwa", "electric_blue", "very_light_cyan"], "color_group": "cyan"},
    124: {"index": 124, "names": ["bright_red", "dark_candy_apple_red", "dark_red"], "color_group": "red"},
    125: {"index": 125, "names": ["dark_pink", "jazzberry_jam"], "color_group": "red"},
    126: {"index": 126, "names": ["dark_magenta", "flirt"], "color_group": "purple_violet_and_magenta"},
    127: {"index": 127, "names": ["heliotrope_magenta"], "color_group": "purple_violet_and_magenta"},
    128: {"index": 128, "names": ["vivid_mulberry"], "color_group": "purple_violet_and_magenta"},
    129: {"index": 129, "names": ["electric_purple"], "color_group": "purple_violet_and_magenta"},
    130: {"index": 130, "names": ["dark_orange_brown_tone", "rose_of_sharon", "windsor_tan"], "color_group": "brown"},
    131: {"index": 131, "names": ["dark_moderate_red", "electric_brown", "matrix"], "color_group": "brown"},
    132: {"index": 132, "names": ["dark_moderate_pink", "tapestry", "turkish_rose"], "color_group": "red"},
    133: {
        "index": 133,
        "names": ["dark_moderate_magenta", "pearly_purple"],
        "color_group": "purple_violet_and_magenta",
    },
    134: {"index": 134, "names": ["rich_lilac"], "color_group": "purple_violet_and_magenta"},
    135: {"index": 135, "names": ["lavender_indigo", "light_violet"], "color_group": "purple_violet_and_magenta"},
    136: {"index": 136, "names": ["dark_goldenrod", "pirate_gold"], "color_group": "brown"},
    137: {"index": 137, "names": ["bronze", "dark_moderate_orange", "muesli"], "color_group": "brown"},
    138: {"index": 138, "names": ["dark_grayish_red", "english_lavender", "pharlap"], "color_group": "brown"},
    139: {
        "index": 139,
        "names": ["bouquet", "dark_grayish_magenta", "opera_mauve"],
        "color_group": "purple_violet_and_magenta",
    },
    140: {
        "index": 140,
        "names": ["lavender", "slightly_desaturated_violet"],
        "color_group": "purple_violet_and_magenta",
    },
    141: {"index": 141, "names": ["bright_lavender"], "color_group": "purple_violet_and_magenta"},
    142: {"index": 142, "names": ["buddha_gold", "light_gold"], "color_group": "brown"},
    143: {"index": 143, "names": ["dark_moderate_yellow", "olive_green"], "color_group": "green"},
    144: {"index": 144, "names": ["dark_grayish_yellow", "hillary", "sage"], "color_group": "brown"},
    145: {"index": 145, "names": ["silver_foil"], "color_group": "gray_and_black"},
    146: {"index": 146, "names": ["grayish_blue", "wild_blue_yonder", "wistful"], "color_group": "blue"},
    147: {"index": 147, "names": ["maximum_blue_purple", "melrose"], "color_group": "blue"},
    148: {"index": 148, "names": ["rio_grande", "sheen_green", "vivid_lime_green"], "color_group": "green"},
    149: {"index": 149, "names": ["conifer", "june_bud", "moderate_green"], "color_group": "green"},
    150: {"index": 150, "names": ["feijoa", "slightly_desaturated_green", "yellow_green"], "color_group": "green"},
    151: {"index": 151, "names": ["grayish_lime_green", "light_moss_green", "pixie_green"], "color_group": "green"},
    152: {"index": 152, "names": ["crystal", "grayish_cyan", "jungle_mist"], "color_group": "cyan"},
    153: {"index": 153, "names": ["fresh_air", "pale_blue"], "color_group": "blue"},
    154: {"index": 154, "names": ["lime", "spring_bud"], "color_group": "green"},
    155: {"index": 155, "names": ["green_yellow", "inchworm"], "color_group": "green"},
    156: {"index": 156, "names": ["mint_green", "very_light_green"], "color_group": "green"},
    157: {"index": 157, "names": ["menthol", "pale_lime_green"], "color_group": "green"},
    158: {"index": 158, "names": ["aero_blue", "magic_mint"], "color_group": "cyan"},
    159: {"index": 159, "names": ["celeste", "french_pass"], "color_group": "cyan"},
    160: {"index": 160, "names": ["guardsman_red", "rosso_corsa", "strong_red"], "color_group": "red"},
    161: {"index": 161, "names": ["razzmatazz", "royal_red"], "color_group": "red"},
    162: {"index": 162, "names": ["mexican_pink", "strong_pink"], "color_group": "pink"},
    163: {"index": 163, "names": ["hollywood_cerise_163"], "color_group": "pink"},
    164: {"index": 164, "names": ["deep_magenta", "strong_magenta"], "color_group": "purple_violet_and_magenta"},
    165: {"index": 165, "names": ["phlox"], "color_group": "purple_violet_and_magenta"},
    166: {"index": 166, "names": ["strong_orange", "tenn"], "color_group": "orange"},
    167: {"index": 167, "names": ["indian_red", "moderate_red", "roman"], "color_group": "red"},
    168: {"index": 168, "names": ["blush", "cranberry", "mystic_pearl"], "color_group": "red"},
    169: {"index": 169, "names": ["hopbush", "moderate_pink", "super_pink"], "color_group": "pink"},
    170: {"index": 170, "names": ["moderate_magenta", "orchid"], "color_group": "purple_violet_and_magenta"},
    171: {"index": 171, "names": ["heliotrope", "light_magenta"], "color_group": "pink"},
    172: {"index": 172, "names": ["chocolate", "harvest_gold", "mango_tango"], "color_group": "brown"},
    173: {"index": 173, "names": ["copperfield", "raw_sienna"], "color_group": "brown"},
    174: {"index": 174, "names": ["my_pink", "new_york_pink", "slightly_desaturated_red"], "color_group": "pink"},
    175: {"index": 175, "names": ["can_can", "middle_purple", "slightly_desaturated_pink"], "color_group": "pink"},
    176: {"index": 176, "names": ["deep_mauve", "light_orchid", "slightly_desaturated_magenta"], "color_group": "pink"},
    177: {"index": 177, "names": ["bright_lilac", "very_light_violet"], "color_group": "pink"},
    178: {"index": 178, "names": ["goldenrod", "mustard_yellow"], "color_group": "brown"},
    179: {"index": 179, "names": ["earth_yellow", "moderate_orange"], "color_group": "brown"},
    180: {"index": 180, "names": ["slightly_desaturated_orange", "tan"], "color_group": "brown"},
    181: {"index": 181, "names": ["clam_shell", "grayish_red", "pale_chestnut"], "color_group": "brown"},
    182: {"index": 182, "names": ["grayish_magenta", "pink_lavender", "thistle"], "color_group": "pink"},
    183: {"index": 183, "names": ["mauve", "pale_violet"], "color_group": "purple_violet_and_magenta"},
    184: {"index": 184, "names": ["citrine", "corn", "strong_yellow"], "color_group": "yellow"},
    185: {"index": 185, "names": ["chinese_green", "moderate_yellow", "tacha"], "color_group": "yellow"},
    186: {"index": 186, "names": ["deco", "medium_spring_bud", "slightly_desaturated_yellow"], "color_group": "yellow"},
    187: {"index": 187, "names": ["grayish_yellow", "green_mist", "pastel_gray"], "color_group": "green"},
    188: {"index": 188, "names": ["light_silver"], "color_group": "gray_and_black"},
    189: {"index": 189, "names": ["fog", "pale_lavender", "very_pale_blue"], "color_group": "blue"},
    190: {"index": 190, "names": ["chartreuse_yellow", "pure_yellow"], "color_group": "yellow"},
    191: {"index": 191, "names": ["canary", "maximum_green_yellow"], "color_group": "yellow"},
    192: {"index": 192, "names": ["honeysuckle", "mindaro"], "color_group": "yellow"},
    193: {"index": 193, "names": ["pale_green", "reef", "tea_green"], "color_group": "green"},
    194: {"index": 194, "names": ["beige", "nyanza", "snowy_mint", "very_pale_lime_green"], "color_group": "green"},
    195: {"index": 195, "names": ["light_cyan", "oyster_bay", "very_pale_cyan"], "color_group": "green"},
    196: {"index": 196, "names": ["light_red", "red"], "color_group": "red"},
    197: {"index": 197, "names": ["vivid_raspberry", "winter_sky"], "color_group": "red"},
    198: {"index": 198, "names": ["bright_pink", "rose"], "color_group": "pink"},
    199: {"index": 199, "names": ["fashion_fuchsia", "hollywood_cerise", "pure_pink"], "color_group": "pink"},
    200: {"index": 200, "names": ["pure_magenta"], "color_group": "pink"},
    201: {"index": 201, "names": ["fuchsia", "light_magenta_013", "magenta"], "color_group": "pink"},
    202: {"index": 202, "names": ["blaze_orange", "orange_red", "vivid_orange"], "color_group": "orange"},
    203: {"index": 203, "names": ["bittersweet", "pastel_red"], "color_group": "red"},
    204: {"index": 204, "names": ["strawberry", "wild_watermelon"], "color_group": "red"},
    205: {"index": 205, "names": ["hot_pink", "light_pink"], "color_group": "pink"},
    206: {"index": 206, "names": ["light_deep_pink", "purple_pizzazz"], "color_group": "pink"},
    207: {"index": 207, "names": ["pink_flamingo", "shocking_pink"], "color_group": "pink"},
    208: {"index": 208, "names": ["american_orange", "dark_orange", "flush_orange"], "color_group": "orange"},
    209: {"index": 209, "names": ["coral", "salmon"], "color_group": "orange"},
    210: {"index": 210, "names": ["tulip", "very_light_red", "vivid_tangerine"], "color_group": "red"},
    211: {"index": 211, "names": ["pink_salmon", "tickle_me_pink"], "color_group": "pink"},
    212: {"index": 212, "names": ["lavender_rose", "princess_perfume", "very_light_pink"], "color_group": "pink"},
    213: {"index": 213, "names": ["blush_pink", "fuchsia_pink", "very_light_magenta"], "color_group": "pink"},
    214: {"index": 214, "names": ["chinese_yellow", "orange", "pure_orange", "yellow_sea"], "color_group": "orange"},
    215: {"index": 215, "names": ["light_orange", "rajah", "texas_rose"], "color_group": "orange"},
    216: {"index": 216, "names": ["hit_pink", "macaroni_and_cheese", "very_light_orange"], "color_group": "orange"},
    217: {"index": 217, "names": ["melon", "pale_red_pink_tone", "sundown"], "color_group": "orange"},
    218: {"index": 218, "names": ["cotton_candy", "lavender_pink", "pale_pink"], "color_group": "pink"},
    219: {"index": 219, "names": ["pale_magenta", "rich_brilliant_lavender", "shampoo"], "color_group": "pink"},
    220: {"index": 220, "names": ["gold"], "color_group": "yellow"},
    221: {"index": 221, "names": ["dandelion", "naples_yellow"], "color_group": "yellow"},
    222: {"index": 222, "names": ["grandis", "jasmine", "khaki"], "color_group": "brown"},
    223: {"index": 223, "names": ["caramel", "moccasin", "pale_orange"], "color_group": "brown"},
    224: {"index": 224, "names": ["cosmos", "misty_rose", "very_pale_red_pink_tone"], "color_group": "pink"},
    225: {"index": 225, "names": ["bubble_gum", "pink_lace", "very_pale_magenta"], "color_group": "pink"},
    226: {"index": 226, "names": ["light_yellow_011", "yellow"], "color_group": "yellow"},
    227: {"index": 227, "names": ["laser_lemon", "light_yellow"], "color_group": "yellow"},
    228: {"index": 228, "names": ["dolly", "pastel_yellow", "very_light_yellow"], "color_group": "yellow"},
    229: {"index": 229, "names": ["calamansi", "pale_yellow", "portafino"], "color_group": "yellow"},
    230: {"index": 230, "names": ["cream", "cumulus", "very_pale_yellow"], "color_group": "white"},
    231: {"index": 231, "names": ["light_white", "white"], "color_group": "white"},
    232: {"index": 232, "names": ["vampire_black"], "color_group": "gray_and_black"},
    233: {"index": 233, "names": ["chinese_black", "cod_gray"], "color_group": "gray_and_black"},
    234: {"index": 234, "names": ["eerie_black"], "color_group": "gray_and_black"},
    235: {"index": 235, "names": ["raisin_black"], "color_group": "gray_and_black"},
    236: {"index": 236, "names": ["dark_charcoal"], "color_group": "gray_and_black"},
    237: {"index": 237, "names": ["black_olive", "mine_shaft"], "color_group": "gray_and_black"},
    238: {"index": 238, "names": ["outer_space"], "color_group": "gray_and_black"},
    239: {"index": 239, "names": ["dark_liver", "tundora"], "color_group": "gray_and_black"},
    240: {"index": 240, "names": ["davys_grey"], "color_group": "gray_and_black"},
    241: {"index": 241, "names": ["granite_gray", "very_dark_gray"], "color_group": "gray_and_black"},
    242: {"index": 242, "names": ["dim_gray", "dove_gray"], "color_group": "gray_and_black"},
    243: {"index": 243, "names": ["boulder", "sonic_silver"], "color_group": "gray_and_black"},
    244: {"index": 244, "names": ["gray", "light_black"], "color_group": "gray_and_black"},
    245: {"index": 245, "names": ["philippine_gray"], "color_group": "gray_and_black"},
    246: {"index": 246, "names": ["dusty_gray"], "color_group": "gray_and_black"},
    247: {"index": 247, "names": ["spanish_gray"], "color_group": "gray_and_black"},
    248: {"index": 248, "names": ["dark_gray", "quick_silver"], "color_group": "gray_and_black"},
    249: {"index": 249, "names": ["philippine_silver", "silver_chalice"], "color_group": "gray_and_black"},
    250: {"index": 250, "names": ["silver"], "color_group": "gray_and_black"},
    251: {"index": 251, "names": ["silver_sand"], "color_group": "gray_and_black"},
    252: {"index": 252, "names": ["american_silver", "light_gray"], "color_group": "gray_and_black"},
    253: {"index": 253, "names": ["alto", "gainsboro"], "color_group": "gray_and_black"},
    254: {"index": 254, "names": ["mercury", "platinum"], "color_group": "gray_and_black"},
    255: {"index": 255, "names": ["bright_gray", "gallery", "very_light_gray"], "color_group": "gray_and_black"},
}


def print_color_codes():
    # TODO Show all colorcodes  in a 36 columns x 6 lines table in the output
    # as three number digit color_code ranging from 16 to 231 in the form
    # "{ESC}[38;5;{color_code}{str(color_code).zfill(3)}"
    # Show left half and right half in two separate tables
    ESC = "\033"
    columns = 18  # half the columns
    start, end = 16, 231

    # First print LEFT half
    print("COLOR CODES")
    for row in range(6):
        line = ""
        for col in range(columns):
            code = start + row * (columns * 2) + col
            if code > end:
                break
            line += f"{ESC}[38;5;{code}m{str(code).zfill(3)}{ESC}[0m "
        print(line)

    # Then print RIGHT half
    for row in range(6):
        line = ""
        for col in range(columns, columns * 2):  # second half of the row
            code = start + row * (columns * 2) + col
            if code > end:
                break
            line += f"{ESC}[38;5;{code}m{str(code).zfill(3)}{ESC}[0m "
        print(line)


def print_color_groups(ansi_dict):
    # Extract color groups using a set to remove duplicates
    color_groups = {entry["color_group"] for entry in ansi_dict.values()}

    # Convert to a sorted list
    sorted_groups = sorted(color_groups)

    # Print the groups
    print(sorted_groups)
    return sorted_groups


def print_colors_by_groups(ansi_dict, groups=COLOR_GROUPS):
    for group in groups:
        print(f"\n{ESC_CODE_TITLE}##### {group.upper()}{ESC_CODE_RESET}")  # Print group header

        for idx, entry in ansi_dict.items():
            if entry["color_group"] == group:
                esc_code_color = f"\033[38;5;{entry['index']}m"  # True ANSI index coloring
                names = ", ".join(entry["names"])
                print(f"{esc_code_color}[{entry['index']:03d}] {names}{ESC_CODE_WHITE}")


if __name__ == "__main__":
    print_colors_by_groups(ANSI_COLOR)
    print()
    print_color_codes()
