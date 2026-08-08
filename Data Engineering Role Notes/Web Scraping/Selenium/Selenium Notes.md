# Selenium WebDriver: Practical Essentials

## 1. What Is Selenium?

Selenium controls a **real web browser** (like Chrome) programmatically — it can click buttons, type text, scroll, and wait for content, everything a human could do by hand.

**When to reach for it:**
- Websites that load content with **JavaScript** (React, Angular, other single-page apps)
- Pages that require **login**
- Sites with **infinite scroll** (e.g. social media feeds)
- Any workflow that needs to **interact** with the page — clicking buttons, filling forms — rather than just reading static HTML

If BeautifulSoup or Selectolax can already see the data in the raw HTML response, prefer them — they're much faster since they don't launch a browser.

---

## 2. Installation (Simplest Method)

**Step 1: Install packages**
```bash
pip install selenium webdriver-manager
```

**Step 2: Basic setup code**
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# This automatically downloads the correct ChromeDriver version for your installed Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

`webdriver-manager` downloads and manages ChromeDriver — the bridge process between your Python code and the Chrome browser — so you don't have to track driver versions manually.

---

## 3. Finding Elements (The Core of Selenium)

Elements are the HTML tags (buttons, inputs, divs) on a page. To interact with any of them, you first have to locate it.

### A. By CSS Selector (Most Versatile)

```python
from selenium.webdriver.common.by import By

login_btn = driver.find_element(By.CSS_SELECTOR, ".login-button")       # by class
search_box = driver.find_element(By.CSS_SELECTOR, "#search-input")       # by id
download_link = driver.find_element(By.CSS_SELECTOR, "a[href='/download']")  # by attribute
product_title = driver.find_element(By.CSS_SELECTOR, "div.product h2.title")  # nested
```

CSS selectors work like CSS styling rules: `.class`, `#id`, `tag`, and combinations of them.

### B. By ID (Fastest When Available)

```python
email_field = driver.find_element(By.ID, "email")
password_field = driver.find_element(By.ID, "password")
```

IDs are supposed to be unique on a page, so `By.ID` lookups are fast and reliable when the site provides them.

### C. By XPath (When CSS Can't Do It)

```python
# Find a button with exact visible text
submit_btn = driver.find_element(By.XPATH, "//button[text()='Submit']")

# Find an element whose text contains a substring
link = driver.find_element(By.XPATH, "//a[contains(text(), 'Download')]")
```

XPath can match on text content — something plain CSS selectors cannot do.

---

## 4. Waiting for Elements (Critical!)

Modern websites load content dynamically, so an element might not exist the instant the page loads. **Waits** tell Selenium to pause until an element is actually ready, instead of failing immediately.

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a wait object (10 second max wait)
wait = WebDriverWait(driver, 10)

# Wait until the element exists in the DOM
element = wait.until(
    EC.presence_of_element_located((By.ID, "dynamic-content"))
)

# Wait until the element exists AND is visible/interactable
button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".submit-btn"))
)
```

Selenium polls the page (by default about every 0.5 seconds) for up to the timeout you specify. If the element appears in time, execution continues immediately; if not, it raises a `TimeoutException` once the timeout elapses.

**Without waits**, you'll intermittently see "element not found" errors simply because the page hadn't finished loading yet — this is the single most common source of flaky Selenium scripts.

---

## 5. Interacting with Elements

### A. Clicking (buttons, links, checkboxes)

```python
login_button.click()
checkbox.click()
link.click()
```

### B. Typing Text (input fields, textareas)

```python
search_box.send_keys("python tutorial")

# Clear existing text before typing new text
email_field.clear()
email_field.send_keys("user@example.com")

# Press special keys
from selenium.webdriver.common.keys import Keys
search_box.send_keys(Keys.ENTER)
search_box.send_keys(Keys.TAB)
```

### C. Reading Data (extracting information)

```python
title = element.text  # visible text, e.g. "Hello World"

url = link.get_attribute("href")
image_url = img.get_attribute("src")

if checkbox.is_selected():
    print("Checkbox is checked")
if button.is_enabled():
    print("Button is clickable")
```

---

## 6. Scrolling (Infinite Scroll / Lazy Loading)

Some sites load more content as you scroll (e.g. social media feeds), so you need to simulate scrolling to trigger that loading.

```python
# Scroll to the bottom of the page
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Scroll a specific element into view
element = driver.find_element(By.ID, "footer")
driver.execute_script("arguments[0].scrollIntoView();", element)

# Scroll a fixed distance
driver.execute_script("window.scrollBy(0, 500);")
```

`execute_script` runs raw JavaScript inside the browser — this is the general escape hatch for anything Selenium's own API doesn't expose directly, scrolling included.

---

## 7. Screenshots (Debugging / Evidence)

```python
driver.save_screenshot("page.png")     # whole page
element.screenshot("button.png")       # a single element
```

Useful for debugging what a page actually looked like when your script ran, capturing error states, or keeping evidence of what was scraped.

---

## Complete Practical Example: Login & Scrape

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. SETUP: launch Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

try:
    # 2. NAVIGATE
    driver.get("https://quotes.toscrape.com/login")

    # 3. LOGIN: find fields, enter credentials
    username = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password = driver.find_element(By.ID, "password")

    username.send_keys("admin")
    password.send_keys("password")

    login_button = driver.find_element(By.CSS_SELECTOR, "input[value='Login']")
    login_button.click()

    # 4. WAIT for the login to complete
    time.sleep(2)  # a fixed sleep works but an explicit wait on a post-login element is more robust

    # 5. SCROLL to load any lazy content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    # 6. SCRAPE: find all quotes and extract data
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    print(f"Found {len(quotes)} quotes:")
    print("-" * 50)

    for quote in quotes:
        text = quote.find_element(By.CSS_SELECTOR, ".text").text
        author = quote.find_element(By.CSS_SELECTOR, ".author").text
        print(f'"{text}"')
        print(f"  — {author}")
        print()

    # 7. CAPTURE proof
    driver.save_screenshot("scraped_quotes.png")
    print("Screenshot saved as 'scraped_quotes.png'")

finally:
    # 8. CLEANUP: always close the browser, even on error
    driver.quit()
    print("Browser closed")
```

---

## Common Errors & Solutions

### "No such element found"
**Cause:** the element doesn't exist yet — the page is still loading.
**Solution:** wait before finding it.
```python
# Fragile — may fail if page hasn't finished loading
element = driver.find_element(By.ID, "dynamic-element")

# Robust — waits for the element to appear
element = wait.until(EC.presence_of_element_located((By.ID, "dynamic-element")))
```

### "Element not clickable"
**Cause:** the element exists but is hidden, covered, or off-screen.
**Solution:** wait for clickability, or scroll it into view first.
```python
button = wait.until(EC.element_to_be_clickable((By.ID, "button")))
# or
driver.execute_script("arguments[0].scrollIntoView();", element)
element.click()
```

### "Stale element reference"
**Cause:** the page changed (re-rendered/navigated) after you located the element, invalidating your reference to it.
**Solution:** re-locate the element when you need it rather than holding onto old references.
```python
selector = (By.ID, "dynamic-element")
element = driver.find_element(*selector)  # find fresh, right before use
```

---

## Quick Decision Guide

| Situation | Best Locator | Example |
|-----------|--------------|---------|
| Element has an id | `By.ID` | `find_element(By.ID, "search")` |
| Element has a class | `By.CSS_SELECTOR` | `find_element(By.CSS_SELECTOR, ".button")` |
| Need to match by visible text | `By.XPATH` | `find_element(By.XPATH, "//button[text()='Submit']")` |
| Need multiple matches | `find_elements` (plural) | `find_elements(By.CLASS_NAME, "product")` |

### Essential Wait Patterns

```python
# A sensible first wait on any new page
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# For interactive elements (buttons, links)
wait.until(EC.element_to_be_clickable(locator))

# For form inputs
wait.until(EC.presence_of_element_located(locator))
```

---

## The 5-Step Selenium Workflow

1. **Setup** — launch the browser via `webdriver-manager`.
2. **Navigate** — go to a URL with `driver.get()`.
3. **Wait** — use `WebDriverWait` for anything dynamically loaded.
4. **Find & Interact** — locate elements, then click/type/scroll.
5. **Extract** — read text/attributes back out of the elements.

Selenium is slow relative to BeautifulSoup/Selectolax because it drives a real browser, but it's the only option once a page's data depends on JavaScript execution or user interaction. A common pattern is to use Selenium only to get past the JS/interaction barrier — navigate, log in, click "load more", scroll — then hand `driver.page_source` to BeautifulSoup or Selectolax for the actual parsing, since parsing HTML strings is faster in those libraries than querying live DOM elements through Selenium.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup Notes|BeautifulSoup Installation & Core Syntax]]
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]]
