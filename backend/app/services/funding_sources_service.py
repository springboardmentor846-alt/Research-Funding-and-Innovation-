"""
Additional funding source integrations (Phase 3).

Architecture note: the generic link-scraper below (_fetch_html, _links,
_looks_like_opportunity, _parse_date, _build_opportunity) extracts every
<a> link from a funding source's public listing page, keeps the ones that
look like an actual opportunity (by title keywords), and pulls a deadline
out of the surrounding text if present. This is intentionally generic
rather than tied to one page's exact HTML structure, so it keeps working
even if a source tweaks its page layout — verified against each real
source below before being wired in.

- Horizon (EU) and UKRI (UK Funding Finder) use this generic approach.
- ANRF (India) uses it against anrf.gov.in/page/english/research_grants
  (the public informational site — not anrfonline.in, which is a
  JS-driven application portal with nothing to scrape).
- BIRAC, DBT, ICMR (India) use dedicated table-scrapers, since their
  listings are plain server-rendered HTML tables (verified individually).
- Wellcome's site returns bot-detection blocks to simple automated
  fetches in some environments; it's scraped the same way as the others,
  but with a curated fallback in case a request gets blocked in practice.
Every function degrades to an empty/fallback list on any error — it
never raises, so a broken/changed/blocked upstream page never crashes
a request.
"""
import re
from datetime import date, datetime
from html import unescape
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.core.cache import ttl_cache

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ResearchFundingPlatform/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}

OPPORTUNITY_WORDS = (
    "call", "proposal", "grant", "fellowship", "scheme", "programme",
    "program", "research", "mission", "award", "fund", "funding",
)

BLOCKED_LINK_WORDS = (
    "home", "contact", "login", "register", "faq", "download",
    "privacy", "terms", "sitemap", "annual report", "vacancy",
    "tender", "news", "read more", "cookie", "sign in", "menu",
)


def _matches_keyword(text: str, keyword: str) -> bool:
    if not keyword:
        return True
    return keyword.lower() in (text or "").lower()


def _clean_text(value) -> str:
    if value is None:
        return ""
    text = unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_html(url: str) -> str:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=18)
    response.raise_for_status()
    return response.text


def _links(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    output = []
    for a in soup.find_all("a", href=True):
        text = _clean_text(a.get_text())
        href = a["href"]
        if not text or not href:
            continue
        url = urljoin(base_url, href)
        key = (text.lower(), url)
        if key not in seen:
            seen.add(key)
            output.append((text, url))
    return output


def _looks_like_opportunity(title: str) -> bool:
    if len(title) < 8:
        return False
    lower = title.lower()
    if any(lower == w or lower.startswith(w + " ") for w in BLOCKED_LINK_WORDS):
        return False
    return any(word in lower for word in OPPORTUNITY_WORDS)


_DATE_PATTERNS = (
    "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
    "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y",
)


def _parse_date(text: str):
    if not text:
        return None
    candidates = re.findall(
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4}|"
        r"\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})",
        text,
        flags=re.I,
    )
    parsed = []
    for value in candidates:
        value = re.sub(r"\s+", " ", value.strip())
        for fmt in _DATE_PATTERNS:
            try:
                parsed.append(datetime.strptime(value, fmt).date())
                break
            except ValueError:
                pass
    return max(parsed) if parsed else None


def _context_after_link(html: str, title: str, chars: int = 900) -> str:
    pos = html.lower().find(title.lower())
    if pos < 0:
        return title
    return _clean_text(html[pos:pos + chars])


def _build_opportunity(title, url, context, source, domains, eligibility_hint=""):
    deadline = _parse_date(context)
    return {
        "title": _clean_text(title)[:500],
        "source": source,
        "description": _clean_text(context)[:600] or f"See {source} for full details.",
        "eligibility": eligibility_hint or f"See {source} for eligibility criteria",
        "domains": domains,
        "deadline": deadline.isoformat() if deadline else "See source for current deadline",
        "amount": "See source for funding amount",
        "link": url,
    }


def _generic_scrape(url: str, source: str, domains: str, keyword_filter, eligibility_hint=""):
    """Shared scraper: fetch a page, keep opportunity-looking links, dedupe."""
    html = _fetch_html(url)
    items = []
    seen_links = set()
    for title, link in _links(html, url):
        if not _looks_like_opportunity(title):
            continue
        if keyword_filter and not any(w in title.lower() for w in keyword_filter):
            continue
        if link in seen_links:
            continue
        seen_links.add(link)
        context = _context_after_link(html, title)
        items.append(_build_opportunity(title, link, context, source, domains, eligibility_hint))
    return items


# ---------------- Horizon Europe (EU) ----------------

@ttl_cache(seconds=300)
def search_horizon(keyword: str, limit: int = 10):
    """
    Live search against the EU Funding & Tenders Portal search API.
    'SEDIA' is the fixed public apiKey the EU portal itself uses for
    read-only search access — no registration required.
    """
    try:
        response = requests.post(
            "https://api.tech.ec.europa.eu/search-api/prod/rest/search",
            params={"apiKey": "SEDIA", "text": keyword or "", "pageSize": max(20, limit * 2)},
            json={
                "query": {
                    "bool": {
                        "must": [
                            {"terms": {"type": ["1", "2", "8"]}},
                            {"terms": {"status": ["31094501", "31094502"]}},
                        ]
                    }
                }
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=18,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    except Exception:
        return []

    opportunities = []
    for item in results:
        metadata = item.get("metadata", {})

        def _first(field):
            value = metadata.get(field)
            if isinstance(value, list):
                return value[0] if value else None
            return value

        title = _first("title") or _first("title_en")
        if not title:
            continue
        identifier = item.get("reference") or _first("identifier") or ""
        deadline = _first("deadlineDate") or _first("startDate") or "See portal for current deadline"
        description = _clean_text(_first("description") or _first("description_en") or "")
        link = _first("url") or (
            f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/{identifier}"
            if identifier else "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home"
        )

        opportunities.append({
            "title": title[:500],
            "source": "Horizon Europe",
            "description": description[:600] or f"Reference: {identifier}",
            "eligibility": "See Horizon Europe Funding & Tenders Portal for eligibility",
            "domains": keyword or "European Research and Innovation",
            "deadline": deadline,
            "amount": "See portal for budget details",
            "link": link,
        })

    return opportunities[:limit]


# ---------------- UKRI (UK) — public Funding Finder ----------------

@ttl_cache(seconds=1800)
def _scrape_ukri_live(keyword: str, limit: int):
    try:
        return _generic_scrape(
            "https://www.ukri.org/opportunity/?keywords=apply+for+funding",
            source="UKRI",
            domains="Research and Innovation",
            keyword_filter=("fund", "grant", "fellowship", "award", "research", "call", "funding"),
            eligibility_hint="See UKRI for eligibility (UK research organisations, unless stated otherwise)",
        )
    except Exception:
        return []


def search_ukri(keyword: str, limit: int = 10):
    items = _scrape_ukri_live(keyword, limit)
    if keyword:
        items = [i for i in items if _matches_keyword(i["title"] + " " + i["description"], keyword)] or items
    return items[:limit]


# ---------------- ANRF (India) — public informational site ----------------

@ttl_cache(seconds=1800)
def _scrape_anrf_live():
    try:
        return _generic_scrape(
            "https://www.anrf.gov.in/page/english/research_grants",
            source="ANRF (India)",
            domains="Science, Technology, Engineering and Interdisciplinary Research",
            keyword_filter=None,
            eligibility_hint="See ANRF for scheme-specific eligibility (Indian researchers/institutions)",
        )
    except Exception:
        return []


_ANRF_FALLBACK = [
    {
        "title": "ANRF Advanced Research Grant (ARG / ARG-MATRICS)",
        "source": "ANRF (India)",
        "description": "Core competitive research grant for advanced, hypothesis-driven research proposals.",
        "eligibility": "Faculty/researchers at Indian academic and research institutions",
        "domains": "Natural Sciences, Engineering, Interdisciplinary Research",
        "deadline": "Rolling — see anrf.gov.in for current cycle",
        "amount": "Up to ₹5 Crore",
        "link": "https://www.anrf.gov.in/page/english/research_grants",
    },
    {
        "title": "ANRF National Post-Doctoral Fellowship (NPDF)",
        "source": "ANRF (India)",
        "description": "Fellowship supporting early-career researchers to pursue independent postdoctoral research.",
        "eligibility": "Recent PhD holders at Indian institutions",
        "domains": "All Science and Engineering Disciplines",
        "deadline": "Annual call — see anrf.gov.in",
        "amount": "Fellowship stipend + research grant",
        "link": "https://www.anrf.gov.in/page/english/research_grants",
    },
]


def search_anrf(keyword: str, limit: int = 10):
    live_results = _scrape_anrf_live()
    pool = live_results if live_results else _ANRF_FALLBACK
    matched = [p for p in pool if _matches_keyword(p["title"] + " " + p["domains"], keyword)]
    return (matched or pool)[:limit]


# ---------------- BIRAC (India) — live scrape with curated fallback ----------------
# BIRAC's "Call For Proposal" page (cfp.php) is a plain HTML table (verified,
# not JS-rendered), so it can be scraped reliably with requests + BeautifulSoup.

@ttl_cache(seconds=1800)
def _scrape_birac_live():
    try:
        html = _fetch_html("https://www.birac.nic.in/cfp.php")
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []

    opportunities = []
    for row in soup.select("table tr"):
        link_tag = row.find("a")
        if not link_tag or not link_tag.get("href"):
            continue
        title = link_tag.get_text(strip=True)
        if not title or "cfp_view.php" not in link_tag["href"]:
            continue

        row_text = row.get_text(" ", strip=True)
        deadline = "Not specified"
        if "Last Date of Submission" in row_text:
            deadline = row_text.split("Last Date of Submission")[-1].strip()

        link = link_tag["href"]
        full_link = link if link.startswith("http") else f"https://www.birac.nic.in/{link.lstrip('/')}"

        opportunities.append({
            "title": title,
            "source": "BIRAC (India)",
            "description": "See BIRAC Call for Proposal page for full scheme details.",
            "eligibility": "See specific call for eligibility criteria",
            "domains": "Biotechnology, Life Sciences, Startups",
            "deadline": deadline,
            "amount": "Varies by scheme — see call details",
            "link": full_link,
        })

    return opportunities


_BIRAC_FALLBACK = [
    {
        "title": "BIRAC Biotechnology Ignition Grant (BIG)",
        "source": "BIRAC (India)",
        "description": "Seed funding for early-stage biotech startups and entrepreneurs to validate proof-of-concept ideas.",
        "eligibility": "Biotech startups and individual innovators in India",
        "domains": "Biotechnology, Life Sciences, Startups",
        "deadline": "Rolling — see birac.nic.in for current cycle",
        "amount": "Up to INR 50 lakh",
        "link": "https://birac.nic.in/",
    },
    {
        "title": "BIRAC Small Business Innovation Research Initiative (SBIRI)",
        "source": "BIRAC (India)",
        "description": "Funding for high-risk, proof-of-concept to early-stage validation biotech research.",
        "eligibility": "Biotech startups and MSMEs in India",
        "domains": "Biotechnology, Product Development",
        "deadline": "See birac.nic.in for current call",
        "amount": "Varies by project stage",
        "link": "https://birac.nic.in/",
    },
]


def search_birac(keyword: str, limit: int = 10):
    live_results = _scrape_birac_live()
    pool = live_results if live_results else _BIRAC_FALLBACK
    matched = [p for p in pool if _matches_keyword(p["title"] + " " + p["domains"], keyword)]
    return (matched or pool)[:limit]


# ---------------- DBT (India) — live scrape with curated fallback ----------------

@ttl_cache(seconds=1800)
def _scrape_dbt_live():
    try:
        html = _fetch_html("https://dbtindia.gov.in/whats-new/call-for-proposals")
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []

    opportunities = []
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        link_tag = row.find("a")
        title = cells[1].get_text(strip=True) if len(cells) > 1 else None
        if not title:
            continue

        deadline = cells[2].get_text(strip=True) if len(cells) > 2 else "Not specified"

        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            full_link = href if href.startswith("http") else f"https://dbtindia.gov.in{href}"
        else:
            full_link = "https://dbtindia.gov.in/whats-new/call-for-proposals"

        opportunities.append({
            "title": title,
            "source": "DBT (India)",
            "description": "See DBT Call for Proposals page for full scheme details.",
            "eligibility": "See specific call for eligibility criteria",
            "domains": "Biotechnology, Life Sciences",
            "deadline": deadline or "Not specified",
            "amount": "Varies by scheme — see call details",
            "link": full_link,
        })

    return opportunities


_DBT_FALLBACK = [
    {
        "title": "DBT Extramural Research Grants",
        "source": "DBT (India)",
        "description": "Competitive research grants supporting biotechnology research across academic institutions in India.",
        "eligibility": "Faculty/researchers at Indian academic and research institutions",
        "domains": "Biotechnology, Life Sciences",
        "deadline": "Rolling — see dbtindia.gov.in for current cycle",
        "amount": "Varies by project scope",
        "link": "https://dbtindia.gov.in/",
    },
    {
        "title": "DBT-BioE3 Policy Research Support",
        "source": "DBT (India)",
        "description": "Supports biomanufacturing, bio-economy, and biotechnology-for-environment research.",
        "eligibility": "Academic and industry research teams in India",
        "domains": "Biomanufacturing, Bio-Economy, Environmental Biotechnology",
        "deadline": "See dbtindia.gov.in for current call",
        "amount": "Varies by call",
        "link": "https://dbtindia.gov.in/",
    },
]


def search_dbt(keyword: str, limit: int = 10):
    live_results = _scrape_dbt_live()
    pool = live_results if live_results else _DBT_FALLBACK
    matched = [p for p in pool if _matches_keyword(p["title"] + " " + p["domains"], keyword)]
    return (matched or pool)[:limit]


# ---------------- ICMR (India) — live scrape with curated fallback ----------------

@ttl_cache(seconds=1800)
def _scrape_icmr_live():
    try:
        html = _fetch_html("https://www.icmr.gov.in/call-for-proposals")
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []

    opportunities = []
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        serial = cells[0].get_text(strip=True)
        if not serial or not serial[0].isdigit():
            continue

        title = cells[1].get_text(strip=True) if len(cells) > 1 else None
        if not title:
            continue

        deadline = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        if not deadline and "Last Date" in title:
            deadline = title.split("Last Date")[-1].strip(": ")
        if not deadline:
            deadline = "Not specified"

        link_tag = row.find("a", href=True)
        if link_tag:
            href = link_tag["href"]
            full_link = href if href.startswith("http") else f"https://www.icmr.gov.in{href}"
        else:
            full_link = "https://www.icmr.gov.in/call-for-proposals"

        opportunities.append({
            "title": title,
            "source": "ICMR (India)",
            "description": "See ICMR Call for Proposals page for full scheme details.",
            "eligibility": "See specific call for eligibility criteria",
            "domains": "Biomedical Research, Public Health, Clinical Research",
            "deadline": deadline,
            "amount": "Varies by scheme — see call details",
            "link": full_link,
        })

    return opportunities


_ICMR_FALLBACK = [
    {
        "title": "ICMR Extramural Research Grants",
        "source": "ICMR (India)",
        "description": "Competitive grants supporting biomedical and health research at Indian institutions.",
        "eligibility": "Faculty/researchers at Indian medical and research institutions",
        "domains": "Biomedical Research, Public Health, Clinical Research",
        "deadline": "Rolling — see icmr.gov.in for current cycle",
        "amount": "Varies by project scope",
        "link": "https://icmr.gov.in/",
    },
    {
        "title": "ICMR Centres for Advanced Research (CAR)",
        "source": "ICMR (India)",
        "description": "Long-term institutional support for centres pursuing advanced biomedical research.",
        "eligibility": "Established Indian research institutions",
        "domains": "Biomedical Research, Health Systems",
        "deadline": "See icmr.gov.in for current call",
        "amount": "Multi-year institutional funding",
        "link": "https://icmr.gov.in/",
    },
]


def search_icmr(keyword: str, limit: int = 10):
    live_results = _scrape_icmr_live()
    pool = live_results if live_results else _ICMR_FALLBACK
    matched = [p for p in pool if _matches_keyword(p["title"] + " " + p["domains"], keyword)]
    return (matched or pool)[:limit]


# ---------------- Wellcome (International) — live scrape with curated fallback ----------------
# Wellcome's site can return bot-detection blocks to some automated fetchers;
# we still attempt a live scrape (a plain requests call with a normal User-Agent
# may pass where a stricter tool doesn't), and fall back to curated real
# programs if the request is blocked or the page returns nothing useful.

@ttl_cache(seconds=1800)
def _scrape_wellcome_live():
    try:
        return _generic_scrape(
            "https://wellcome.org/grant-funding",
            source="Wellcome",
            domains="Health, Life Sciences, Biomedical Research",
            keyword_filter=("award", "research", "fund", "discovery", "mental health", "infectious", "climate"),
            eligibility_hint="See Wellcome for scheme-specific eligibility (open worldwide, some exclusions apply)",
        )
    except Exception:
        return []


_WELLCOME_FALLBACK = [
    {
        "title": "Wellcome Discovery Awards",
        "source": "Wellcome",
        "description": "Long-term funding for exceptional researchers pursuing significant questions in human life, health and wellbeing.",
        "eligibility": "Established researchers worldwide (see Wellcome for eligibility)",
        "domains": "Health, Life Sciences, Biomedical Research",
        "deadline": "See wellcome.org for current cycle",
        "amount": "Multi-year, substantial funding",
        "link": "https://wellcome.org/grant-funding",
    },
    {
        "title": "Wellcome Mental Health Research Funding",
        "source": "Wellcome",
        "description": "Supports research aimed at understanding, preventing, and treating anxiety, depression and psychosis.",
        "eligibility": "Researchers worldwide working in mental health",
        "domains": "Mental Health, Neuroscience, Psychology",
        "deadline": "See wellcome.org for current cycle",
        "amount": "Varies by award",
        "link": "https://wellcome.org/grant-funding",
    },
]


def search_wellcome(keyword: str, limit: int = 10):
    live_results = _scrape_wellcome_live()
    pool = live_results if live_results else _WELLCOME_FALLBACK
    matched = [p for p in pool if _matches_keyword(p["title"] + " " + p["domains"], keyword)]
    return (matched or pool)[:limit]


# ---------------- Dispatcher ----------------

SOURCE_FUNCTIONS = {
    "horizon": search_horizon,
    "ukri": search_ukri,
    "anrf": search_anrf,
    "birac": search_birac,
    "dbt": search_dbt,
    "icmr": search_icmr,
    "wellcome": search_wellcome,
}


def search_funding_source(source: str, keyword: str, limit: int = 10):
    fn = SOURCE_FUNCTIONS.get(source.lower())
    if not fn:
        return []
    return fn(keyword, limit)