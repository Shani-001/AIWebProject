import time
import datetime
import logging
from typing import List, Dict, Optional, Callable, Set
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import settings
from crawler.content_cleaner import clean_html, normalize_url, compute_content_hash
from crawler.search import search_web_candidates

logger = logging.getLogger(__name__)


class WebCrawlerEngine:
    """
    Ethical, robust web crawler that respects robots.txt, applies politeness delays,
    removes boilerplate, handles HTTP errors gracefully, and deduplicates content.
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: int = 5,
        delay: float = 0.2
    ):
        self.user_agent = user_agent or settings.USER_AGENT
        self.timeout = timeout
        self.delay = delay

        # Configure resilient requests session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

        # Cache for robots.txt parsers by domain
        self._robots_cache: Dict[str, RobotFileParser] = {}

    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Fetches and evaluates the site's robots.txt for our user agent.
        Defaults to allowed if robots.txt is unreachable or not present.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                return False

            if domain not in self._robots_cache:
                robots_url = f"{parsed.scheme}://{domain}/robots.txt"
                rfp = RobotFileParser()
                rfp.set_url(robots_url)
                try:
                    resp = self.session.get(robots_url, timeout=5)
                    if resp.status_code == 200:
                        rfp.parse(resp.text.splitlines())
                    else:
                        rfp.allow_all = True
                except Exception:
                    # If robots.txt cannot be read, default to allow politely
                    rfp.allow_all = True
                self._robots_cache[domain] = rfp

            return self._robots_cache[domain].can_fetch(self.user_agent, url)
        except Exception as e:
            logger.debug(f"robots.txt check error for {url}: {e}")
            return True

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches HTML for a single URL with error handling, timeout, and content-type validation.
        """
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if resp.status_code != 200:
                logger.warning(f"HTTP {resp.status_code} for {url}")
                return None

            content_type = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                logger.info(f"Skipping non-HTML content-type '{content_type}' at {url}")
                return None

            return resp.text
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def crawl_topic(
        self,
        topic: str,
        keywords: Optional[str] = None,
        max_pages: int = settings.MAX_PAGES_DEFAULT,
        domain_restrictions: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, any]:
        """
        Orchestrates full crawling pipeline:
        1. Discover candidates across multiple domains
        2. Filter by robots.txt and domain rules
        3. Fetch, clean, and deduplicate
        4. Accumulate up to max_pages across at least 3 domains
        """
        start_time = datetime.datetime.now(datetime.timezone.utc)
        if progress_callback:
            progress_callback(f"Discovering candidate web pages for topic: '{topic}'...", 0, max_pages)

        # 1. Search candidates
        candidates = search_web_candidates(
            topic=topic,
            keywords=keywords,
            domain_restrictions=domain_restrictions,
            target_count=max(max_pages * 2, 40)
        )

        # Interleave candidates across domains to guarantee balanced coverage across at least 3 domains
        from collections import defaultdict
        domain_groups = defaultdict(list)
        for cand in candidates:
            dom = cand.get("domain", "")
            domain_groups[dom].append(cand)

        interleaved_candidates = []
        all_doms = list(domain_groups.keys())
        max_len = max((len(v) for v in domain_groups.values()), default=0)
        for i in range(max_len):
            for dom in all_doms:
                if i < len(domain_groups[dom]):
                    interleaved_candidates.append(domain_groups[dom][i])

        crawled_pages: List[Dict] = []
        seen_urls: Set[str] = set()
        seen_content_hashes: Set[str] = set()
        domains_covered: Set[str] = set()

        processed_count = 0
        total_candidates = len(interleaved_candidates)

        for candidate in interleaved_candidates:
            if len(crawled_pages) >= max_pages and len(domains_covered) >= 3:
                break

            raw_url = candidate["url"]
            clean_url = normalize_url(raw_url)
            parsed = urlparse(clean_url)
            domain = parsed.netloc.lower()

            # URL deduplication
            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)

            # Domain restriction check
            if domain_restrictions:
                if not any(d.lower() in domain for d in domain_restrictions if d):
                    continue

            # Respect robots.txt
            if not self.is_allowed_by_robots(clean_url):
                logger.info(f"Blocked by robots.txt: {clean_url}")
                continue

            processed_count += 1
            if progress_callback:
                progress_callback(
                    f"Crawling ({len(crawled_pages)+1}/{max_pages}): {domain}...",
                    len(crawled_pages),
                    max_pages
                )

            # Fetch HTML
            html = self.fetch_page(clean_url)
            if not html:
                time.sleep(self.delay)
                continue

            # Clean content & remove boilerplate
            cleaned_result = clean_html(html, default_title=candidate.get("title", ""))
            cleaned_text = cleaned_result["cleaned_text"]
            content_hash = cleaned_result["content_hash"]
            word_count = cleaned_result["word_count"]

            # Content deduplication
            if content_hash in seen_content_hashes:
                logger.info(f"Duplicate content detected for {clean_url}, skipping.")
                continue

            # Skip thin / empty pages (< 40 words)
            if word_count < 40:
                logger.info(f"Skipping thin page ({word_count} words): {clean_url}")
                continue

            seen_content_hashes.add(content_hash)
            domains_covered.add(domain)

            crawl_item = {
                "url": clean_url,
                "domain": domain,
                "title": cleaned_result["title"],
                "crawl_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "text_content": cleaned_text,
                "word_count": word_count,
                "content_hash": content_hash,
                "snippet": candidate.get("snippet", "")
            }
            crawled_pages.append(crawl_item)

            # Politeness delay
            time.sleep(self.delay)

        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()

        summary_note = ""
        if len(crawled_pages) < max_pages:
            summary_note = (
                f"Crawled {len(crawled_pages)} pages out of requested {max_pages}. "
                f"Some URLs were filtered due to robots.txt restrictions, HTTP errors, "
                f"or thin content."
            )
        else:
            summary_note = f"Successfully crawled {len(crawled_pages)} unique pages across {len(domains_covered)} domains."

        return {
            "topic": topic,
            "pages": crawled_pages,
            "pages_crawled_count": len(crawled_pages),
            "domains_count": len(domains_covered),
            "domains_covered": list(domains_covered),
            "duration_seconds": round(duration_seconds, 2),
            "summary_note": summary_note
        }
