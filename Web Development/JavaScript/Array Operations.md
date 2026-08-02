***

### **6. Arrays - Push and Pull Operations**

Arrays are used to store multiple values in a single variable. "Push" and "Pull" are common terms for adding (pushing) elements to the end of an array and removing (pulling) elements from the end or beginning.

#### **A. Adding Elements to an Array (Pushing)**

1.  **`push()`**
    *   **Action:** Adds one or more elements **to the end** of an array.
    *   **Return Value:** The new `length` of the array.
    *   **Mutates Original Array:** Yes.
    *   **Example:**
        ```javascript
        let fruits = ["apple", "banana"];
        let newLength = fruits.push("orange");
        console.log(fruits); // ["apple", "banana", "orange"]
        console.log(newLength); // 3

        fruits.push("mango", "grape"); // Add multiple items
        console.log(fruits); // ["apple", "banana", "orange", "mango", "grape"]
        ```

2.  **`unshift()`**
    *   **Action:** Adds one or more elements **to the beginning** of an array.
    *   **Return Value:** The new `length` of the array.
    *   **Mutates Original Array:** Yes.
    *   **Example:**
        ```javascript
        let numbers = [2, 3, 4];
        numbers.unshift(1);
        console.log(numbers); // [1, 2, 3, 4]
        ```

#### **B. Removing Elements from an Array (Pulling)**

1.  **`pop()`**
    *   **Action:** Removes the **last** element from an array.
    *   **Return Value:** The **removed element**.
    *   **Mutates Original Array:** Yes.
    *   **Example:**
        ```javascript
        let fruits = ["apple", "banana", "orange"];
        let lastFruit = fruits.pop();
        console.log(fruits); // ["apple", "banana"]
        console.log(lastFruit); // "orange"
        ```

2.  **`shift()`**
    *   **Action:** Removes the **first** element from an array.
    *   **Return Value:** The **removed element**.
    *   **Mutates Original Array:** Yes.
    *   **Example:**
        ```javascript
        let numbers = [1, 2, 3, 4];
        let firstNumber = numbers.shift();
        console.log(numbers); // [2, 3, 4]
        console.log(firstNumber); // 1
        ```

#### **Visual Summary: Push vs. Pull**

| Method | Action | End/Start | Returns | Mutates Array |
| :--- | :--- | :--- | :--- | :--- |
| **`push(item)`** | **Adds** element(s) | **End** | New `length` | Yes |
| **`unshift(item)`** | **Adds** element(s) | **Start** | New `length` | Yes |
| **`pop()`** | **Removes** element | **End** | **Removed element** | Yes |
| **`shift()`** | **Removes** element | **Start** | **Removed element** | Yes |

**Key Takeaway:** These four methods are fundamental for managing the contents of an array, especially when treating it like a **stack** (LIFO - Last In, First Out, using `push/pop`) or a **queue** (FIFO - First In, First Out, using `push/shift`).

---

**I have created the notes for Topic 6. Please say "Next" for me to proceed to Topic 7 (DOM).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Loops in JavaScript|Loops in JavaScript and forEach with Event Listeners]]
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
- [[Web Development/JavaScript/String Operations|String Operations]]
