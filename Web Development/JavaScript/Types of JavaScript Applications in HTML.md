Of course. Here are the comprehensive notes for the first topic you provided.

***

### **1. Types of JavaScript Applications in HTML**

JavaScript code can be included in an HTML document in three primary ways, allowing for dynamic behavior and interactivity.

#### **A. Inline JavaScript (Using Event Attributes)**
*   **Description:** JavaScript code is placed directly inside HTML **event attributes** like `onclick`, `onmouseover`, `onload`, etc.
*   **Use Case:** Best for very small, simple actions specific to a single HTML element.
*   **Example:**
    ```html
    <button onclick="alert('Button was clicked!')">Click Me</button>
    ```

#### **B. Internal JavaScript (Using the `<script>` Tag)**
*   **Description:** JavaScript code is written within a `<script>` tag placed inside the HTML file, typically in the `<head>` or at the end of the `<body>`.
*   **Use Case:** Suitable for scripts that are specific to a single page.
*   **Example:**
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <script>
            function greet() {
                document.getElementById('msg').innerHTML = "Hello from Internal JS!";
            }
        </script>
    </head>
    <body>
        <p id="msg"></p>
        <button onclick="greet()">Greet</button>
    </body>
    </html>
    ```

#### **C. External JavaScript (Using a `.js` File)**
*   **Description:** JavaScript code is written in a separate file with a `.js` extension. This file is then linked to the HTML document using the `<script>` tag with a `src` (source) attribute.
*   **Use Case:** The **most preferred and professional method**. It promotes separation of concerns, code reusability across multiple pages, and better cache management.
*   **Example:**
    *   **File: `script.js`**
        ```javascript
        function showTime() {
            document.getElementById('time').innerHTML = new Date().toLocaleTimeString();
        }
        ```
    *   **File: `index.html`**
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <script src="script.js"></script>
        </head>
        <body>
            <p id="time"></p>
            <button onclick="showTime()">Show Time</button>
        </body>
        </html>
        ```

**Best Practice:** For production-level code, **External JavaScript** is strongly recommended.

---

**I have created the notes for Topic 1. Please say "Next" for me to proceed to Topic 2 (Equality Operators), or "Adjust" if you would like me to refine this topic.**

## 🔗 Related Notes
- [[Web Development/JavaScript/DOM (Document Object Model)|DOM (Document Object Model)]]
- [[Web Development/JavaScript/Event Listeners|Event Listeners in JavaScript]]
