# Selectolax: Fast HTML Parsing

## What Is Selectolax?

Selectolax is a Python HTML/XML parsing library built on top of the C libraries **Modest** and **Lexbor**. It exposes an API similar in spirit to BeautifulSoup (CSS selectors, tag/attribute access) but is a compiled parser under the hood, so it parses large documents significantly faster.

## Why It Matters

- **Speed**: because parsing happens in C rather than pure Python, Selectolax typically parses HTML several times faster than BeautifulSoup with `lxml`. This matters when scraping thousands of pages, where parsing time adds up.
- **Trade-off**: it's a smaller, more focused library. It doesn't have BeautifulSoup's rich navigation API (no `.parent`/`.next_sibling` chains in the same style, no XPath support, no `html5lib`-level tolerance for badly broken markup) — it's best used when you just need to select elements and pull out text/attributes quickly.

## Installation

```bash
pip install selectolax
```

## Basic Usage

### 1. Import the parser

```python
from selectolax.parser import HTMLParser
```

### 2. Parse HTML into a tree

Works the same way whether the HTML comes from a string, a file you've read, or a `requests` response's `.text`:

```python
html_content = """<your HTML content here>"""
tree = HTMLParser(html_content)
```

```python
# Typical real-world usage: fetch, then parse
import requests
from selectolax.parser import HTMLParser

response = requests.get("https://books.toscrape.com/")
tree = HTMLParser(response.text)
```

### 3. Select elements with CSS selectors

`tree.css(selector)` returns a list of matching nodes — the same CSS selector syntax you'd use in BeautifulSoup's `select()`:

```python
# Select all links
links = tree.css('a')
for link in links:
    href = link.attributes.get('href')  # dict-like access to attributes
    text = link.text()                  # .text() is a method call in Selectolax, not a property
    print(f"Link text: {text}, URL: {href}")
```

```python
# Select all paragraphs
paragraphs = tree.css('p')
for p in paragraphs:
    print(p.text())
```

### 4. Get a single element

Use `tree.css_first(selector)` to get just the first match (equivalent to BeautifulSoup's `select_one()`), instead of indexing into `tree.css(selector)[0]`:

```python
first_link = tree.css_first('a')
if first_link:
    url = first_link.attributes.get('href')
    print(f"Extracted URL: {url}")
```

## Complete Example

```python
import requests
from selectolax.parser import HTMLParser

response = requests.get("https://books.toscrape.com/")
tree = HTMLParser(response.text)

books = tree.css('article.product_pod')

for book in books[:3]:
    title_node = book.css_first('h3 a')
    price_node = book.css_first('.price_color')

    title = title_node.attributes.get('title') if title_node else 'N/A'
    price = price_node.text() if price_node else 'N/A'

    print(f"Title: {title}")
    print(f"Price: {price}")
```

## Gotchas

- `.text()` is a **method**, not a property (unlike BeautifulSoup's `.text`) — forgetting the parentheses returns a bound method object instead of a string.
- `node.attributes` returns a dict where missing attributes simply aren't keys — use `.get('attr')` (or `.get('attr', default)`) rather than `['attr']` to avoid a `KeyError`.
- No JavaScript execution, same as BeautifulSoup — Selectolax only parses static HTML. For JS-rendered content, use Selenium first and feed the resulting HTML to Selectolax.

## Summary

1. Install with `pip install selectolax`.
2. Parse HTML into a tree with `HTMLParser(html_content)`.
3. Use `tree.css(selector)` / `tree.css_first(selector)` to locate elements.
4. Extract text with `.text()` and attributes with `.attributes.get('name')`.
5. Reach for Selectolax over BeautifulSoup specifically when parsing speed on static HTML is the bottleneck.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup Notes|BeautifulSoup Installation & Core Syntax]]
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup|Beautiful Soup]]
