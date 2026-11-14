import pytest
from crawler.content_cleaner import clean_html, normalize_url, compute_content_hash


def test_clean_html_removes_scripts_and_nav():
    sample_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>WhatsApp Automation Issues</title>
        <script>alert('malicious or tracking');</script>
        <style>body { color: red; }</style>
      </head>
      <body>
        <nav>
          <a href="/home">Home</a>
          <a href="/about">About</a>
        </nav>
        <div class="cookie-banner">
          We use cookies to track you. Accept?
        </div>
        <main>
          <h1>Real User Pain Point</h1>
          <p>Small businesses struggle with high WhatsApp API template charges and complex setup procedures.</p>
        </main>
        <footer>
          <p>Copyright 2026. All rights reserved.</p>
        </footer>
      </body>
    </html>
    """
    result = clean_html(sample_html)
    assert result["title"] == "WhatsApp Automation Issues"
    assert "Real User Pain Point" in result["cleaned_text"]
    assert "Small businesses struggle" in result["cleaned_text"]
    assert "alert" not in result["cleaned_text"]
    assert "cookie" not in result["cleaned_text"].lower()
    assert "Home" not in result["cleaned_text"]
    assert result["word_count"] > 5


def test_normalize_url():
    dirty_url = "https://example.com/blog/article/?utm_source=twitter&utm_medium=cpc&b=2&a=1#section-2"
    cleaned = normalize_url(dirty_url)
    assert "utm_source" not in cleaned
    assert "utm_medium" not in cleaned
    assert "#section-2" not in cleaned
    assert cleaned == "https://example.com/blog/article?a=1&b=2"


def test_content_deduplication():
    text1 = "Many customers complain about WhatsApp cloud API limits and verification delays."
    text2 = "  Many customers   complain about WhatsApp cloud API limits and verification delays.  \n\n"
    text3 = "Completely different content about EV charging stations in Pune."

    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)
    hash3 = compute_content_hash(text3)

    assert hash1 == hash2
    assert hash1 != hash3
