***

### **3. String Operations**

Strings are sequences of characters used to represent text. JavaScript provides many built-in methods and properties to manipulate them.

#### **A. String Length**
*   **Description:** The `.length` property returns the number of characters in a string.
*   **Example:**
    ```javascript
    let greeting = "Hello, World!";
    console.log(greeting.length); // 13
    ```

#### **B. Accessing Characters**
*   **Description:** You can access individual characters using **bracket notation** `[]` with a zero-based index.
*   **Example:**
    ```javascript
    let str = "JavaScript";
    console.log(str[0]); // "J"
    console.log(str[4]); // "S"
    ```

#### **C. Common String Methods**
Strings are immutable (they cannot be changed directly). These methods return a **new string**.

*   **`toUpperCase()` & `toLowerCase()`**: Change the case of the string.
    ```javascript
    let word = "Hello";
    console.log(word.toUpperCase()); // "HELLO"
    console.log(word.toLowerCase()); // "hello"
    ```

*   **`trim()`**: Removes whitespace from both ends of a string.
    ```javascript
    let input = "   user input    ";
    console.log(input.trim()); // "user input"
    ```

*   **`includes(substring)`**: Checks if a string contains a specified substring. Returns `true` or `false`.
    ```javascript
    let sentence = "The quick brown fox";
    console.log(sentence.includes("brown")); // true
    console.log(sentence.includes("red"));   // false
    ```

*   **`indexOf(substring)`**: Returns the index of the first occurrence of a specified substring. Returns `-1` if not found.
    ```javascript
    let data = "Hello World";
    console.log(data.indexOf("World")); // 6
    console.log(data.indexOf("Universe")); // -1
    ```

*   **`slice(start, end)`**: Extracts a section of a string and returns it as a new string. The `end` index is not included.
    ```javascript
    let str = "JavaScript";
    console.log(str.slice(0, 4)); // "Java"
    console.log(str.slice(4));    // "Script" (from index 4 to the end)
    ```

*   **`replace(old, new)`**: Replaces the first occurrence of a specified value with another value.
    ```javascript
    let msg = "I love cats. Cats are great!";
    console.log(msg.replace("cats", "dogs")); // "I love dogs. Cats are great!"
    ```

#### **D. String Concatenation**
*   **Description:** Combining strings. This can be done with the `+` operator or **template literals** (preferred).
*   **Examples:**
    ```javascript
    // Using the + operator
    let name = "Jane";
    let greeting = "Hello, " + name + "!";

    // Using Template Literals (backticks ``)
    let modernGreeting = `Hello, ${name}!`; // Much cleaner and more powerful
    console.log(modernGreeting); // "Hello, Jane!"
    ```

---

**I have created the notes for Topic 3. Please say "Next" for me to proceed to Topic 4 (typeof()).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Array Operations|Arrays - Push and Pull Operations]]
- [[Web Development/JavaScript/Datatypes in JavaScript|Data Types in JavaScript]]
