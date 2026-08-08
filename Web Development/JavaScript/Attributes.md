***

### **15. Attributes - attributes, getAttribute(), setAttribute()**

#### **A. `attributes` Property**
*   **Returns:** NamedNodeMap object containing all attributes

**Input HTML:**
```html
<div id="main" class="container" data-code="ABC">Test</div>
```

**JavaScript:**
```javascript
let div = document.getElementById('main');

console.log(div.attributes);
// OUTPUT: NamedNodeMap {0: id, 1: class, 2: data-code, length: 3}

console.log(div.attributes[0].name);  // OUTPUT: "id"
console.log(div.attributes[0].value); // OUTPUT: "main"
console.log(div.attributes.length);   // OUTPUT: 3
```

#### **B. `getAttribute(attrName)`**
*   **Returns:** String value or null

**Input HTML:**
```html
<input type="text" id="username" value="john" data-role="admin" required>
```

**JavaScript:**
```javascript
let input = document.getElementById('username');

console.log(input.getAttribute('type'));      // OUTPUT: "text"
console.log(input.getAttribute('value'));     // OUTPUT: "john"
console.log(input.getAttribute('data-role')); // OUTPUT: "admin"
console.log(input.getAttribute('required'));  // OUTPUT: "" (empty string)
console.log(input.getAttribute('invalid'));   // OUTPUT: null
```

#### **C. `setAttribute(attrName, value)`**
*   **Action:** Sets or modifies attributes

**Input HTML:**
```html
<img id="logo" src="old.jpg">
```

**JavaScript:**
```javascript
let img = document.getElementById('logo');

img.setAttribute('src', 'new.jpg');
img.setAttribute('alt', 'Company Logo');
img.setAttribute('data-loaded', 'true');

console.log(img.getAttribute('src'));  // OUTPUT: "new.jpg"
console.log(img.getAttribute('alt'));  // OUTPUT: "Company Logo"
```

#### **D. Direct Property Access (GET)**
*   **For:** Common standard attributes

**Input HTML:**
```html
<a id="link" href="/page" class="btn" title="Click me">Link</a>
```

**JavaScript:**
```javascript
let link = document.getElementById('link');

console.log(link.id);        // OUTPUT: "link"
console.log(link.href);      // OUTPUT: "http://localhost/page" (full URL)
console.log(link.className); // OUTPUT: "btn"
console.log(link.title);     // OUTPUT: "Click me"
```

#### **E. Direct Property Access (SET)**
*   **For:** Modifying common attributes directly

**Input HTML:**
```html
<div id="content">Hello</div>
```

**JavaScript:**
```javascript
let div = document.getElementById('content');

// Set properties directly
div.id = "new-content";
div.className = "highlight";
div.title = "Updated div";

console.log(div.id);        // OUTPUT: "new-content"
console.log(div.className); // OUTPUT: "highlight"
console.log(div.title);     // OUTPUT: "Updated div"
```

#### **F. Comparison: Direct vs getAttribute()**

**Input HTML:**
```html
<a id="test" href="/products" data-id="P123">Test</a>
```

**JavaScript:**
```javascript
let link = document.getElementById('test');

// href comparison
console.log(link.href);                  // OUTPUT: "http://localhost/products"
console.log(link.getAttribute('href'));  // OUTPUT: "/products"

// data attribute comparison
console.log(link.dataset.id);            // OUTPUT: "P123"
console.log(link.getAttribute('data-id')); // OUTPUT: "P123"

// Direct property for non-standard attribute
console.log(link.getAttribute('data-id')); // OUTPUT: "P123"
// link.data-id = "P456" // ❌ This would cause error
```

#### **G. Quick Reference Table**

| Method | Purpose | Example Input | Example Output |
|--------|---------|---------------|----------------|
| `element.attributes` | Get all attributes | `div.attributes` | `NamedNodeMap {0: id, 1: class...}` |
| `getAttribute(name)` | Get specific attribute | `input.getAttribute('type')` | `"text"` |
| `setAttribute(name, value)` | Set attribute | `img.setAttribute('src', 'new.jpg')` | (modifies element) |
| `element.property` | Direct get access | `link.href` | `"http://localhost/page"` |
| `element.property = value` | Direct set access | `div.id = "new"` | (modifies element) |

**Best Practice:**
- Use direct properties (`element.id`, `element.className`) for standard attributes
- Use `getAttribute()`/`setAttribute()` for custom data attributes
- Use `attributes` when you need to work with all attributes

---

**I have created concise notes with direct outputs. Please say "Next" for me to proceed to Topic 16.**

## 🔗 Related Notes
- [[Web Development/JavaScript/Manipulating Elements Using DOM|Manipulating Elements Using DOM - Camel Case for Properties]]
- [[Web Development/JavaScript/Selecting HTML Elements Using DOM|Selecting HTML Elements Using the DOM]]
- [[Web Development/JavaScript/Difference Between innerHTML and textContent|Difference Between innerHTML and textContent]]
