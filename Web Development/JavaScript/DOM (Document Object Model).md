***

### **7. DOM (Document Object Model)**

The DOM is a fundamental concept for web development, acting as a bridge between HTML/CSS and JavaScript.

#### **A. What is the DOM?**
*   **Definition:** The Document Object Model (DOM) is a **programming interface** for web documents. It represents the structure of an HTML or XML document as a **tree of objects**.
*   **Purpose:** It allows programming languages (like JavaScript) to **interact with and manipulate** the content, structure, and style of a webpage dynamically.
*   **Key Idea:** The DOM is **not** the HTML source code. It is a live, in-memory representation of the document that the browser creates after parsing the HTML. When you change the DOM with JavaScript, the browser updates the page accordingly.

#### **B. How the Browser Uses the DOM**
1.  The browser fetches the HTML file.
2.  It **parses** the HTML and constructs the DOM tree.
3.  The browser then uses this DOM tree to **render** the page.
4.  JavaScript can access and modify this DOM tree to change what the user sees without reloading the page.

#### **C. The `document` Object**
*   The `document` object is the entry point to the DOM. It represents the entire web page.
*   It is a property of the global `window` object and is available in any script running in the page.
*   All operations to select, create, or manipulate elements start from the `document` object.

**Example:**
```javascript
// Using the document object to change the page title
document.title = "New Page Title";

// Using it to select an element
let header = document.getElementById("main-header");
```

**In essence, the DOM is the reason JavaScript can make web pages interactive and dynamic.**

---

**I have created the notes for Topic 7. Please say "Next" for me to proceed to Topic 8 (Tree Structure of HTML Elements).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Structure of HTML Elements in DOM Tree|Tree Structure of HTML Elements (DOM Tree)]]
- [[Web Development/JavaScript/Selecting HTML Elements Using DOM|Selecting HTML Elements Using the DOM]]
- [[Web Development/JavaScript/Manipulating Elements Using DOM|Manipulating Elements Using DOM - Camel Case for Properties]]
