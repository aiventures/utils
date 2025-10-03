"""browser_bookmarks creates a markdown version of exported bookmarks favoriten favorites from browser.

v4 top (=latest)

for empty cells keep the month but take into that the cell height is
supposed to be the same as the cells that also have a link count

below the year, in an additional line in the cell,
add the total number of links that were created for this year

for the first column in the toc containing the year,
add the anchor link pointing to the year in the markdown. Make the year bold markdown

instead of the format yyyy-mm use only month mm

for toc_vertical_heatmap, make the icon ciolor dependent from its relative value.
If its below 50% percentile, draw it 🟩, if its below 80% draw it 🟨, 🟥 for the upper value

almost there: Adjust the bars so that the have a fixed height

can you also rearrange the table of contents as following:
- arrange the TOC as a markdown table
- each line represents a year (yyyy). the first column will contain the year
- each column in line represents a month (yyyy-mm)
- in each cell draw the emojis for the stat counter as stacked bar. On the botton of the cell, draw the anchor as yyyy-mm text with a link to the section in the markdown file

change the sidebar link generation so that the
link counter reflects the number always be a three digit number

format the number of entries in the tox to a fixed of 3 drigits

also make the toc in fixed font

change the toc_heatmap so that it shows the icons relative
to the maximum number of links in a month

how to use generate_toc_with_heatmap in create_markdown

also add a heatmap of number of occurences as icons to the toc

how do i use build_sidebar_anchors in the create_markdown function?

create the sidebar_anchor list for the following sections : TOC,
Domain Table and for each year occuring in the link list.

also create HTML floating sidebar with the table of contents

also add a link in the domain statistics section back to the toc section.
In the top section provide a link to the domain statistics section as first entry
add generation of these two links into code

in the domain statistics list, can you also add the top level domain urls as link into the first coilumn

sort the domain list in alphabetical order. for the domain table, only consider
links that were created within the last 365 days. use color coded emojis to display frequency as text only heatmap.
add additional logig to existing code to create heatmap

add the total number of entries as an additional comment in the section

also generate a domain frequency chart in markdown as simple markdown table

for each inks, also add as postfix in parentheses the root domain name of each
link, without the http://www..  So, for a link like http://www.example.com/mysubpage,
as postfix add a (example.com) to the link line

at the end of each ## section privde an anchor link headiung back to top of
document respectively to the # Table Of Contents section on top

these links do not conform to md format for anchors or links within documents.
any special characters such as [ or ] need to be dropped to generate valid anchor links

the anchor links do not work because they don't reflect the
postfix that will display the number of entries for each level

add a table of contents with YYYY as fist level and YYYY-mm as second level.
Also add the total number of links for each level and also supply anchors so that
you can navigate to the respective location by clicking on the link in the table of contents

also add the totals for the YYYY-MM and YYYY levels as well

for the date header lines add in parentheses [ ]
the number of children links contained below each header line

skip the top 2 tree levels in the display as they do not provide any value add

no that was wrong. update as postfix all parent elements of the html link
that represent the folders in the bookmarks (corresponding to the H3
HTMl tags in the original exported html file )

Got it, You want each Markdown link to include a postfix that
# reflects its full folder path—derived from the hierarchy of
#  <H3> tags in the original HTML. That means:

For each <A> (link), we trace its parent <DL> blocks upward.
For each parent <H3> encountered, we collect its text.
The final postfix is a breadcrumb-style path like: → Folder1 / SubfolderA / SubfolderB

v3

Sort the markdown in descending order of date.
Also add the the Order Path as postfix to each link

v2
Specification

<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file. -->
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1633036800">Favorites Bar</H3>
    <DL><p>
        <DT><A HREF="https://example.com" ADD_DATE="1633036801">Example Site</A>
    </DL><p>
</DL><p>

Prompt
Optimize the following python program to export the information in that bookmarks file in markdown format.
Consider the following
The Markdown file exports in the following format
1st Level # is the corresponding year (yyyy)
2nd level ## is corresponding year-month (yyyy-mm)
3rd level ### is year-month-day (yyyy-mm-dd)
Under 3rd level display each link in as list item in the form
* [yyyy-mm-dd linktext](url) with linktext
the extracted text from the link, url as the extracted url
from the the href attribute and yyyy-mm-dd as transformed date derived from the ADD_DATE timestamp attribute of that link.

v1
original handcrafted version

"""

import os
import re
import sys
import traceback
import json
from collections import Counter
from datetime import datetime as DateTime
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime, timedelta

# get read/write path from env
from config.myenv import MY_P_DESKTOP


def generate_floating_sidebar(anchors):
    """Returns HTML+CSS for a right-aligned floating TOC sidebar"""
    sidebar = [
        "<style>",
        "#toc-sidebar {",
        "  position: fixed;",
        "  top: 80px;",
        "  right: 20px;",
        "  width: 220px;",
        "  background: #2e2e2e;",  # Dark gray
        "  border: 1px solid #444;",
        "  padding: 12px;",
        "  font-family: sans-serif;",
        "  font-size: 14px;",
        "  line-height: 1.6;",
        "  box-shadow: 2px 2px 6px rgba(0,0,0,0.2);",
        "  z-index: 999;",
        "  color: #f0f0f0;",
        "}",
        "#toc-sidebar h2 {",
        "  margin-top: 0;",
        "  font-size: 16px;",
        "  color: #ffffff;",
        "}",
        "#toc-sidebar a {",
        "  display: block;",
        "  color: #80c0ff;",
        "  text-decoration: none;",
        "  margin-bottom: 6px;",
        "}",
        "#toc-sidebar a:hover {",
        "  text-decoration: underline;",
        "}",
        "</style>",
        "",
        "<div id='toc-sidebar'>",
        "  <h2>▶️⏩ Navigation</h2>",
    ]
    for label, anchor in anchors:
        sidebar.append(f"  <a href='#{anchor}'>{label}</a>")
    sidebar.append("</div>")
    return sidebar


def save(filepath, data):
    """Saves string data or stringified dict"""
    if isinstance(data, dict):
        data = json.dumps(data, indent=4, ensure_ascii=False)
    elif isinstance(data, list):
        data = "\n".join(data)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception:
        print(f"Error writing to {filepath}")
        print(traceback.format_exc())


def get_soup_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "lxml")
    except Exception:
        print(traceback.format_exc())


def get_root_domain(url):
    """Extracts root domain from URL, stripping http://, https://, www."""
    try:
        netloc = urlparse(url).netloc
        domain = netloc.lower().replace("www.", "")
        return domain
    except:
        return ""


def extract_links_by_date(soup):
    """Returns nested dict: {year: {month: {day: [ (text, url, date_str, folder_path) ]}}}"""
    links_by_date = {}

    for a_tag in soup.find_all("a"):
        href = a_tag.get("href")
        text = a_tag.text.strip()
        ts = a_tag.get("add_date")

        if not href or not ts:
            continue

        dt = DateTime.utcfromtimestamp(int(ts))
        y, m, d = dt.strftime("%Y"), dt.strftime("%Y-%m"), dt.strftime("%Y-%m-%d")

        # Traverse parents to collect folder names
        folder_names = []
        for parent in a_tag.parents:
            if parent.name == "dl":
                h3 = parent.find_previous("h3")
                if h3 and h3.text.strip():
                    folder_names.insert(0, h3.text.strip())

        # Skip top 2 levels
        trimmed_path = folder_names[2:] if len(folder_names) > 2 else []
        folder_path = " / ".join(trimmed_path)

        links_by_date.setdefault(y, {}).setdefault(m, {}).setdefault(d, []).append(
            (text, href, dt.strftime("%Y-%m-%d"), folder_path)
        )

    return links_by_date


def generate_anchor(header_text):
    """Sanitize header text to match GitHub-flavored Markdown anchor format"""
    anchor = header_text.lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)  # remove all except alphanumerics, spaces, hyphens
    anchor = anchor.strip().replace(" ", "-")
    return anchor


def format_count(n):
    return f"{n:03d}"  # Pads to 3 digits


def build_sidebar_anchors(links_by_date, year_counts):
    """Returns list of (label, anchor) tuples for sidebar"""
    anchors = []

    # TOC and Domain Table
    anchors.append(("Table of Contents", "table-of-contents"))
    anchors.append(("Domain Statistics", "domain-statistics"))

    # Each year header with padded count
    for year in sorted(year_counts.keys(), reverse=True):
        padded = format_count(year_counts[year])
        label = f"{year} [{padded}]"
        anchor = generate_anchor(label)
        anchors.append((label, anchor))

    return anchors


def emoji_heatmap(count):
    """Returns emoji heatmap based on frequency tiers"""
    if count >= 10:
        return "🟥🟥🟥🟥🟥"
    elif count >= 5:
        return "🟧🟧🟧🟧"
    elif count >= 2:
        return "🟨🟨"
    else:
        return "🟩"


def toc_heatmap_abs(count):
    """tox heatmap based on absolute stats."""
    if count >= 50:
        return "🟥🟥🟥🟥🟥"
    elif count >= 30:
        return "🟧🟧🟧🟧"
    elif count >= 15:
        return "🟨🟨🟨"
    elif count >= 5:
        return "🟩🟩"
    else:
        return "🟩"


def toc_vertical_heatmap(count, max_count, height=5):
    """Returns fixed-height stacked emoji bar with adaptive color"""
    if max_count == 0:
        return "<br>".join([" "] * height)
    ratio = count / max_count
    if ratio < 0.5:
        icon = "🟩"
    elif ratio < 0.8:
        icon = "🟨"
    else:
        icon = "🟥"
    blocks = int(ratio * height)
    return "<br>".join([" "] * (height - blocks) + [icon] * blocks)


def toc_heatmap(count, max_count, width=5, emoji="🟦"):
    """Returns emoji heatmap scaled to max monthly count"""
    if max_count == 0:
        return ""
    blocks = int((count / max_count) * width)
    return emoji * blocks + " " * (width - blocks)


def format_domain_table_recent(entries):
    """Returns Markdown table of domain frequencies for links in last 365 days, with emoji heatmap"""
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    domain_counter = Counter()

    for dt, _, _, _, _, url, _ in entries:
        if dt >= one_year_ago:
            domain = get_root_domain(url)
            domain_counter[domain] += 1

    total_recent_links = sum(domain_counter.values())

    lines = [
        "# Domain Statistics",
        "",
        f"<!-- Total recent entries: {total_recent_links} -->",
        f"_Total entries in the last 365 days: **{total_recent_links}**_",
        "",
        "| Domain           | Count | Heatmap |",
        "|------------------|-------|---------|",
    ]

    for domain, count in sorted(domain_counter.items(), key=lambda x: x[0].lower()):
        heatmap = emoji_heatmap(count)
        url = f"https://{domain}"
        link = f"[{domain}]({url})"
        lines.append(f"| {link:<16} | {count:<5} | {heatmap} |")

    lines.append("")
    lines.append("[Back to Table of Contents](#table-of-contents)")

    return lines


def generate_toc_with_heatmap(year_counts, month_counts):
    toc_lines = ["# Table of Contents", "* [Domain Statistics](#domain-statistics) 🔍"]
    for year in sorted(year_counts.keys(), reverse=True):
        label = f"{year} [{year_counts[year]}]"
        anchor = generate_anchor(label)
        heat = toc_heatmap_abs(year_counts[year])
        toc_lines.append(f"* [{label}](#{anchor}) {heat}")

        for month in sorted([m for m in month_counts if m.startswith(year)], reverse=True):
            month_label = f"{month} [{month_counts[month]}]"
            month_anchor = generate_anchor(month_label)
            heat = toc_heatmap_abs(month_counts[month])
            toc_lines.append(f"  * [{month_label}](#{month_anchor}) {heat}")
    return toc_lines


def generate_toc_with_scaled_heatmap(year_counts, month_counts):
    max_month_count = max(month_counts.values()) if month_counts else 0
    toc_lines = [
        "# Table of Contents",
        "* [Domain Statistics](#domain-statistics) 🔍",
    ]
    for year in sorted(year_counts.keys(), reverse=True):
        label = f"{year} [{format_count(year_counts[year])}]"
        anchor = generate_anchor(label)
        heat = toc_heatmap(year_counts[year], max_month_count, emoji="🟨")
        toc_lines.append(f"* [{label}](#{anchor}) {heat}")

        for month in sorted([m for m in month_counts if m.startswith(year)], reverse=True):
            label = f"{month} [{format_count(month_counts[month])}]"
            anchor = generate_anchor(label)
            heat = toc_heatmap(month_counts[month], max_month_count, emoji="🟦")
            toc_lines.append(f"  * [{label}](#{anchor}) {heat}")
    return toc_lines


def generate_toc_table_vertical_heatmap(year_counts, month_counts):
    from collections import defaultdict

    # Organize months by year
    months_by_year = defaultdict(list)
    for key in month_counts:
        year, month = key.split("-")
        months_by_year[year].append(f"{year}-{month}")

    # Determine all months used
    all_months_by_year = sorted(set(m.split("-")[1] for m in month_counts))

    # Header row
    header = ["| Year "] + [f"| {m}" for m in all_months_by_year] + ["|"]
    divider = ["|------"] + ["|------" for _ in all_months_by_year] + ["|"]

    # Max count for scaling
    max_count = max(month_counts.values()) if month_counts else 0

    # Rows per year
    rows = []
    for year in sorted(months_by_year.keys(), reverse=True):
        # row = [f"| {year} "]

        year_total = year_counts[year]
        padded_year_count = str(year_total).zfill(4)
        year_label = f"{year} [{padded_year_count}]"
        year_anchor = generate_anchor(year_label)
        year_cell = f"| [**{year}**](#{year_anchor})<br>{padded_year_count} "
        row = [year_cell]

        for month in all_months_by_year:
            key = f"{year}-{month}"
            if key in month_counts:
                count = month_counts[key]
                padded = format_count(count)
                label = f"{key} [{padded}]"
                anchor = generate_anchor(label)
                heat = toc_vertical_heatmap(count, max_count)
                # link = f"[{key}](#{anchor})"
                link = f"[{str(month).zfill(2)}](#{anchor})"  # display only month
                cell = f"{heat}<br>{str(padded).zfill(3)}<br>{link}"
            else:
                cell = (
                    '<div style="background-color:##1f1f1f;text-align:center;">'
                    + "<br>".join(["&nbsp;"] * 6)
                    + f"<br><span style='color:#aaa;'>{month}</span>"
                    + "</div>"
                )
                # cell = "—"
            row.append(f"| {cell} ")
        row.append("|")
        rows.append("".join(row))

    created_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    created_line = f"Generated on: **{created_timestamp}**_"
    return ["# Table of Contents", "", created_line, ""] + ["".join(header), "".join(divider)] + rows


def create_markdown(links_by_date):
    """Creates markdown with folder path postfix and link counts at all header levels"""
    all_entries = []
    year_counts = defaultdict(int)
    month_counts = defaultdict(int)
    day_counts = defaultdict(int)

    # Flatten and count
    for year, months in links_by_date.items():
        for month, days in months.items():
            for day, links in days.items():
                for text, url, date_str, folder_path in links:
                    dt = DateTime.strptime(date_str, "%Y-%m-%d")
                    all_entries.append((dt, year, month, day, text, url, folder_path))
                    year_counts[year] += 1
                    month_counts[month] += 1
                    day_counts[day] += 1

    all_entries.sort(reverse=True, key=lambda x: x[0])

    # 🧭 Build TOC

    toc_lines = ["# Table of Contents", "* [Domain Statistics](#domain-statistics)"]

    for year in sorted(year_counts.keys(), reverse=True):
        year_header = f"{year} [{year_counts[year]}]"
        year_anchor = generate_anchor(year_header)
        toc_lines.append(f"* [{year_header}](#{year_anchor})")

        for month in sorted([m for m in month_counts if m.startswith(year)], reverse=True):
            month_header = f"{month} [{month_counts[month]}]"
            month_anchor = generate_anchor(month_header)
            toc_lines.append(f"  * [{month_header}](#{month_anchor})")

    # toc_lines = ["# Table of Contents"]
    toc_years = sorted(year_counts.keys(), reverse=True)

    for year in toc_years:
        year_anchor = f"{year}"
        toc_lines.append(f"* [{year} ({year_counts[year]})](#{year_anchor})")

        months = sorted([m for m in month_counts if m.startswith(year)], reverse=True)
        for month in months:
            month_anchor = f"{month}"
            toc_lines.append(f"  * [{month} ({month_counts[month]})](#{month_anchor})")

    md_lines = []
    current_year, current_month, current_day = None, None, None
    day_links = []

    domain_counter = Counter()

    # for i, (dt, year, month, day, text, url, folder_path) in enumerate(
    #     all_entries + [(None, None, None, None, None, None, None)]
    # ):
    for dt, year, month, day, text, url, folder_path in all_entries:
        domain = get_root_domain(url)
        domain_counter[domain] += 1
        if day != current_day and current_day is not None:
            # md_lines.append(f"### {day} [{len(day_links)}]")
            md_lines.append(f"### {current_day} [{str(len(day_links)).zfill(3)}]")
            md_lines.extend(day_links)
            day_links = []

        if year != current_year and year is not None:
            # md_lines.append(f"# {year} [{year_counts[year]}]")
            md_lines.append(f"# {year} [{str(year_counts[year]).zfill(3)}]")
            current_year = year
            current_month, current_day = None, None

        if month != current_month and month is not None:
            # md_lines.append(f"## {month} [{month_counts[month]}]")
            md_lines.append(f"## {month} [{str(month_counts[month]).zfill(3)}]")
            current_month = month
            current_day = None
            md_lines.append("[Back to Top](#table-of-contents)\n")

        if day is not None:
            postfix = f"→ {folder_path}" if folder_path else ""
            domain_tag = f"({domain})" if domain else ""
            link_line = f"* [{day} {text}]({url}) {postfix} {domain_tag}"
            day_links.append(link_line)
            current_day = day

    domain_stats_md = format_domain_table_recent(all_entries)
    sidebar_anchors = build_sidebar_anchors(links_by_date, year_counts)
    sidebar_html = generate_floating_sidebar(sidebar_anchors)

    # toc_lines_stat = generate_toc_with_heatmap(year_counts, month_counts)
    # toc_lines_stat = generate_toc_with_scaled_heatmap(year_counts, month_counts)
    toc_lines_stat = generate_toc_table_vertical_heatmap(year_counts, month_counts)

    return sidebar_html + [""] + toc_lines_stat + [""] + format_domain_table_recent(all_entries) + [""] + md_lines
    # return toc_lines + [""] + domain_stats_md + [""] + md_lines


def run(bookmark_file):
    p = Path(bookmark_file)
    if not p.is_file():
        print(f"{bookmark_file} is not a valid file.")
        sys.exit()

    soup = get_soup_from_file(bookmark_file)
    links_by_date = extract_links_by_date(soup)
    md_lines = create_markdown(links_by_date)

    timestamp = DateTime.now().strftime("%Y%m%d_%H%M%S")
    base_name = p.stem
    md_path = p.parent / f"{timestamp}_{base_name}.md"
    md_path_0 = p.parent / f"{base_name}.md"
    json_path = p.parent / f"{timestamp}_{base_name}.json"

    save(md_path, md_lines)
    save(json_path, links_by_date)
    print(f"Saved Markdown: {md_path}")
    print(f"Saved Markdown: {md_path_0}")
    print(f"Saved JSON: {json_path}")


if __name__ == "__main__":
    # Read and Write from Desktop
    f = os.path.join(MY_P_DESKTOP, "favorites.html")
    run(f)
