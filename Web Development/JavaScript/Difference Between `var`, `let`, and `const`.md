***

### **13. Difference Between `var`, `let`, and `const`**

JavaScript provides three ways to declare variables: `var`, `let`, and `const`. Understanding their differences is crucial for writing modern, bug-free code.

#### **A. `var` (The Old Way)**
*   **Function Scope:** A `var` variable is scoped to the entire function in which it's declared.
*   **Hoisting:** `var` declarations are hoisted to the top of their scope and initialized with `undefined`.
*   **Re-declaration:** Can be re-declared in the same scope without error.
*   **Example:**
    ```javascript
    function varExample() {
        if (true) {
            var x = 10;
        }
        console.log(x); // 10 (accessible outside the block)
    }
    var y = 5;
    var y = 10; // No error - re-declaration allowed
    ```

#### **B. `let` (The Modern Way - Block Scoped)**
*   **Block Scope:** A `let` variable is scoped to the block (`{}`) in which it's declared.
*   **Hoisting:** `let` declarations are hoisted but NOT initialized (Temporal Dead Zone).
*   **Re-declaration:** Cannot be re-declared in the same scope.
*   **Re-assignment:** Can be re-assigned new values.
*   **Example:**
    ```javascript
    function letExample() {
        if (true) {
            let x = 10;
            console.log(x); // 10
        }
        console.log(x); // ReferenceError: x is not defined
    }
    
    let y = 5;
    y = 10; // OK - re-assignment allowed
    let y = 15; // SyntaxError: Identifier 'y' has already been declared
    ```

#### **C. `const` (The Modern Way - Constant)**
*   **Block Scope:** Same as `let` - scoped to the block.
*   **Hoisting:** Same as `let` - hoisted but not initialized.
*   **Re-declaration:** Cannot be re-declared in the same scope.
*   **Re-assignment:** **Cannot** be re-assigned after declaration.
*   **Important Note:** For objects and arrays, the variable cannot be re-assigned, but the **contents can be modified**.
*   **Example:**
    ```javascript
    const z = 100;
    z = 200; // TypeError: Assignment to constant variable
    
    // But with objects/arrays:
    const person = { name: "John" };
    person.name = "Jane"; // ✅ Allowed - modifying content
    person.age = 30; // ✅ Allowed - adding property
    
    const numbers = [1, 2, 3];
    numbers.push(4); // ✅ Allowed - modifying content
    ```

#### **D. Comparison Table**

| Feature | `var` | `let` | `const` |
|---------|-------|-------|---------|
| **Scope** | Function | Block | Block |
| **Hoisting** | Hoisted and initialized | Hoisted but not initialized | Hoisted but not initialized |
| **Re-declaration** | ✅ Allowed | ❌ Not allowed | ❌ Not allowed |
| **Re-assignment** | ✅ Allowed | ✅ Allowed | ❌ Not allowed |
| **Temporal Dead Zone** | ❌ No | ✅ Yes | ✅ Yes |

#### **E. Best Practices**
1.  **Prefer `const`** by default for variables that won't be re-assigned.
2.  **Use `let`** when you need to re-assign a variable.
3.  **Avoid `var`** in modern JavaScript code.
4.  Use `const` for objects and arrays that you want to keep as the same reference (you can still modify their contents).

```javascript
// ✅ Modern best practice
const API_URL = "https://api.example.com"; // Constant value
let isLoading = false; // Will change during execution

function processData(data) {
    const results = []; // Constant reference, but array can be modified
    for (let i = 0; i < data.length; i++) { // i needs to change
        results.push(data[i] * 2);
    }
    return results;
}
```

**Key Takeaway:** Use `const` for values that shouldn't change, `let` for variables that need to change, and avoid `var` in modern code to prevent scope-related bugs.

---

**I have created the notes for Topic 13 including `const`. Please say "Next" for me to proceed to Topic 14 (Difference between innerHTML and textContent).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Datatypes in JavaScript|Data Types in JavaScript]]
- [[Web Development/JavaScript/Equality Operator|Equality Operators]]
