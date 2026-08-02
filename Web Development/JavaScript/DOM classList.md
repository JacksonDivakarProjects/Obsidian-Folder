***

### **11. DOM classList**

The `classList` property is a powerful and modern way to work with the CSS classes of an element. It provides methods to add, remove, toggle, and check for classes in a clean and manageable way.

#### **A. What is classList?**
*   **Description:** `classList` is a read-only property that returns a live **DOMTokenList** collection of the `class` attributes of an element.
*   **Advantage:** Much easier and more flexible than manually working with the `className` property string.

#### **B. Key classList Methods**

1.  **`add(className)`**
    *   **Action:** Adds one or more class names to an element.
    *   **Example:**
        ```javascript
        let div = document.getElementById("myDiv");
        div.classList.add("active");
        div.classList.add("highlight", "border"); // Add multiple classes
        ```

2.  **`remove(className)`**
    *   **Action:** Removes one or more class names from an element.
    *   **Example:**
        ```javascript
        let div = document.getElementById("myDiv");
        div.classList.remove("highlight");
        div.classList.remove("active", "border"); // Remove multiple classes
        ```

3.  **`toggle(className)`**
    *   **Action:**
        *   If the class exists, it **removes** it (returns `false`).
        *   If the class does not exist, it **adds** it (returns `true`).
    *   **Use Case:** Perfect for implementing toggle switches, dark mode, expanding/collapsing sections, etc.
    *   **Example:**
        ```javascript
        let button = document.getElementById("myButton");
        button.addEventListener("click", function() {
            document.body.classList.toggle("dark-mode");
        });
        ```

4.  **`contains(className)`**
    *   **Action:** Checks if an element has a specific class name.
    *   **Returns:** `true` if the element contains the class, `false` if not.
    *   **Use Case:** Conditional logic based on an element's class.
    *   **Example:**
        ```javascript
        let div = document.getElementById("myDiv");
        if (div.classList.contains("warning")) {
            console.log("This is a warning element!");
        }
        ```

5.  **`replace(oldClass, newClass)`**
    *   **Action:** Replaces an existing class with a new class.
    *   **Example:**
        ```javascript
        let div = document.getElementById("myDiv");
        div.classList.replace("old-style", "new-style");
        ```

#### **C. Why Use classList? (Separation of Concerns)**
Using `classList` promotes a clean separation between HTML, CSS, and JavaScript:

*   **HTML:** Defines the structure.
*   **CSS:** Defines all the visual styles for classes like `.active`, `.hidden`, etc.
*   **JavaScript:** Only handles the logic of **when** to add or remove these classes using `classList`.

This is much cleaner than manipulating styles directly with the `style` property in JavaScript.

**Example Comparison:**
```javascript
// ❌ Less maintainable: Mixing style logic in JS
button.style.backgroundColor = "blue";
button.style.color = "white";

// ✅ Better: Using CSS classes and classList
// CSS: .btn-primary { background-color: blue; color: white; }
button.classList.add("btn-primary");
```

---

**I have created the notes for Topic 11. Please say "Next" for me to proceed to Topic 12 (Class List Functions).**

## 🔗 Related Notes
- [[Web Development/JavaScript/classList Functions (add,remove,toggle)|Class List Functions: add, remove, toggle]]
- [[Web Development/JavaScript/Manipulating Elements Using DOM|Manipulating Elements Using DOM - Camel Case for Properties]]
