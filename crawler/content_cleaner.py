import re
import hashlib
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from bs4 import BeautifulSoup

# Tracking query parameters to strip
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "source", "mc_cid", "mc_eid", "yclid"
}

# Elements to remove completely
EXCLUDED_TAGS = [
    "script", "style", "nav", "header", "footer", "aside", "form",
    "noscript", "svg", "iframe", "button", "select", "option", "canvas"
]

# Regex patterns for classes and IDs commonly associated with boilerplate
BOILERPLATE_PATTERN = re.compile(
    r"(cookie|banner|consent|gdpr|newsletter|subscribe|modal|popup|advert|disclaimer|share|social|author-bio|related-posts|breadcrumb)",
    re.IGNORECASE
)


def normalize_url(url: str) -> str:
    """
    Normalizes a URL by stripping tracking parameters, query fragments,
    lowercasing hostname, and removing redundant slashes.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()

        # Remove port if default
        if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
            netloc = netloc.rsplit(":", 1)[0]

        # Filter query params
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        clean_query = [(k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS]
        clean_query.sort()
        query_string = urlencode(clean_query)

        # Normalize path
        path = parsed.path or "/"
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]

        # Reconstruct without fragment
        clean_url = urlunparse((scheme, netloc, path, parsed.params, query_string, ""))
        return clean_url
    except Exception:
        return url.strip()


def compute_content_hash(text: str) -> str:
    """
    Computes a cryptographic hash of normalized text for duplicate detection.
    """
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def clean_html(html_content: str, default_title: str = "") -> dict:
    """
    Cleans raw HTML content by removing navigation, cookie notices, scripts,
    boilerplate, and extracts the page title and readable body text.

    Returns:
        dict: {
            "title": str,
            "cleaned_text": str,
            "word_count": int,
            "content_hash": str
        }
    """
    if not html_content or not html_content.strip():
        return {
            "title": default_title or "Untitled Page",
            "cleaned_text": "",
            "word_count": 0,
            "content_hash": ""
        }

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    title = default_title
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        h1 = soup.find("h1")
        if h1 and h1.text:
            title = h1.text.strip()

    # Remove script, style, nav, footer, etc.
    for tag in soup(EXCLUDED_TAGS):
        tag.decompose()

    # Remove elements with boilerplate classes/ids
    elements_to_remove = []
    for element in soup.find_all(True):
        if not hasattr(element, "attrs") or element.attrs is None:
            continue
        classes = element.attrs.get("class", [])
        if isinstance(classes, list):
            class_attr = " ".join(classes)
        else:
            class_attr = str(classes)
        id_attr = str(element.attrs.get("id", ""))
        combined_attrs = f"{class_attr} {id_attr}"
        if BOILERPLATE_PATTERN.search(combined_attrs):
            elements_to_remove.append(element)

    for element in elements_to_remove:
        try:
            element.decompose()
        except Exception:
            pass

    # Try extracting main article / content if available
    main_container = soup.find(["main", "article", "div[role='main']", "div.post-content", "div.entry-content"])
    target_node = main_container if main_container else soup.body or soup

    # Get text with clean whitespace
    text = target_node.get_text(separator="\n", strip=True)

    # Clean lines: remove blank lines, repetitive lines, very short snippets
    cleaned_lines = []
    seen_lines = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Deduplicate identical consecutive or repeated short boilerplate lines
        if len(line) < 3:
            continue
        if line.lower() in seen_lines and len(line) < 60:
            continue
        seen_lines.add(line.lower())
        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    words = re.findall(r"\b\w+\b", cleaned_text)
    word_count = len(words)
    content_hash = compute_content_hash(cleaned_text)

    return {
        "title": title or "Untitled Page",
        "cleaned_text": cleaned_text,
        "word_count": word_count,
        "content_hash": content_hash
    }
