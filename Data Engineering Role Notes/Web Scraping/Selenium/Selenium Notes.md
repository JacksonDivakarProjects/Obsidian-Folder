# Selenium WebDriver - Practical Essentials**

## **1. What is Selenium?**

**Definition:** Selenium is a tool that controls a **real web browser** (like Chrome) programmatically. It can click buttons, type text, scroll pages - everything a human can do.

**When to use it:** 
- Websites that load content with **JavaScript** (React, Angular, Single Page Apps)
- Pages that require **login**
- Sites with **infinite scroll** (like social media)
- When you need to **interact** with the page (click buttons, fill forms)

---

## **2. Installation (Simplest Method)**

**Step 1:** Install packages
```bash
pip install selenium webdriver-manager
```

**Step 2:** Basic setup code
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# This automatically downloads the correct ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

**What's happening:** `webdriver-manager` automatically downloads the ChromeDriver (the bridge between Python and Chrome) so you don't have to manually install it.

---

## **3. Finding Elements (The Core of Selenium)**

### **Definition:** Elements are HTML tags (buttons, inputs, divs) on a webpage. To interact with them, you first need to "find" them.

### **Three Most Useful Ways:**

#### **A. By CSS Selector (Most Versatile)**
```python
from selenium.webdriver.common.by import By

# Find by class name
login_btn = driver.find_element(By.CSS_SELECTOR, ".login-button")

# Find by ID
search_box = driver.find_element(By.CSS_SELECTOR, "#search-input")

# Find by attribute
download_link = driver.find_element(By.CSS_SELECTOR, "a[href='/download']")

# Find nested element
product_title = driver.find_element(By.CSS_SELECTOR, "div.product h2.title")
```

**Why CSS Selectors:** They're powerful and work like CSS styling rules. `.class` for classes, `#id` for IDs, `tag` for tags.

#### **B. By ID (Fastest When Available)**
```python
# Simple and direct
email_field = driver.find_element(By.ID, "email")
password_field = driver.find_element(By.ID, "password")
```

**Why ID:** IDs are unique on a page, so finding by ID is fast and reliable.

#### **C. By XPath (When CSS Can't Do It)**
```python
# Find button with exact text
submit_btn = driver.find_element(By.XPATH, "//button[text()='Submit']")

# Find element containing text
link = driver.find_element(By.XPATH, "//a[contains(text(), 'Download')]")
```

**Why XPath:** Can find elements by their text content, which CSS selectors can't do.

---

## **4. Waiting for Elements (CRITICAL!)**

### **Definition:** Modern websites load content dynamically. Elements might not exist immediately when page loads. **Waits** make Selenium pause until elements are ready.

### **The Most Important Wait:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a wait object (10 second max wait)
wait = WebDriverWait(driver, 10)

# Wait for element to exist in page
element = wait.until(
    EC.presence_of_element_located((By.ID, "dynamic-content"))
)

# Wait for element to be clickable (exists AND visible)
button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".submit-btn"))
)
```

**What's happening:** Selenium checks every 0.5 seconds for up to 10 seconds. If element appears, it continues. If not, it raises an error after 10 seconds.

**Without waits:** You'll get errors like "element not found" because the page is still loading.

---

## **5. Interacting with Elements**

### **A. Clicking (For buttons, links, checkboxes)**
```python
# Click any clickable element
login_button.click()
checkbox.click()
link.click()
```

### **B. Typing Text (For input fields, textareas)**
```python
# Type into input field
search_box.send_keys("python tutorial")

# Clear existing text and type new
email_field.clear()
email_field.send_keys("user@example.com")

# Press special keys (Enter, Tab, etc.)
from selenium.webdriver.common.keys import Keys
search_box.send_keys(Keys.ENTER)  # Press Enter key
search_box.send_keys(Keys.TAB)    # Press Tab key
```

### **C. Getting Data (Extracting information)**
```python
# Get visible text inside element
title = element.text  # Returns "Hello World"

# Get attribute value
url = link.get_attribute("href")  # Returns "https://example.com"
image_url = img.get_attribute("src")

# Check if element has certain state
if checkbox.is_selected():
    print("Checkbox is checked")
if button.is_enabled():
    print("Button is clickable")
```

---

## **6. Scrolling (For Infinite Scroll/Lazy Loading)**

### **Definition:** Some websites load content as you scroll down (like Facebook, Twitter). We need to simulate scrolling.

```python
# Scroll to bottom of page (triggers loading)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Scroll to specific element
element = driver.find_element(By.ID, "footer")
driver.execute_script("arguments[0].scrollIntoView();", element)

# Scroll a fixed amount (500 pixels down)
driver.execute_script("window.scrollBy(0, 500);")
```

**What `execute_script` does:** Runs JavaScript code in the browser. We use it to control scrolling.

---

## **7. Screenshots (For Debugging/Evidence)**

```python
# Take screenshot of entire page
driver.save_screenshot("page.png")

# Take screenshot of specific element
element.screenshot("button.png")
```

**When to use:** 
- To debug what the page looks like when your code runs
- To save evidence of what you scraped
- To capture error states

---

## **Complete Practical Example: Login & Scrape**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. SETUP: Launch Chrome browser
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

try:
    # 2. NAVIGATE: Go to website
    driver.get("https://quotes.toscrape.com/login")
    
    # 3. LOGIN: Find fields and enter credentials
    username = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password = driver.find_element(By.ID, "password")
    
    username.send_keys("admin")
    password.send_keys("password")
    
    # Click login button
    login_button = driver.find_element(By.CSS_SELECTOR, "input[value='Login']")
    login_button.click()
    
    # 4. WAIT: Let login process complete
    time.sleep(2)  # Simple wait (not ideal but works)
    
    # 5. SCROLL: Load all content (if lazy loaded)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # Wait for new content to load
    
    # 6. SCRAPE: Find all quotes and extract data
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    
    print(f"Found {len(quotes)} quotes:")
    print("-" * 50)
    
    for quote in quotes:
        text = quote.find_element(By.CSS_SELECTOR, ".text").text
        author = quote.find_element(By.CSS_SELECTOR, ".author").text
        print(f'"{text}"')
        print(f"  — {author}")
        print()
    
    # 7. CAPTURE: Save screenshot as proof
    driver.save_screenshot("scraped_quotes.png")
    print("Screenshot saved as 'scraped_quotes.png'")
    
finally:
    # 8. CLEANUP: Always close the browser
    driver.quit()
    print("Browser closed")
```

---

## **Common Errors & Solutions**

### **Error:** "No such element found"
**Cause:** Element doesn't exist yet (page still loading)
**Solution:** Add wait before finding element
```python
# WRONG (might fail)
element = driver.find_element(By.ID, "dynamic-element")

# RIGHT (waits for element)
element = wait.until(EC.presence_of_element_located((By.ID, "dynamic-element")))
```

### **Error:** "Element not clickable"
**Cause:** Element exists but is hidden or covered
**Solution:** Wait for it to be clickable OR scroll to it
```python
# Wait until clickable
button = wait.until(EC.element_to_be_clickable((By.ID, "button")))

# OR scroll to element first
driver.execute_script("arguments[0].scrollIntoView();", element)
element.click()
```

### **Error:** "Stale element reference"
**Cause:** Page changed after you found the element
**Solution:** Find the element again when needed
```python
# Store selector, not element object
selector = (By.ID, "dynamic-element")

# When needed, find it fresh
element = driver.find_element(*selector)
```

---

## **Quick Decision Guide**

### **When to Use Which Finder:**

| Situation | Best Method | Example |
|-----------|-------------|---------|
| Element has ID | `By.ID` | `find_element(By.ID, "search")` |
| Element has class | `By.CSS_SELECTOR` | `find_element(By.CSS_SELECTOR, ".button")` |
| Find by text | `By.XPATH` | `find_element(By.XPATH, "//button[text()='Submit']")` |
| Find multiple | `find_elements` (plural) | `find_elements(By.CLASS_NAME, "product")` |

### **Essential Wait Patterns:**

```python
# Always start with this for new pages
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# For interactive elements (buttons, links)
wait.until(EC.element_to_be_clickable(locator))

# For form inputs
wait.until(EC.presence_of_element_located(locator))
```

---

## **The 5-Step Selenium Workflow:**

1. **Setup** - Launch browser with webdriver-manager
2. **Navigate** - Go to URL with `driver.get()`
3. **Wait** - Use `WebDriverWait` for dynamic content
4. **Find & Interact** - Locate elements and click/type
5. **Extract** - Get text/attributes from elements

**Remember:** Selenium is slow (runs real browser) but powerful. Use it only when BeautifulSoup can't handle the website.

---

**Next:** We'll build a complete project combining BeautifulSoup (for simple sites) and Selenium (for complex sites).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup Notes|BeautifulSoup Installation & Core Syntax]]
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]]
