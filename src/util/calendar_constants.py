"""Calendar and Time Utils"""

import re

WORKDAYS = ["onduty", "workday", "workday_home"]

# # Patterns for Date Identification
# # regex match any 8 Digit Groups preceded by space or start of line
# # and not followed by a dash
REGEX_YYYYMMDD = re.compile(r"((?<=\s)|(?<=^))(\d{8})(?!-)")
REGEX_DATE_RANGE = re.compile(r"\d{8}-\d{8}")
# # any combination of Upper/Lowercase String  in German
REGEX_WEEKDAY = re.compile(r"[MDFS][oira]")
# # REGEX TO Extract a TODO.TXT substring
REGEX_TODO_TXT = r"@[Tt]\((.+)?\)"
REGEX_TODO_TXT_REPLACE = r"@[Tt]\(.+?\)"
# # REGEX for TAGS / excluding the TODOO TXT tag
REGEX_TAGS = r"@([^Tt][a-zA-Z0-9_]+)"
REGEX_TAGS_REPLACE = r"@[^Tt][a-zA-Z0-9_]+"

# REGEX FOR TOTAL WORK
REGEX_TOTAL_WORK = r"@TOTALWORK([0-9,.]+)"
REGEX_TOTAL_WORK_REPLACE = r"@TOTALWORK[0-9,.]+"

# WEEK INDICES FOR LAST CALENDAR WEEK OF PREVIOUS YEAR AND
# FOLLOWING YEAR
WEEK_INDEX_PREVIOUS_YEAR = 0
WEEK_INDEX_NEXT_YEAR = 99

# Mode to Determine Calendar Week Indices
CW_DROP = "cw_drop"  # drop 1st calendar week if in previous year
CW_TRUNC = "cw_trunc"  # truncate to January 1
