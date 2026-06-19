"""Shared article-fetching and cleaning utilities for the style-transfer benchmark.

This module is the SINGLE source of truth imported by every generator and judge
notebook (see the "pipeline bootstrap" cell at the top of each notebook). Keeping
one copy here means every model and every judge sees the *same* preprocessed
article, instead of each notebook carrying its own slightly different copy.

Two responsibilities, deliberately separated:

  * ``fetch_html_body_content(url)`` does I/O only -- fetch the arXiv HTML page and
    flatten the ``<body>`` to text. No cleaning happens here.

  * ``get_article_snippet(text)`` does ALL cleaning and returns the article IN
    FULL -- there is no character cap, so the whole article is handed to the
    model/judge (audit H3). It:
        1. strips the arXiv nav/UI + table-of-contents boilerplate,
        2. strips leading front-matter (title / authors / abstract) up to the
           first section heading, and
        3. trims trailing end-matter -- acknowledgments, references / bibliography,
           appendices, and supplementary / supporting material (audit M7).
"""

import re

import requests
from bs4 import BeautifulSoup


# --- arXiv HTML nav/UI boilerplate (appears before the real article prose) ---
BOILERPLATE_EXACT = {
    "Report GitHub Issue", "Submit without GitHub", "Submit in GitHub",
    "Back to arXiv", "Why HTML?", "Report Issue", "Content selection saved",
    "Describe the issue below", "×",
}

# Substrings -- if ANY of these appear anywhere in the line, skip it.
BOILERPLATE_SUBSTRINGS = [
    "Report GitHub Issue",
    "Back to arXiv",
    "Why HTML?",
    "Report Issue",
    "Submit without GitHub",
    "Submit in GitHub",
    "Back to Introduction",
    "Back to ",            # catches "Back to <any section>"
    "Content selection saved",
    "Describe the issue below",
]

# --- End-matter section headings to trim (audit M7) ---
# Matched only against short, heading-style lines (optionally numbered), so an
# inline mention such as "see Appendix B" or "...in the acknowledgements" inside
# a sentence does NOT trigger a cut. arXiv HTML flattens each heading onto its
# own line, so heading detection is reliable.
_END_MATTER_KEYWORDS = (
    r"references|bibliography"
    r"|acknowledgements?|acknowledgments?|acknowledgement|acknowledgment"
    r"|appendix|appendices"
    r"|supplementary\s+(?:material|materials|information)"
    r"|supporting\s+information"
)
_END_MATTER_HEADING = re.compile(
    r"^\s*"
    r"(?:\d+(?:\.\d+)*\.?\s+|[A-Z]\.?\s+|[IVXLC]+\.?\s+)?"   # optional 1 / 1.2 / A / IV numbering
    r"(?:" + _END_MATTER_KEYWORDS + r")\b",
    re.I,
)

_INTRO_HEADING = re.compile(r"^\s*(?:\d+\.?\s+)?introduction\b", re.I)
_SECTION_ONE = re.compile(r"^\s*1(?:\.|\s)")

# A heading line is short; a sentence that merely mentions one of these words is
# long. Require the candidate line to be heading-length to avoid false cuts.
_MAX_HEADING_LEN = 60


def fetch_html_body_content(html_url):
    """Fetch an arXiv HTML page and return ``(body_text, status)``.

    I/O only -- no cleaning. ``body_text`` is the ``<body>`` flattened to one
    line per visible string. On any failure returns ``(None, <status>)`` where
    status is one of ``html_fetch_failed`` / ``no_body`` / ``empty_text``.
    """
    try:
        r = requests.get(html_url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print("⚠ HTML request failed:", e)
        return None, "html_fetch_failed"

    body = soup.find("body")
    if not body:
        return None, "no_body"

    lines = [line.strip() for line in body.stripped_strings if line.strip()]
    text = "\n".join(lines)
    if not text:
        return None, "empty_text"

    return text, "html_success"


def _strip_boilerplate(lines):
    """Drop the arXiv nav UI + table-of-contents preamble and stray TOC lines."""
    # Phase 1: find where real prose begins. TOC lines are short section titles;
    # real prose lines are longer and contain lowercase words forming sentences.
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) > 80 and " " in stripped and re.search(r"[a-z]", stripped):
            body_start = i
            break

    # Phase 2: from body_start onward, drop remaining boilerplate / bare numbers.
    cleaned = []
    for line in lines[body_start:]:
        stripped = line.strip()
        if not stripped:
            if cleaned:                       # preserve paragraph breaks
                cleaned.append("")
            continue
        if any(bp in stripped for bp in BOILERPLATE_SUBSTRINGS):
            continue
        if stripped in BOILERPLATE_EXACT:
            continue
        if re.match(r"^[A-Z]?\.?\d+(\.\d+)*$", stripped):   # bare "2", "2.1", "A.3"
            continue
        cleaned.append(line)
    return cleaned


def _strip_front_matter(lines):
    """Drop leading front-matter (title / authors / abstract) up to the first
    real section heading.

    Conservative replacement for the old lazy ``Abstract.*?Introduction`` regex
    (audit M6): scan only the top of the document for the first heading-style
    ``Introduction`` / ``1 ...`` line and drop everything before it. If no such
    heading is found near the top, return the text unchanged rather than risk
    eating the paper. (Anchoring on the section heading rather than the word
    "Abstract" is robust to the abstract heading already having been removed by
    the boilerplate/TOC pass.)
    """
    for i, line in enumerate(lines[:200]):
        stripped = line.strip()
        if len(stripped) <= _MAX_HEADING_LEN and (
            _INTRO_HEADING.match(stripped) or _SECTION_ONE.match(stripped)
        ):
            return lines[i:]
    return lines


def _trim_end_matter(lines):
    """Cut everything from the first end-matter heading onward (audit M7).
    
    Added safety guard: severe end-matter cuts should not happen at the very
    beginning of the paper. We only scan for end-matter headings after the first 30% 
    of the document lines to avoid false-positive triggers in the abstract/intro.
    """
    total_lines = len(lines)
    # We only start looking for "References/Appendix" after 30% of the paper
    safe_zone_limit = int(total_lines * 0.3) 
    
    for i, line in enumerate(lines):
        # If we are still in the first 30% of the paper, skip checking to prevent nuclear mis-cuts
        if i < safe_zone_limit:
            continue
            
        stripped = line.strip()
        if len(stripped) <= _MAX_HEADING_LEN and _END_MATTER_HEADING.match(stripped):
            # Found the real end-matter in the latter part of the paper!
            return lines[:i]
            
    return lines




def get_article_snippet_without_abstract(full_text):
    """Return the FULL cleaned article body EXCLUDING the abstract and front matter.
    
    Ideal for Style-Transfer Generation Models that only need the core text.
    """
    if not full_text:
        return ""

    lines = _strip_boilerplate(full_text.splitlines())
    lines = _strip_front_matter(lines)  # Cuts off everything before Introduction
    lines = _trim_end_matter(lines)

    return "\n".join(lines).strip()


def get_article_snippet_with_abstract(full_text):
    """Return the FULL cleaned article body INCLUDING the abstract and front matter.
    
    Ideal for Judge LLMs that need full context (Title, Authors, Abstract) 
    but still require boilerplate and end-matter (references) to be removed.
    """
    if not full_text:
        return ""

    lines = _strip_boilerplate(full_text.splitlines())
    # SKIPPED: _strip_front_matter(lines) -> Preserves Abstract and Metadata
    lines = _trim_end_matter(lines)

    return "\n".join(lines).strip()