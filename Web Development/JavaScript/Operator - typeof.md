***

### **4. The `typeof` Operator**

The `typeof` operator is used to determine the data type of a variable or a value. It returns a string indicating the type.

#### **Syntax**
```javascript
typeof variable;
typeof(value);
```
Both syntaxes are valid and functionally identical.

#### **Return Values and Examples**

| Type | `typeof` Return Value | Example |
| :--- | :--- | :--- |
| **Number** | `"number"` | `typeof 42; // "number"` |
| **String** | `"string"` | `typeof "Hello"; // "string"` |
| **Boolean** | `"boolean"` | `typeof true; // "boolean"` |
| **Undefined** | `"undefined"` | `typeof undefinedVar; // "undefined"` |
| **Null** | `"object"` **(!)** | `typeof null; // "object"` |
| **Function** | `"function"` | `typeof function() {}; // "function"` |
| **Object (General)** | `"object"` | `typeof {name: "John"}; // "object"` |
| **Array** | `"object"` **(!)** | `typeof [1, 2, 3]; // "object"` |
| **Symbol** | `"symbol"` | `typeof Symbol('id'); // "symbol"` |
| **BigInt** | `"bigint"` | `typeof 9007199254740991n; // "bigint"` |

#### **Important Notes & Quirks**
*   **The `null` Quirk:** `typeof null` returns `"object"`. This is a known and long-standing bug in JavaScript that cannot be fixed without breaking existing code. To check for `null`, use strict equality: `variable === null`.
*   **Arrays are Objects:** Since arrays are a type of object, `typeof` cannot distinguish between a plain object, an array, or `null`. To check for an array, use `Array.isArray()`.
    ```javascript
    let arr = [1, 2, 3];
    console.log(Array.isArray(arr)); // true
    ```
*   **`undefined` vs. `ReferenceError`:** `typeof` is a safe operation. It returns `"undefined"` for variables that have been declared but not assigned a value, and it will **not** throw a `ReferenceError` for undeclared variables.
    ```javascript
    let declaredButUndefined;
    console.log(typeof declaredButUndefined); // "undefined"
    console.log(typeof neverDeclared);        // "undefined" (no error)
    ```

**Primary Use Case:** `typeof` is most commonly used for **type checking** to ensure a function or operation receives the correct kind of data, or to handle different data types in conditional logic.

---

**I have created the notes for Topic 4. Please say "Next" for me to proceed to Topic 5 (Datatypes in JS).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Datatypes in JavaScript|Data Types in JavaScript]]
- [[Web Development/JavaScript/Equality Operator|Equality Operators]]
