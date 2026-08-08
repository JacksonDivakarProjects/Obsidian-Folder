# BeautifulSoup: Installation & Core Syntax

## Part 1: Installation & Packages

### Step-by-Step Installation

```bash
# 1. Install beautifulsoup4 (the main library)
pip install beautifulsoup4

# 2. Install requests (to fetch web pages)
pip install requests

# 3. Install lxml (fast HTML parser - recommended)
pip install lxml

# 4. OR install html5lib (alternative parser, slower but forgiving)
pip install html5lib
```

### What Each Package Does

| Package | Purpose | Why You Need It |
|---------|---------|-----------------|
| **beautifulsoup4** | HTML parsing library | Main tool to extract data |
| **requests** | HTTP client | Fetch web pages from URLs |
| **lxml** | HTML/XML parser | Fast parsing engine for BeautifulSoup |
| **html5lib** | Alternative parser | Handles messy/broken HTML better |

### Essential Imports

```python
import requests
from bs4 import BeautifulSoup
```

---

## Part 2: Creating BeautifulSoup Objects

### Method 1: From an HTML String

```python
html_doc = """
<html>
    <head><title>Test Page</title></head>
    <body>
        <div class="container" id="main">
            <p class="text">First paragraph</p>
            <p class="text special">Second paragraph</p>
            <a href="https://example.com">Link</a>
        </div>
    </body>
</html>
"""

# Create the BeautifulSoup object
soup = BeautifulSoup(html_doc, 'lxml')  # 'lxml' is the parser
```

### Method 2: From a Website (Most Common)

```python
import requests
from bs4 import BeautifulSoup

# Fetch the page
url = "https://books.toscrape.com/"
response = requests.get(url)

# Parse the HTML text into a soup object
soup = BeautifulSoup(response.text, 'lxml')
```

### Parser Comparison

```python
soup1 = BeautifulSoup(html, 'lxml')        # Fast, external (pip install lxml)
soup2 = BeautifulSoup(html, 'html.parser') # Built into Python, slower
soup3 = BeautifulSoup(html, 'html5lib')    # Very forgiving of broken HTML, slowest
```

**Recommendation:** use `'lxml'` for speed and reliability. Fall back to `'html5lib'` only if you're dealing with genuinely malformed HTML that `lxml` chokes on.

---

## Part 3: Core Syntax — Finding Elements

### `find()` — get the FIRST matching element

```python
# Find the first paragraph
first_p = soup.find('p')  # Returns a Tag object, or None if not found
print(first_p.text)  # "First paragraph"

# Find the first element with a class
first_div = soup.find('div', class_='container')
# OR
first_div = soup.find('div', {'class': 'container'})

# Find the first element with an id
main_div = soup.find(id='main')
# OR
main_div = soup.find('div', id='main')
```

### `find_all()` — get ALL matching elements

```python
# Find all paragraphs
all_paragraphs = soup.find_all('p')  # Returns a ResultSet (list-like)
print(f"Found {len(all_paragraphs)} paragraphs")

# Find all elements with class 'text'
text_elements = soup.find_all(class_='text')
# OR
text_elements = soup.find_all(attrs={'class': 'text'})

# Find all divs with class 'container'
divs = soup.find_all('div', class_='container')
```

---

## Part 4: Different Ways to Search

### By Tag Name

```python
all_links = soup.find_all('a')
h1_tags = soup.find_all('h1')
h2_tags = soup.find_all('h2')
```

### By Class (Most Important)

```python
# Elements with a single class
items = soup.find_all(class_='product')

# Elements matching a compound class string (order matters!)
items = soup.find_all(class_='product featured')
# Matches: <div class="product featured">
# Does NOT match: <div class="featured product">

# Elements with ANY of several classes
items = soup.find_all(class_=['product', 'item'])
# Matches class="product" OR class="item"

# Equivalent using attrs
items = soup.find_all(attrs={'class': 'product'})
```

### By ID

```python
element = soup.find(id='header')
# OR
element = soup.find('div', id='header')

# Multiple elements by id (uncommon, since ids should be unique per page)
elements = soup.find_all(id=['header', 'footer'])
```

### By Attributes

```python
# Elements that have a given attribute at all
images = soup.find_all('img', src=True)  # every <img> that has a src

# Elements with an exact attribute value
links = soup.find_all('a', href='https://example.com')

# Elements where an attribute value contains a substring
# (there is no href_contains= keyword in BeautifulSoup — use a regex or a lambda)
import re
links = soup.find_all('a', href=re.compile('example'))
links = soup.find_all('a', href=lambda href: href and 'example' in href)

# Multiple attributes at once
elements = soup.find_all('input', {'type': 'text', 'name': 'search'})
```

---

## Part 5: CSS Selectors with `select()` and `select_one()`

### `select()` — returns a list of elements matching a CSS selector

```python
products = soup.select('.product')            # class selector
header = soup.select('#main-header')           # id selector
paragraphs = soup.select('p')                  # tag selector
titles = soup.select('.product .title')        # descendant selector
items = soup.select('.list > .item')            # direct-child selector
elements = soup.select('.product, .item, .card')  # multiple selectors (comma = OR)
images = soup.select('img[src]')                # attribute-presence selector
links = soup.select('a[href^="https"]')         # attribute starts-with selector
```

### `select_one()` — returns the FIRST element matching a CSS selector

```python
first_product = soup.select_one('.product')
link = soup.select_one('header a')  # first <a> inside a <header>
```

CSS selectors and `find`/`find_all` do the same job — `select()` tends to be more concise for compound conditions (nesting, "starts with", multiple classes), while `find_all()` is more explicit when filtering on tag name plus one or two attributes.

---

## Part 6: Working with Results

### Accessing Data from a Single Element

```python
element = soup.find('div', class_='product')

# Text content
text = element.text                        # all text, including children's text
text = element.get_text()                  # same as .text
text = element.get_text(' ', strip=True)   # joined with a separator, whitespace stripped

# Attributes
link = element['href']          # direct access — raises KeyError if missing
link = element.get('href')      # safer — returns None if missing
link = element.get('href', '#') # safer still — returns a default if missing

# Checking for an attribute
if 'class' in element.attrs:
    print("Has a class attribute")

# All attributes as a dict
attrs = element.attrs
```

### Working with Multiple Elements (Lists)

```python
products = soup.find_all('div', class_='product')

# Loop through the list
for product in products:
    title = product.find('h2').text
    print(title)

# List comprehension
titles = [p.find('h2').text for p in products if p.find('h2')]

# Index / slice like any Python list
first_product = products[0]
last_product = products[-1]
first_5_products = products[:5]
```

---

## Part 7: Practical Examples

### Example 1: Scraping books.toscrape.com

```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# find_all with class_
books = soup.find_all('article', class_='product_pod')

# Equivalent using a CSS selector
books = soup.select('article.product_pod')

for book in books[:3]:  # first 3 only
    title1 = book.find('h3').find('a')['title']
    title2 = book.select_one('h3 a')['title']  # same result, different route

    price = book.find('p', class_='price_color').text
    link = book.find('h3').find('a')['href']

    print(f"Title: {title1}")
    print(f"Price: {price}")
    print(f"Link: {link}")
    print("-" * 30)
```

### Example 2: Extracting Data into a Dictionary

```python
import requests
from bs4 import BeautifulSoup

def extract_product_data(product):
    """Extract data from a single product element."""
    data = {}

    title_tag = product.find('h3')
    if title_tag:
        link_tag = title_tag.find('a')
        if link_tag:
            data['title'] = link_tag.get('title', 'No title')
            data['link'] = link_tag.get('href', '#')

    price_tag = product.find('p', class_='price_color')
    data['price'] = price_tag.text if price_tag else 'N/A'

    avail_tag = product.find('p', class_='instock')
    data['available'] = 'Yes' if avail_tag else 'No'

    return data

url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

products = soup.find_all('article', class_='product_pod')
all_data = [extract_product_data(p) for p in products]

for item in all_data[:3]:
    print(item)
```

---

## Part 8: Best Practices & Common Patterns

### 1. Always Check if an Element Exists

```python
# Risky: crashes with AttributeError if <h1> is missing
title = soup.find('h1').text

# Safe
title_tag = soup.find('h1')
title = title_tag.text if title_tag else 'Default Title'
```

### 2. Use `.get()` for Attributes

```python
link = tag['href']            # risky — raises KeyError if missing
link = tag.get('href')        # safe — returns None if missing
link = tag.get('href', '#')   # safe — returns a default if missing
```

### 3. Limit Results with the `limit` Parameter

```python
first_five = soup.find_all('div', class_='product', limit=5)
```

### 4. Search by Visible Text with `string`

```python
element = soup.find('p', string='Hello World')
element = soup.find('p', string=lambda text: text and 'price' in text.lower())
```

(`string=` is the current keyword; you may see the older, deprecated `text=` alias in tutorials — they behave the same in modern BeautifulSoup versions.)

### 5. Navigate Using Parent / Children / Siblings

```python
parent = element.parent
children = list(element.children)
first_child = list(element.children)[0]
next_sibling = element.next_sibling
previous_sibling = element.previous_sibling
```

### 6. Strip Whitespace

```python
clean_text = element.get_text(strip=True)
# or
clean_text = ' '.join(element.text.split())
```

---

## Part 9: Complete Working Template

```python
import requests
from bs4 import BeautifulSoup

class BasicScraper:
    def __init__(self, parser='lxml'):
        self.session = requests.Session()
        self.parser = parser

    def fetch_page(self, url):
        """Fetch and parse HTML from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # raises on 4xx/5xx responses
            return BeautifulSoup(response.text, self.parser)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def find_elements(self, soup, tag=None, class_name=None, id=None):
        """Find elements matching a combination of tag/class/id."""
        filters = {}
        if class_name:
            filters['class_'] = class_name
        if id:
            filters['id'] = id

        if tag:
            return soup.find_all(tag, **filters)
        if class_name:
            return soup.find_all(class_=class_name)
        if id:
            found = soup.find(id=id)
            return [found] if found else []
        return []

    def extract_attribute(self, element, attr_name, default=None):
        """Safely extract an attribute from an element."""
        return element.get(attr_name, default) if element else default

    def extract_text(self, element, default=''):
        """Safely extract text from an element."""
        return element.get_text(strip=True) if element else default

if __name__ == "__main__":
    scraper = BasicScraper()
    soup = scraper.fetch_page("https://books.toscrape.com/")

    if soup:
        books = scraper.find_elements(soup, 'article', 'product_pod')
        print(f"Found {len(books)} books")

        if books:
            first_book = books[0]
            title_tag = first_book.find('h3').find('a')
            title = scraper.extract_attribute(title_tag, 'title', 'No title')

            price_tag = first_book.find('p', class_='price_color')
            price = scraper.extract_text(price_tag, 'N/A')

            print(f"First book: {title} - {price}")
```

---

## Part 10: Common Pitfalls & Solutions

### Pitfall 1: Dynamic / Generated Class Names

Some sites generate randomized class names per build, e.g. `<div class="product-a1b2c3">...</div>`. An exact match on `class_='product-a1b2c3'` will break the next time the site redeploys.

```python
# Match on a partial class name instead
products = soup.find_all('div', class_=lambda x: x and 'product' in x)
# OR, with a CSS attribute-contains selector
products = soup.select('div[class*="product"]')
```

### Pitfall 2: Over-Broad or Under-Specific Searches

```python
# Too broad — matches every div on the page
soup.find_all('div')

# Better — describe the actual parent-child relationship you want
soup.select('.container .product-list .item')
```

### Pitfall 3: Text with Extra Whitespace

```python
text = element.text  # e.g. "\n   Hello World   \n"

clean_text = element.get_text(strip=True)      # "Hello World"
# or
clean_text = ' '.join(element.text.split())    # "Hello World"
```

### Pitfall 4: JavaScript-Rendered Content

BeautifulSoup only parses the HTML it's given — it never runs JavaScript. If the data you're looking for isn't present in `response.text` (view the page source, not the rendered DOM, to check), the content is likely injected by JS after load. In that case you need a browser-driving tool such as Selenium instead of (or in addition to) BeautifulSoup.

---

## Key Takeaways

1. **`find()`** for a single element, **`find_all()`** for multiple.
2. **`class_`** (with the trailing underscore) is used because `class` is a reserved Python keyword.
3. **`.get()`** is safer than direct attribute access with `['attr']`.
4. **CSS selectors** (`select()` / `select_one()`) are concise and often more readable than chained `find()` calls.
5. **Always check** whether an element exists before calling methods/attributes on it — `find()` returns `None` on no match.
6. **Strip whitespace** from extracted text before storing or comparing it.
7. BeautifulSoup has no concept of JavaScript — for JS-rendered pages, pair it with (or replace it with) Selenium.

---

## Homework Exercises

**Exercise 1 — Practice All Methods**
Build a small HTML string and practice:
1. `find()` by tag, class, and id
2. `find_all()` with different filters
3. `select()` with CSS selectors
4. Extracting attributes and text from each result

**Exercise 2 — Real Website**
Scrape `https://quotes.toscrape.com/` using:
1. `find_all()` with class names
2. `select()` with CSS selectors
3. Separately extract quote text, author, and tags

**Exercise 3 — Error Handling**
Write a function that safely extracts data even when tags are missing, attributes don't exist, or `find()` returns `None`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Selectolax/Selectolax Codes|Selectolax Codes]]
- [[Data Engineering Role Notes/Web Scraping/Selenium/Selenium Notes|Selenium WebDriver - Practical Essentials]]
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]]
