#!/usr/bin/env python3
"""Generates a markdown of exported browser history csv.

V2

Prompt
There were also some more prompts ... but I won't note down the steps here any more 😀

Refactor the following python program in 4 Steps

Step 1:
For the domain statistics section:
- Add a h2 header to the section:
- ## Stats By Domain and add the existing table
- ## Top 40 Domains listing the domains with the highest count, sorted descending order

Step 2:
- Order the Link by Date Section in descending order
- In that Section, show duplicate links for a given date only once, followed by number of duplicate show in brackets after the link
- On the Chapter level ### YYYY-MM-DD add the number of occuring links assigned to that day

Step 3:
- Drop the Duplicates Section

Step 4:
- Adjust the Navigation bar to show the links to navigaate to
  - Table of Contents
  - Stats By Domain
  - Top 40 Domains
  - Links to the last recent day sections (habing the title of ### YYYY-MM-DD )

Here's the python program ...


V1

Check the original python script. It originally was used for parsing the XML base export of internet favorites from Edge browser.
Now do a redesign of this code to import the CSV File export of browser history.

The CSV has columns DateTime containing Timestamp ,NavigatedToUrl the url ,PageTitle the title name of the link.
Here is an example
DateTime,NavigatedToUrl,PageTitle
2025-09-29T15:16:20.101Z,https://www.xyz.com/,bla vla

Rewrite existing code with these requiremnts:
* Read the CSV and convert it to UTF-8, as it might have a different encoding format such as UTF-8-BOM
* Extract the CSV contents into a dict containing an consecutive index number as key, and as dictionary atrtributes;:
- "DateTime" the datetime string (in the format YYYY-MM-DDThh:mm:ss.tttZ as shown in the example, in ISO Format) transformed into datetime.datetime object,
- "url" containing NavigatedToUrl
- "base_url" containing the base url (without leading http://www.) derived from NavigatedToUrl
- "title" containing PageTitle

As for the original version, generate:
- the Table Of Content section as generated with function generate_toc_table_vertical_heatmap (showing the number of visited links)
  But make the table of content s just one line showing the number of links visited in a month with the last column being the current month, and just the last 12 preceding months i the previous columns.
- Keep the domain statistics section just as generated using function format_domain_table_recent
- Add a section and subsections of previously visited links, as for the existing code into subsections by year (# yyyy) , year-month (## yyyy-mm), year-month-day (### yyyy-mm-dd). If there are duplicate links on the level ### yyyy-mm-dd, just add one link in the display list, but add the count of how many duplicates were found in brackets behind the link in that line
- Finally, add a a sections of # Duplicates per MOnth on Header level 1. Header Level two is ## YYYY-MM Dupllicates. As lines , add as list (markdown format * ) all duplicate links that are found for this month, sorted by it's link url

Here's the original Code ...

"""

import os
import sys
import traceback
import json
import csv
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import re

# get read/write path from env
from config.myenv import MY_P_DESKTOP


def save(filepath, data):
    """Saves string data or stringified dict"""
    if isinstance(data, dict):
        data = json.dumps(data, indent=4, ensure_ascii=False, default=str)
    elif isinstance(data, list):
        data = "\n".join(data)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception:
        print(f"Error writing to {filepath}")
        print(traceback.format_exc())


def get_root_domain(url):
    """Extracts root domain from URL, stripping http://, https://, www."""
    try:
        netloc = urlparse(url).netloc
        domain = netloc.lower().replace("www.", "")
        return domain
    except:
        return ""


def read_csv_history(filename):
    """Reads CSV and returns parsed dict with DateTime, url, base_url, title"""
    records = {}
    try:
        with open(filename, "r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader, start=1):
                dt = datetime.fromisoformat(row["DateTime"].replace("Z", "+00:00"))
                url = row["NavigatedToUrl"].strip("[]")
                base_url = get_root_domain(url)
                title = row["PageTitle"]
                records[idx] = {
                    "DateTime": dt,
                    "url": url,
                    "base_url": base_url,
                    "title": title,
                }
    except Exception:
        print(f"Error reading {filename}")
        print(traceback.format_exc())
    return records


def generate_toc_summary(records):
    """One-line TOC showing links per last 12 months"""
    month_counts = Counter()
    for rec in records.values():
        mkey = rec["DateTime"].strftime("%Y-%m")
        month_counts[mkey] += 1

    now = datetime.utcnow()
    months = [(now.year, now.month)]
    for i in range(1, 12):
        prev = now.replace(day=1) - timedelta(days=30 * i)
        months.append((prev.year, prev.month))

    header = [
        "# Table of Contents",
        "",
        "| Month | " + " | ".join(f"{y}-{str(m).zfill(2)}" for y, m in reversed(months)) + " |",
    ]

    divider = "|-------" + "|-------" * len(months) + "|"

    row = ["| Count "]
    for y, m in reversed(months):
        key = f"{y}-{str(m).zfill(2)}"
        count = month_counts.get(key, 0)
        row.append(f"| {count} ")
    row.append("|")

    return header + [divider, "".join(row), ""]


def indicator_from_cumulative(cumulative):
    """Return a 10-char indicator string based on cumulative percentage"""
    if cumulative < 10:
        return "🟪🟦🟦🟦🟦🟦🟦🟦🟦🟦"
    elif cumulative < 20:
        return "🟪🟪🟦🟦🟦🟦🟦🟦🟦🟦"
    elif cumulative < 30:
        return "🟩🟩🟩🟦🟦🟦🟦🟦🟦🟦"
    elif cumulative < 40:
        return "🟩🟩🟩🟩🟦🟦🟦🟦🟦🟦"
    elif cumulative < 50:
        return "🟨🟨🟨🟨🟨🟦🟦🟦🟦🟦"
    elif cumulative < 60:
        return "🟨🟨🟨🟨🟨🟨🟦🟦🟦🟦"
    elif cumulative < 70:
        return "🟧🟧🟧🟧🟧🟧🟧🟦🟦🟦"
    elif cumulative < 80:
        return "🟧🟧🟧🟧🟧🟧🟧🟧🟦🟦"
    elif cumulative < 90:
        return "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟦"
    else:
        return "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥"


def format_domain_table_recent(records):
    """Markdown table of ALL domain frequencies within last 365 days + Top 100 section with cumulative percentages + indicators"""
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    domain_counter = Counter()

    for rec in records.values():
        if rec["DateTime"] >= one_year_ago:
            domain_counter[rec["base_url"]] += 1

    total_recent_links = sum(domain_counter.values()) if domain_counter else 1

    lines = [
        "## Stats By Domain",
        "",
        f"_Total entries in the last 365 days: **{total_recent_links}**_",
        "",
        "| Domain | Count | % |",
        "|--------|-------|---|",
    ]

    # Show ALL domains alphabetically
    for domain, count in sorted(domain_counter.items(), key=lambda x: x[0].lower()):
        percent = (count / total_recent_links) * 100
        url = f"https://{domain}"
        link = f"[{domain}]({url})"
        lines.append(f"| {link} | {count} | {percent:.2f}% |")

    lines.append("")

    # Top 100 domains list with cumulative and indicator
    lines.append("## Top 100 Domains")
    lines.append(f"_Total links in last 365 days: **{total_recent_links}**_")  # <-- NEW LINE

    cumulative = 0
    for domain, count in domain_counter.most_common(100):
        percent = (count / total_recent_links) * 100
        cumulative += percent
        url = f"https://{domain}"
        link = f"[{domain}]({url})"
        indicator = indicator_from_cumulative(cumulative)
        lines.append(f"* {indicator} {link} ({count}, {percent:.2f}%, cumulated {cumulative:.2f}%)")
    lines.append("")

    return lines


def generate_anchor(header_text):
    """Sanitize header text to GitHub-style Markdown anchor format"""
    anchor = header_text.lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = anchor.strip().replace(" ", "-")
    return anchor


def build_sidebar_anchors(records):
    """Build anchor list for floating sidebar."""
    anchors = []
    anchors.append(("Table of Contents", "table-of-contents"))
    anchors.append(("Stats By Domain", "stats-by-domain"))
    anchors.append(("Top 100 Domains", "top-100-domains"))

    daily_counts = Counter()
    for rec in records.values():
        ymd = rec["DateTime"].strftime("%Y-%m-%d")
        daily_counts[ymd] += 1

    recent_days = sorted(daily_counts.items(), key=lambda x: x[0], reverse=True)

    for ymd, count in recent_days[:7]:
        header_text = f"{ymd} ({count} links)"
        anchors.append((header_text, generate_anchor(header_text)))

    return anchors


def generate_floating_sidebar(anchors):
    """Returns HTML+CSS for a right-aligned floating TOC sidebar"""
    sidebar = [
        "<style>",
        "#toc-sidebar {",
        "  position: fixed;",
        "  top: 80px;",
        "  right: 20px;",
        "  width: 220px;",
        "  background: #2e2e2e;",
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


def create_markdown(records):
    """Creates structured markdown grouped by year -> month -> day -> domain with clickable domain headers, sorted domains and links"""
    all_entries = sorted(records.values(), key=lambda x: x["DateTime"], reverse=True)

    year_month_day_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Counter))))

    for rec in all_entries:
        y = rec["DateTime"].strftime("%Y")
        ym = rec["DateTime"].strftime("%Y-%m")
        ymd = rec["DateTime"].strftime("%Y-%m-%d")
        domain = rec["base_url"]
        url = rec["url"]
        title = rec["title"]
        year_month_day_counts[y][ym][ymd][domain][(url, title)] += 1

    md_lines = []
    for y in sorted(year_month_day_counts.keys(), reverse=True):
        md_lines.append(f"# {y}")
        for ym in sorted(year_month_day_counts[y].keys(), reverse=True):
            md_lines.append(f"## {ym}")
            for ymd in sorted(year_month_day_counts[y][ym].keys(), reverse=True):
                daily_domains = year_month_day_counts[y][ym][ymd]
                day_count = sum(count for domain_links in daily_domains.values() for count in domain_links.values())
                md_lines.append(f"### {ymd} ({day_count} links)")
                # sort domains alphabetically
                for domain in sorted(daily_domains.keys(), key=lambda d: d.lower()):
                    domain_url = f"https://{domain}"
                    md_lines.append(f"* [{domain}]({domain_url})")
                    # sort links alphabetically
                    for (url, title), count in sorted(
                        daily_domains[domain].items(),
                        key=lambda x: (x[0][1] or x[0][0]).lower(),
                    ):
                        dup_suffix = f" ({count})" if count > 1 else ""
                        md_lines.append(f"  * [{title}]({url}){dup_suffix}")
            md_lines.append("")
    return md_lines


def run(csv_file):
    p = Path(csv_file)
    if not p.is_file():
        print(f"{csv_file} is not a valid file.")
        sys.exit()

    records = read_csv_history(csv_file)

    anchors = build_sidebar_anchors(records)
    sidebar_html = generate_floating_sidebar(anchors)

    md_lines = []
    md_lines.extend(sidebar_html)
    md_lines.append("")
    md_lines.extend(generate_toc_summary(records))
    md_lines.extend(format_domain_table_recent(records))
    md_lines.extend(create_markdown(records))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = p.stem
    md_path = p.parent / f"{timestamp}_{base_name}.md"
    json_path = p.parent / f"{timestamp}_{base_name}.json"

    save(md_path, md_lines)
    save(json_path, records)
    print(f"Saved Markdown: {md_path}")
    print(f"Saved JSON: {json_path}")


if __name__ == "__main__":
    # Read and Write from Desktop
    f = os.path.join(MY_P_DESKTOP, "BrowserHistory.csv")
    run(f)
