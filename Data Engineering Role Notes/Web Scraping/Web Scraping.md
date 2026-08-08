# Web Scraping

Web scraping is programmatically extracting data from web pages instead of copying it by hand. The general pipeline is always: fetch a page's HTML (via an HTTP request or by driving a real browser), parse that HTML into a navigable structure, then locate and pull out the specific pieces of data you need (text, links, attributes).

## Choosing a Tool

| Tool | Best For | Speed | Runs JavaScript? |
|------|----------|-------|-------------------|
| **BeautifulSoup** | General-purpose parsing of static HTML | Moderate | No |
| **Selectolax** | Static HTML at scale, when parsing speed matters | Fast (C-based parser) | No |
| **Selenium** | JS-rendered pages, logins, clicks, infinite scroll | Slow (drives a real browser) | Yes |

**Rule of thumb:** start with `requests` + BeautifulSoup (or Selectolax if raw parsing speed matters). Only reach for Selenium when the data you need isn't present in the raw HTML response — i.e. it's rendered by JavaScript after the page loads, or getting to it requires interaction such as logging in, clicking "load more", or scrolling. It's also common to combine tools: use Selenium to get past a JS/login barrier, then hand the resulting `page_source` to BeautifulSoup or Selectolax for fast parsing.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup|Beautiful Soup]]
- [[Data Engineering Role Notes/Web Scraping/Selenium/Selenium|Selenium]]
- [[Data Engineering Role Notes/Web Scraping/Selectolax/Selectolax Codes|Selectolax Codes]]

## 🗺️ Map of Content (auto-generated)

### Beautiful Soup
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup|Beautiful Soup]] - Stub note linking to the full BeautifulSoup reference.
- [[Data Engineering Role Notes/Web Scraping/Beautiful Soup/Beautiful Soup Notes|BeautifulSoup Installation & Core Syntax]] - Installation, parser choice, find/find_all, CSS selectors, and a complete scraper template.

### Selectolax
- [[Data Engineering Role Notes/Web Scraping/Selectolax/Selectolax Codes|Selectolax Codes]] - Installing Selectolax and using its HTMLParser/CSS selectors as a fast alternative to BeautifulSoup.

### Selenium
- [[Data Engineering Role Notes/Web Scraping/Selenium/Selenium|Selenium]] - Stub note linking to the full Selenium reference.
- [[Data Engineering Role Notes/Web Scraping/Selenium/Selenium Notes|Selenium WebDriver - Practical Essentials]] - Browser automation for JS-heavy sites: finding elements, waits, interactions, scrolling, and a login-and-scrape example.
