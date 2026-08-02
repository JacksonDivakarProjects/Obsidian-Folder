***

### **2. Equality Operators**

Equality operators are used to compare two values. JavaScript has two main types: **Strict** and **Loose** equality.

#### **A. Strict Equality (`===` and `!==`)**
*   **Description:** Compares **both the value and the data type**. This is the recommended and safer way to check for equality.
*   **Behavior:** No type conversion is performed. If the types are different, it immediately returns `false`.
*   **Examples:**
    ```javascript
    console.log(5 === 5);    // true (same value, same type: number)
    console.log(5 === '5');  // false (same value, different type: number vs string)
    console.log(0 === false); // false (different types: number vs boolean)
    console.log(null === undefined); // false (different types)
    console.log(5 !== '5');  // true (strictly not equal)
    ```

#### **B. Loose Equality (`==` and `!=`)**
*   **Description:** Compares **only the value after performing type coercion**. This means it will try to convert the values to the same type before making the comparison.
*   **Behavior:** Can lead to unexpected and confusing results. Its use is generally discouraged.
*   **Examples (showing potential pitfalls):**
    ```javascript
    console.log(5 == 5);     // true
    console.log(5 == '5');   // true (string '5' is converted to number 5)
    console.log(0 == false); // true (boolean false is converted to number 0)
    console.log(null == undefined); // true (this is a special rule)
    console.log('' == false); // true (both are "falsy" and get coerced to 0)
    ```

**Key Takeaway:** **Always use Strict Equality (`===` and `!==`)** to avoid bugs caused by JavaScript's implicit type coercion.

---

**I have created the notes for Topic 2. Please say "Next" for me to proceed to Topic 3 (String Operations).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Operator - typeof|The typeof Operator]]
- [[Web Development/JavaScript/Datatypes in JavaScript|Data Types in JavaScript]]
- [[Web Development/JavaScript/Difference Between `var`, `let`, and `const`|Difference Between var, let, and const]]
