***

### **5. Data Types in JavaScript**

Data types define the kind of data that can be stored and manipulated in a program. JavaScript is a **dynamically typed** language, meaning a variable can hold a value of any type without being explicitly defined.

Data types are categorized as **Primitive** and **Non-Primitive (Object)** types.

---

#### **A. Primitive Data Types**
Primitives are immutable (cannot be changed directly) and are compared **by value**.

1.  **Number**
    *   Represents both integer and floating-point numbers.
    *   **Example:** `let age = 25;`, `let price = 99.95;`

2.  **String**
    *   Represents a sequence of characters, enclosed in single quotes (`''`), double quotes (`""`), or backticks (`` ` ` ``).
    *   **Example:** `let name = "Alice";`, `let msg = `Hello, ${name}!`;`

3.  **Boolean**
    *   Represents a logical entity and can only be `true` or `false`.
    *   **Example:** `let isLogged = true;`, `let isEmpty = false;`

4.  **Undefined**
    *   A variable that has been declared but has not been assigned a value has the value `undefined`.
    *   **Example:** `let x; console.log(x); // undefined`

5.  **Null**
    *   Represents the intentional absence of any object value. It is a special value that means "nothing", "empty", or "value unknown".
    *   **Example:** `let user = null;`

6.  **Symbol (ES6)**
    *   Represents a unique and immutable identifier. Often used for object property keys to avoid naming collisions.
    *   **Example:** `let id = Symbol("id");`

7.  **BigInt (ES11)**
    *   Represents integers that are too large to be represented by the `Number` type. Created by appending `n` to the end of an integer.
    *   **Example:** `let bigNumber = 9007199254740991n;`

---

#### **B. Non-Primitive (Object) Data Type**
Objects are mutable (can be changed) and are compared **by reference** (two variables are equal only if they point to the exact same object in memory).

*   **Object**
    *   A collection of key-value pairs. Used to store complex data structures.
    *   **Example:**
        ```javascript
        let person = {
          name: "John",
          age: 30,
          isStudent: false
        };
        ```

*   **Special Object Sub-types:**
    *   **Array:** Used to store multiple values in a single variable.
        ```javascript
        let fruits = ["apple", "banana", "orange"];
        ```
    *   **Function:** A callable object that executes a block of code.
        ```javascript
        function greet() {
          console.log("Hello!");
        }
        ```
    *   **Date, RegExp, etc.** are also specialized objects.

---

#### **Key Concept: Dynamic Typing**
In JavaScript, the type is associated with the **value**, not the variable. The same variable can be reassigned to hold different data types.

```javascript
let dynamicVar = 42;        // dynamicVar is a Number
console.log(typeof dynamicVar); // "number"

dynamicVar = "Now I'm a string"; // Now it's a String
console.log(typeof dynamicVar); // "string"

dynamicVar = true;          // Now it's a Boolean
console.log(typeof dynamicVar); // "boolean"
```

---

**I have created the notes for Topic 5. Please say "Next" for me to proceed to Topic 6 (Arrays - Push and Pull Operations).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Operator - typeof|The typeof Operator]]
- [[Web Development/JavaScript/Equality Operator|Equality Operators]]
- [[Web Development/JavaScript/Difference Between `var`, `let`, and `const`|Difference Between var, let, and const]]
