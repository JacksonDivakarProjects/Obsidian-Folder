***

### **14. Difference Between `innerHTML` and `textContent`**

Both `innerHTML` and `textContent` are used to work with element content, but they behave very differently in how they handle and interpret that content.

#### **A. `textContent`**

*   **Description:** Gets or sets the **plain text** content of an element and all its descendants.
*   **HTML Handling:** **Ignores** HTML tags and treats them as text. Any HTML in the string will be displayed as literal characters.
*   **Performance:** Generally faster because it doesn't need to parse HTML.
*   **Security:** Safer - prevents accidental injection of HTML and protects against XSS attacks.

**Example:**
```html
<div id="example">
  This is <strong>important</strong> text.
  <script>console.log('This script wont run with textContent')</script>
</div>
```

```javascript
let div = document.getElementById("example");

// GETTING content
console.log(div.textContent); 
// Output: "This is important text. console.log('This script wont run with textContent')"

// SETTING content
div.textContent = 'New <em>text</em> with <strong>HTML tags</strong>';
// Result: The text will display exactly as written: "New <em>text</em> with <strong>HTML tags</strong>"
```

#### **B. `innerHTML`**

*   **Description:** Gets or sets the **HTML content** of an element, including all tags.
*   **HTML Handling:** **Parses and renders** HTML tags as actual elements.
*   **Performance:** Slower because it triggers HTML parsing and DOM updates.
*   **Security:** **Dangerous** if used with untrusted input - can lead to XSS vulnerabilities.

**Example:**
```html
<div id="example">
  This is <strong>important</strong> text.
</div>
```

```javascript
let div = document.getElementById("example");

// GETTING content
console.log(div.innerHTML); 
// Output: "This is <strong>important</strong> text."

// SETTING content
div.innerHTML = 'New <em>emphasized</em> text with <strong>bold</strong> elements';
// Result: The HTML is parsed and rendered with actual formatting
```

#### **C. Key Differences Summary**

| Aspect | `textContent` | `innerHTML` |
|--------|---------------|-------------|
| **Content Type** | Plain text only | HTML markup |
| **HTML Tags** | Treated as literal text | Parsed and rendered |
| **Performance** | Faster | Slower (parses HTML) |
| **Security** | Safe from XSS | Vulnerable to XSS attacks |
| **Whitespace** | Preserves all whitespace | Normalizes whitespace |
| **Script Execution** | Scripts remain as text | Scripts can execute |

#### **D. When to Use Each**

**Use `textContent` when:**
- Working with plain text content
- Setting user input that shouldn't contain HTML
- Performance is important
- Security is a concern

**Use `innerHTML` when:**
- You need to insert actual HTML elements
- Adding complex markup dynamically
- Working with trusted HTML content

#### **E. Security Warning Example**
```javascript
// ❌ DANGEROUS - XSS vulnerability
let userInput = "<script>maliciousCode()</script><img src='x' onerror='stealData()'>";
element.innerHTML = userInput; // Executes the malicious code!

// ✅ SAFE - treats input as text
element.textContent = userInput; // Displays the text literally, no execution
```

**Best Practice:** Prefer `textContent` for plain text manipulation and only use `innerHTML` when you specifically need to work with HTML markup and can guarantee the content is safe.

---

**I have created the notes for Topic 14. Please say "Next" for me to proceed to Topic 15 (Attributes).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Manipulating Elements Using DOM|Manipulating Elements Using DOM - Camel Case for Properties]]
- [[Web Development/JavaScript/Attributes|Attributes - attributes, getAttribute(), setAttribute()]]
