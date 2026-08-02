# ** BeautifulSoup Installation & Core Syntax**

## **Part 1: Installation & Packages**

### **Step-by-Step Installation:**

```bash
# 1. Install beautifulsoup4 (the main library)
pip install beautifulsoup4

# 2. Install requests (to fetch web pages)
pip install requests

# 3. Install lxml (fast HTML parser - recommended)
pip install lxml

# 4. OR Install html5lib (alternative parser, slower but forgiving)
pip install html5lib
```

### **What Each Package Does:**

| Package | Purpose | Why You Need It |
|---------|---------|-----------------|
| **beautifulsoup4** | HTML parsing library | Main tool to extract data |
| **requests** | HTTP client | Fetch web pages from URLs |
| **lxml** | HTML/XML parser | Fast parsing engine for BeautifulSoup |
| **html5lib** | Alternative parser | Handles messy HTML better |

### **Import Statements:**
```python
# Essential imports
import requests
from bs4 import BeautifulSoup
```

---

## **Part 2: Creating BeautifulSoup Objects**

### **Method 1: From HTML String**
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

# Create BeautifulSoup object
soup = BeautifulSoup(html_doc, 'lxml')  # 'lxml' is the parser
```

### **Method 2: From Website (Most Common)**
```python
import requests
from bs4 import BeautifulSoup

# Fetch website
url = "https://books.toscrape.com/"
response = requests.get(url)

# Create soup object
soup = BeautifulSoup(response.text, 'lxml')  # response.text is HTML string
```

### **Parser Comparison:**
```python
# Different parsers you can use:
soup1 = BeautifulSoup(html, 'lxml')       # Fast, external (need to install)
soup2 = BeautifulSoup(html, 'html.parser') # Built-in, slower
soup3 = BeautifulSoup(html, 'html5lib')   # Very forgiving, slow
```

**Recommendation:** Use `'lxml'` for speed and reliability.

---

## **Part 3: Core Syntax - Finding Elements**

### **1. `find()` - Get FIRST matching element**
```python
# Find first paragraph
first_p = soup.find('p')  # Returns Tag object or None
print(first_p.text)  # "First paragraph"

# Find first element with class
first_div = soup.find('div', class_='container')
# OR
first_div = soup.find('div', {'class': 'container'})

# Find first element with id
main_div = soup.find(id='main')
# OR
main_div = soup.find('div', id='main')
```

### **2. `find_all()` - Get ALL matching elements**
```python
# Find all paragraphs
all_paragraphs = soup.find_all('p')  # Returns ResultSet (list-like)
print(f"Found {len(all_paragraphs)} paragraphs")

# Find all elements with class 'text'
text_elements = soup.find_all(class_='text')
# OR
text_elements = soup.find_all(attrs={'class': 'text'})

# Find all divs with class 'container'
divs = soup.find_all('div', class_='container')
```

---

## **Part 4: Different Ways to Search**

### **By Tag Name:**
```python
# All links
all_links = soup.find_all('a')

# All headers
h1_tags = soup.find_all('h1')
h2_tags = soup.find_all('h2')
```

### **By Class (MOST IMPORTANT):**
```python
# Elements with single class
items = soup.find_all(class_='product')

# Elements with multiple classes (order matters!)
items = soup.find_all(class_='product featured')
# This matches: <div class="product featured"> NOT <div class="featured product">

# Elements with ANY of multiple classes
items = soup.find_all(class_=['product', 'item'])
# Matches class="product" OR class="item"

# Using CSS class selector
items = soup.find_all(attrs={'class': 'product'})
```

### **By ID:**
```python
# Element with specific ID
element = soup.find(id='header')
# OR
element = soup.find('div', id='header')

# Multiple elements with IDs (rare)
elements = soup.find_all(id=['header', 'footer'])
```

### **By Attributes:**
```python
# Find elements with specific attribute
images = soup.find_all('img', src=True)  # All img tags with src

# Find elements with specific attribute value
links = soup.find_all('a', href='https://example.com')

# Find elements where attribute contains value
links = soup.find_all('a', href_contains='example')

# Multiple attributes
elements = soup.find_all('input', {'type': 'text', 'name': 'search'})
```

---

## **Part 5: CSS Selectors with `select()` and `select_one()`**

### **`select()` - Returns list of elements matching CSS selector**
```python
# Class selector
products = soup.select('.product')

# ID selector
header = soup.select('#main-header')

# Tag selector
paragraphs = soup.select('p')

# Descendant selector
titles = soup.select('.product .title')

# Child selector
items = soup.select('.list > .item')

# Multiple selectors
elements = soup.select('.product, .item, .card')

# Attribute selector
images = soup.select('img[src]')
links = soup.select('a[href^="https"]')  # Starts with https
```

### **`select_one()` - Returns FIRST element matching CSS selector**
```python
# Get first product
first_product = soup.select_one('.product')

# Get first link inside header
link = soup.select_one('header a')
```

---

## **Part 6: Working with Results**

### **Accessing Data from Single Element:**
```python
element = soup.find('div', class_='product')

# Get text content
text = element.text            # All text including children
text = element.get_text()      # Same as .text
text = element.get_text(' ', strip=True)  # With separator

# Get attributes
link = element['href']         # Direct access (might fail)
link = element.get('href')     # Safer, returns None if not found
link = element.get('href', '#') # With default value

# Check if attribute exists
if 'class' in element.attrs:
    print("Has class attribute")

# Get all attributes as dict
attrs = element.attrs  # Returns dictionary
```

### **Working with Multiple Elements (Lists):**
```python
# Get all products
products = soup.find_all('div', class_='product')

# Method 1: Loop through list
for product in products:
    title = product.find('h2').text
    print(title)

# Method 2: List comprehension
titles = [p.find('h2').text for p in products if p.find('h2')]

# Method 3: Access by index
first_product = products[0]
last_product = products[-1]

# Method 4: Slice the list
first_5_products = products[:5]
```

---

## **Part 7: Practical Examples**

### **Example 1: Scraping Books.toscrape.com**
```python
import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Method 1: Using find_all with class_
books = soup.find_all('article', class_='product_pod')

# Method 2: Using CSS selectors (alternative)
books = soup.select('article.product_pod')

for book in books[:3]:  # First 3 only
    # Title (multiple ways)
    title1 = book.find('h3').find('a')['title']
    title2 = book.select_one('h3 a')['title']
    
    # Price
    price = book.find('p', class_='price_color').text
    
    # Link
    link = book.find('h3').find('a')['href']
    
    print(f"Title: {title1}")
    print(f"Price: {price}")
    print(f"Link: {link}")
    print("-" * 30)
```

### **Example 2: Extracting All Data into Dictionary**
```python
import requests
from bs4 import BeautifulSoup

def extract_product_data(product):
    """Extract data from a single product element"""
    data = {}
    
    # Title with safe access
    title_tag = product.find('h3')
    if title_tag:
        link_tag = title_tag.find('a')
        if link_tag:
            data['title'] = link_tag.get('title', 'No title')
            data['link'] = link_tag.get('href', '#')
    
    # Price with safe access
    price_tag = product.find('p', class_='price_color')
    data['price'] = price_tag.text if price_tag else 'N/A'
    
    # Availability
    avail_tag = product.find('p', class_='instock')
    data['available'] = 'Yes' if avail_tag else 'No'
    
    return data

# Usage
url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

products = soup.find_all('article', class_='product_pod')
all_data = [extract_product_data(p) for p in products]

for item in all_data[:3]:
    print(item)
```

---

## **Part 8: Best Practices & Common Patterns**

### **1. Always Check if Element Exists**
```python
# BAD: Might crash
title = soup.find('h1').text

# GOOD: Safe check
title_tag = soup.find('h1')
if title_tag:
    title = title_tag.text
else:
    title = 'Default Title'

# BETTER: Using get with default
title = soup.find('h1').text if soup.find('h1') else 'Default'
```

### **2. Use `get()` for Attributes**
```python
# BAD: Might raise KeyError
link = tag['href']

# GOOD: Returns None if not found
link = tag.get('href')

# BETTER: With default value
link = tag.get('href', '#')
```

### **3. Limit Results with `limit` Parameter**
```python
# Get only first 5 matching elements
first_five = soup.find_all('div', class_='product', limit=5)
```

### **4. Use `string` Parameter for Text Search**
```python
# Find element containing specific text
element = soup.find('p', string='Hello World')
element = soup.find('p', string=lambda text: 'price' in text.lower())
```

### **5. Navigate Using Parent/Children**
```python
# Get parent
parent = element.parent

# Get all children
children = list(element.children)

# Get specific child by index
first_child = list(element.children)[0]

# Navigate siblings
next_sibling = element.next_sibling
previous_sibling = element.previous_sibling
```

### **6. Strip Whitespace**
```python
# Get clean text
clean_text = element.get_text(strip=True)

# Or clean after getting
text = element.text.strip()
```

---

## **Part 9: Complete Working Template**

```python
import requests
from bs4 import BeautifulSoup

class BasicScraper:
    def __init__(self, parser='lxml'):
        self.session = requests.Session()
        self.parser = parser
        
    def fetch_page(self, url):
        """Fetch HTML from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Check for HTTP errors
            return BeautifulSoup(response.text, self.parser)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def find_elements(self, soup, tag=None, class_name=None, id=None):
        """Find elements with multiple criteria"""
        filters = {}
        
        if class_name:
            filters['class_'] = class_name
        if id:
            filters['id'] = id
        
        if tag:
            return soup.find_all(tag, **filters)
        else:
            # Find by class or id only
            if class_name:
                return soup.find_all(class_=class_name)
            elif id:
                return [soup.find(id=id)] if soup.find(id=id) else []
        
        return []
    
    def extract_attribute(self, element, attr_name, default=None):
        """Safely extract attribute from element"""
        return element.get(attr_name, default)
    
    def extract_text(self, element, default=''):
        """Safely extract text from element"""
        return element.get_text(strip=True) if element else default

# Usage example
if __name__ == "__main__":
    scraper = BasicScraper()
    
    # Get page
    soup = scraper.fetch_page("https://books.toscrape.com/")
    
    if soup:
        # Find all books
        books = scraper.find_elements(soup, 'article', 'product_pod')
        print(f"Found {len(books)} books")
        
        # Extract data from first book
        if books:
            first_book = books[0]
            
            # Get title
            title_tag = first_book.find('h3').find('a')
            title = scraper.extract_attribute(title_tag, 'title', 'No title')
            
            # Get price
            price_tag = first_book.find('p', class_='price_color')
            price = scraper.extract_text(price_tag, 'N/A')
            
            print(f"First book: {title} - {price}")
```

---

## **Part 10: Common Pitfalls & Solutions**

### **Pitfall 1: Dynamic Classes**
```python
# Some sites generate random class names
# Solution: Use other selectors
<div class="product-a1b2c3">...</div>

# Use attribute contains
products = soup.find_all('div', class_=lambda x: x and 'product' in x)
# OR
products = soup.select('div[class*="product"]')
```

### **Pitfall 2: Nested Elements**
```python
# If you get too many/few elements
# Be specific with your search

# Too broad
soup.find_all('div')

# Better: specify parent-child relationship
soup.select('.container .product-list .item')
```

### **Pitfall 3: Text with Extra Whitespace**
```python
# Raw text might have newlines and spaces
text = element.text  # "\n   Hello World   \n"

# Clean it
clean_text = element.get_text(strip=True)  # "Hello World"
# OR
clean_text = ' '.join(element.text.split())  # "Hello World"
```

---

## **Key Takeaways**

1. **`find()`** for single elements, **`find_all()`** for multiple
2. **`class_`** (with underscore) is used because `class` is a Python keyword
3. **`.get()`** is safer than direct attribute access `['attr']`
4. **CSS selectors** (`select()`) are powerful and readable
5. **Always check** if elements exist before using them
6. **Strip whitespace** from text for clean data

---

## **Homework Exercises**

### **Exercise 1: Practice All Methods**
Create HTML with different elements and practice:
1. `find()` by tag, class, id
2. `find_all()` with different filters
3. `select()` with CSS selectors
4. Extract attributes and text from each

### **Exercise 2: Real Website**
Scrape `https://quotes.toscrape.com/` using:
1. `find_all()` with class names
2. `select()` with CSS selectors
3. Extract quote text, author, and tags separately

### **Exercise 3: Error Handling**
Create a function that safely extracts data even when:
- Tags are missing
- Attributes don't exist
- Elements return None

---

**Next Topic:** We'll dive into **Topic 6: Extracting Data - Tags, Classes, IDs, and Attributes** with more complex examples and real-world patterns.

**Ready to continue?**

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Selectolax/Selectolax Codes|Selectolax Codes]]
- [[Data Engineering Role Notes/Web Scraping/Selenium/Selenium Notes|Selenium WebDriver - Practical Essentials]]
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]]
