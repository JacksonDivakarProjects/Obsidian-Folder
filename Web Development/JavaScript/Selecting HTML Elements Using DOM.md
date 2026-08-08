***

### **9. Selecting HTML Elements Using the DOM (Adjusted)**

To manipulate an element on a page, you must first **select** it. The DOM provides several methods on the `document` object to find and retrieve elements.

#### **A. Selecting a Single Element**

1.  **`document.getElementById("id")`**
    *   **Description:** Selects a **single element** by its unique `id` attribute.
    *   **Returns:** The matching **Element Node** or `null` if not found.
    *   **Example:**
        ```html
        <h1 id="main-title">Hello World</h1>
        ```
        ```javascript
        let titleElement = document.getElementById("main-title");
        console.log(titleElement); // The <h1> element
        ```

2.  **`document.querySelector("css-selector")`**
    *   **Description:** Selects the **first single element** that matches a specified CSS selector (e.g., `#id`, `.class`, `tag`, `tag[attribute]`).
    *   **Returns:** The first matching **Element Node** or `null`.
    *   **Example:**
        ```html
        <p class="text">First paragraph.</p>
        <p class="text">Second paragraph.</p>
        ```
        ```javascript
        let firstParagraph = document.querySelector(".text"); // Selects the FIRST .text element
        let specificLink = document.querySelector("a[target='_blank']"); // Selects first <a> with target="_blank"
        ```

#### **B. Selecting Multiple Elements (HTMLCollection/NodeList)**

1.  **`document.getElementsByClassName("class")`**
    *   **Description:** Selects **all elements** that have the specified class name.
    *   **Returns:** A live **HTMLCollection** (an array-like object) of found elements.
    *   **Example:**
        ```html
        <div class="item">Item 1</div>
        <div class="item">Item 2</div>
        ```
        ```javascript
        let items = document.getElementsByClassName("item");
        console.log(items[0]); // The first div with class "item"
        console.log(items.length); // 2
        ```

2.  **`document.getElementsByTagName("tag")`**
    *   **Description:** Selects **all elements** with the specified tag name (e.g., `"div"`, `"p"`, `"li"`).
    *   **Returns:** A live **HTMLCollection** of found elements.
    *   **Example:**
        ```javascript
        let allParagraphs = document.getElementsByTagName("p");
        ```

3.  **`document.querySelectorAll("css-selector")`**
    *   **Description:** Selects **all elements** that match the specified CSS selector.
    *   **Returns:** A **static NodeList** (an array-like object) of found elements. This is the most powerful and versatile method.
    *   **Example:**
        ```html
        <ul id="list">
          <li>First</li>
          <li class="special">Second</li>
          <li>Third</li>
        </ul>
        ```
        ```javascript
        let allListItems = document.querySelectorAll("#list li"); // All <li> inside #list
        let specialItems = document.querySelectorAll(".special"); // All elements with class "special"
        ```

#### **C. DOM Traversal Properties (NEW)**
Once you have selected an element, you can navigate to related elements using these properties:

1.  **Navigating to Children:**
    *   **`parentElement.firstElementChild`**: Selects the **first child element** (ignores text nodes).
    *   **`parentElement.lastElementChild`**: Selects the **last child element** (ignores text nodes).
    *   **`parentElement.children`**: Returns an **HTMLCollection** of all child elements.

    **Example:**
    ```html
    <ul id="myList">
      <li>First item</li>
      <li>Second item</li>
      <li>Third item</li>
    </ul>
    ```
    ```javascript
    let list = document.getElementById("myList");
    console.log(list.firstElementChild.textContent); // "First item"
    console.log(list.lastElementChild.textContent);  // "Third item"
    console.log(list.children[1].textContent);       // "Second item"
    ```

2.  **Navigating to Siblings:**
    *   **`element.previousElementSibling`**: Selects the **previous sibling element**.
    *   **`element.nextElementSibling`**: Selects the **next sibling element**.

    **Example:**
    ```html
    <div>First</div>
    <div id="middle">Middle</div>
    <div>Last</div>
    ```
    ```javascript
    let middle = document.getElementById("middle");
    console.log(middle.previousElementSibling.textContent); // "First"
    console.log(middle.nextElementSibling.textContent);     // "Last"
    ```

3.  **Navigating to Parent:**
    *   **`element.parentElement`**: Selects the **direct parent element**.

#### **Key Differences & Best Practice**

| Method | Selects By | Returns | Live/Static |
| :--- | :--- | :--- | :--- |
| `getElementById` | `id` | Single Element | - |
| `querySelector` | CSS Selector | Single Element | - |
| `getElementsByClassName` | `class` | **HTMLCollection** | **Live** (updates automatically) |
| `getElementsByTagName` | Tag Name | **HTMLCollection** | **Live** |
| `querySelectorAll` | CSS Selector | **NodeList** | **Static** (snapshot when called) |

**Best Practice:** For modern development, **`querySelector` and `querySelectorAll`** are the most commonly used and flexible methods because they leverage the power of CSS selectors you already know. Use traversal properties when you need to navigate the DOM tree from a reference point.

---

**I have adjusted the notes for Topic 9 to include DOM traversal properties. Please say "Next" for me to proceed to Topic 10 (Manipulating elements using DOM).**

## 🔗 Related Notes
- [[Web Development/JavaScript/DOM (Document Object Model)|DOM (Document Object Model)]]
- [[Web Development/JavaScript/Manipulating Elements Using DOM|Manipulating Elements Using DOM - Camel Case for Properties]]
- [[Web Development/JavaScript/Structure of HTML Elements in DOM Tree|Tree Structure of HTML Elements (DOM Tree)]]
