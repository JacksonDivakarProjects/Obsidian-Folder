***

### **10. Manipulating Elements Using DOM - Camel Case for Properties**

Once you have selected an element, you can manipulate its content, style, and attributes. JavaScript uses **camelCase** versions of CSS property names for style manipulation.

#### **A. Manipulating Content**

1.  **`textContent`**
    *   **Gets or sets** the **plain text** content of an element and all its descendants.
    *   **Ignores** any HTML tags and returns only the text.
    *   **Example:**
        ```html
        <div id="myDiv">This is <strong>important</strong> text.</div>
        ```
        ```javascript
        let div = document.getElementById("myDiv");
        console.log(div.textContent); // "This is important text."
        div.textContent = "New plain text content"; // HTML tags are not parsed
        ```

2.  **`innerHTML`**
    *   **Gets or sets** the HTML content **including tags**.
    *   **Parses** any HTML string and renders it as actual elements.
    *   **Example:**
        ```javascript
        let div = document.getElementById("myDiv");
        console.log(div.innerHTML); // "This is <strong>important</strong> text."
        div.innerHTML = "New <em>formatted</em> content"; // HTML is parsed and rendered
        ```

#### **B. Manipulating Styles (Using Camel Case)**

*   **Description:** To change CSS styles, use the `style` property followed by the camelCase version of the CSS property name.
*   **Conversion Rule:** Remove hyphens and capitalize the first letter of each subsequent word.
*   **Syntax:** `element.style.cssProperty = "value";`

**CSS to JavaScript Examples:**

| CSS Property | JavaScript `style` Property |
| :--- | :--- |
| `background-color` | `backgroundColor` |
| `font-size` | `fontSize` |
| `display` | `display` |
| `border-radius` | `borderRadius` |
| `z-index` | `zIndex` |

**Example:**
```javascript
let title = document.getElementById("main-title");
title.style.color = "blue";
title.style.backgroundColor = "yellow"; // Note: camelCase for background-color
title.style.fontSize = "24px";
title.style.padding = "10px";
```

#### **C. Manipulating Attributes**

1.  **Direct Property Access:**
    *   For common attributes like `id`, `title`, `src`, `href`, you can often access them directly as properties.
    *   **Example:**
        ```javascript
        let link = document.querySelector("a");
        console.log(link.href); // Gets the href
        link.id = "new-link"; // Sets the id
        ```

2.  **`getAttribute()` and `setAttribute()`:**
    *   More versatile methods that work for any attribute, including custom ones.
    *   **`element.getAttribute("attr-name")`**: Gets the value of an attribute.
    *   **`element.setAttribute("attr-name", "value")`**: Sets the value of an attribute.
    *   **Example:**
        ```javascript
        let image = document.querySelector("img");
        let src = image.getAttribute("src"); // Get the src
        image.setAttribute("alt", "A beautiful landscape"); // Set the alt text
        image.setAttribute("data-custom", "info"); // Set a custom data attribute
        ```

**Key Takeaway:** Use **camelCase** for style properties and be mindful of the difference between `textContent` (text only) and `innerHTML` (parses HTML).

---

**I have created the notes for Topic 10. Please say "Next" for me to proceed to Topic 11 (DOM classList).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Selecting HTML Elements Using DOM|Selecting HTML Elements Using the DOM]]
- [[Web Development/JavaScript/DOM classList|DOM classList]]
- [[Web Development/JavaScript/Attributes|Attributes - attributes, getAttribute(), setAttribute()]]
- [[Web Development/JavaScript/Difference Between innerHTML and textContent|Difference Between innerHTML and textContent]]
