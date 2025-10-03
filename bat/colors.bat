@echo off

rem colors.bat set color codes

rem colors.bat: Sets specific color codes as ENV C... check using C_set C_, also see colors.py
rem https://en.wikipedia.org/wiki/ANSI_escape_code
rem https://ss64.com/nt/syntax-ansi.html
rem https://stackoverflow.com/questions/2048509/how-to-echo-with-different-colors-in-the-windows-command-line 
rem https://gist.github.com/mlocati/fdabcaeb8071d5c75a2d51712db24011#file-win10colors-cmd
rem define a newline variable spaces need to be kept
rem https://stackoverflow.com/questions/132799/how-can-i-echo-a-newline-in-a-batch-file
rem https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
rem 38;5;f is font color and 48;5;b background color with numbers from 16...231

set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1

rem create an ESQ Sequence
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
rem selected color palette 38 is foreground, 48 is background, use py_color_list.bat to display the python

set COL_TEST=%ESC%[38;2;229,229;229m
set COL_GREEN_DARK=%ESC%[38;5;34m 
rem set COL_GREEN=%ESC%[38;5;40m
set COL_GREEN_LIGHT=%ESC%[38;5;46m
set COL_ORANGE_DARK=%ESC%[38;5;202m
set COL_ORANGE=%ESC%[38;5;208m
set COL_ORANGE_LIGHT=%ESC%[38;5;214m
rem set COL_YELLOW=%ESC%[38;5;220m
set COL_YELLOW_LIGHT=%ESC%[38;5;226m
set COL PINK_DARK=%ESC%[38;5;200m
set COL_PINK=%ESC%[38;5;206m
set COL_PINK_LIGHT=%ESC%[38;5;212m
set COL_BLUE_DARK=%ESC%[38;5;33m
rem set COL_BLUE=%ESC%[38;5;39m
set COL_BLUE_LIGHT=%ESC%[38;5;45m
set COL_BLUE_SKY=%ESC%[38;5;75m
rem set COL_PURPLE=%ESC%[38;5;99m
set COL_PURPLE_LIGHT=%ESC%[38;5;105m
set COL_GREY_DARK=%ESC%[38:5:242m
rem set COL_GREY=%ESC%[38;5;246m
set COL_GREY_LIGHT=%ESC%[38;5;249m
rem set COL_WHITE=%ESC% [38;5;255m
rem set COL_BLACK=%ESC% [38;5;232m
set COL_DEFAULT=%ESC%[0m
set COL_RED=%ESC%[1;31;40m
set COL_GREEN=%ESC%[1;32;40m
set COL_YELLOW=%ESC%[1;33;40m
set COL_BLUE=%ESC%[1;34;40m
set COL_PURPLE=%ESC%[1;35;40m
set COL_LIGHTBLUE=%ESC%[1;36;40m
set COL_WHITE=%ESC%[1;37;40m
set COL_DEFAULT_BG=%ESC%[1;37;47m
set COL_RED_BG=%ESC%[1;31;41m
set COL_GREEN_BG=%ESC%[1;37;42m
set COL_YELLOW_BG=%ESC%[1;37;43m
set COL_BLUE_BG=%ESC%[1;37;44m
set COL_PURPLE_BG=%ESC%[1;37;45m
set COL_LIGHTBLUE_BG=%ESC%[1;37;46m
set COL_WHITE_BG=%ESC%[1;37;47m
set COL_GREY_WH=%ESC%[1;30;47m
set COL_RED_WH=%ESC%[1;31;47m
set COL_GREEN_WH=%ESC%[1;32;47m
set COL_YELLOW_WH=%ESC%[1;33;47m
set COL_BLUE_WH=%ESC%[1;34;47m
set COL_PURPLE_WH=%ESC%[1;35;47m
set COL_LIGHTBLUE_WH=%ESC%[1;36;47m
set COL_BLACK_WH=%ESC%[1;30;47m

rem special colors 
set COL_RED_BRIGHT_196=%ESC%[38;5;196m
set COL_RED_STRAWBERRY_204=%ESC%[38;5;204m
set COL_ORANGE_RED_202=%ESC%[38;5;202m
set COL_ORANGE_214=%ESC%[38;5;214m
set COL_ORANGE_LIGHT_215=%ESC%[38;5;215m
set COL_YELLOWGREEN_191=%ESC%[38;5;191m
set COL_YELLOW_PALE_229=%ESC%[38;5;229m
set COL_GREEN_MINT_121=%ESC%[38;5;121m
set COL_GREEN_PALE_193=%ESC%[38;5;193m
set COL_GREEN_LIME_154=%ESC%[38;5;154m
set COL_GREEN_AQUA_85=%ESC%[38;5;85m
set COL_GREEN_PALE_194=%ESC%[38;5;194m

set COL_GREEN_DARKCYAN_23=%ESC%[38;5;23m
set COL_CYAN_PURE_50=%ESC%[38;5;50m
set COL_CYAN_PALE_195=%ESC%[38;5;195m
set COL_CYAN_AQUAMARING_87=%ESC%[38;5;87m
set COL_CYAN_GRAYISH_109=%ESC%[38;5;109m
set COL_CYAN_LIGHT_51=%ESC%[38;5;51m
set COL_CYAN_AQUA_14=%ESC%[38;5;14m
set COL_BLUE_SKYBLUE_45=%ESC%[38;5;45m
set COL_BLUE_MEDIUM_20=%ESC%[38;5;20m
set COL_BLUE_DEEPSKY_39=%ESC%[38;5;39m
set COL_BLUE_PALE_153=%ESC%[38;5;153m
set COL_BLUE_LIGHTCOBALT_110=%ESC%[38;5;110m
set COL_PURPLE_MAGENTA_164=%ESC%[38;5;164m
set COL_PURPLE_MAGENTALIGHT_170=%ESC%[38;5;170m
set COL_PURPLE_LAVENDER_141=%ESC%[38;5;141m
set COL_PURPLE_PALEVIOLET_183=%ESC%[38;5;183m
set COL_PINK_BRIGHT_198=%ESC%[38;5;198m
set COL_PINK_LILAC_177=%ESC%[38;5;177m
set COL_PINK_CANDY_218=%ESC%[38;5;218m
set COL_WHITE_CREAM_230=%ESC%[38;5;230m
set COL_WHITE_LIGHT_15=%ESC%[38;5;15m
set COL_BROWN_94=%ESC%[38;5;94m
set COL_BROWN_KHAKI_222=%ESC%[38;5;222m
set COL_BROWN_COPPER_173=%ESC%[38;5;173m
set COL_GRAY_246=%ESC%[38;5;246m


rem bright colors are 90-97 / std colors are 30-37
set C_0=%ESC%[0m
set C_GRY=%ESC%[90m
set C_RED=%ESC%[91m
set C_GRN=%ESC%[92m
set C_YLL=%ESC%[93m
set C_BLU=%ESC%[94m
set C_MAG=%ESC%[95m
set C_CYN=%ESC%[96m
set C_WHT=%ESC%[97m
rem specific colors for branch path venv
rem prompt branch color
set C_B=%COL_ORANGE_LIGHT_215%
rem prompt path color
set C_P=%COL_GREEN_AQUA_85%
rem prompt venv color
set C_V=%COL_BLUE_DARK%
rem prompt symbol color
set C_SC0=%COL_PURPLE_LIGHT%
set C_SC1=%COL_PURPLE_MAGENTA_164%
rem set output color
set C_O=%COL_BLUE_LIGHT%
rem different text colors when activated
set C_0=%COL_CYAN_PALE_195%
set C_1=%COL_BLUE_PALE_153%
rem set colors for certain echos
rem title
set C_T=%COL_BLUE_SKY%
rem search keys
set C_S=%COL_ORANGE%
rem file keys
set C_F=%COL_BLUE_SKY%
rem python output
set C_PY=%COL_GREEN%
rem question / prompt
set C_Q=%C_MAG%
rem program 
set C_PROG=%COL_PINK%
rem ERROR
set C_E=%COL_RED%

rem show output if called with any dummy input
if %NUM_ARGS% gtr 0 echo %COL_GREY_DARK%### RUN %~f0%C_0%