***

### **21. Loops in JavaScript and forEach with Event Listeners**

Loops allow you to execute a block of code repeatedly. JavaScript provides several types of loops for different use cases.

#### **A. Traditional Loops**

**1. for Loop**
```javascript
for (let i = 0; i < 5; i++) {
    console.log(`Iteration: ${i}`);
}
// OUTPUT: 
// Iteration: 0
// Iteration: 1
// Iteration: 2
// Iteration: 3
// Iteration: 4
```

**2. while Loop**
```javascript
let count = 0;
while (count < 3) {
    console.log(`Count: ${count}`);
    count++;
}
// OUTPUT:
// Count: 0
// Count: 1
// Count: 2
```

**3. do...while Loop**
```javascript
let x = 0;
do {
    console.log(`Value: ${x}`);
    x++;
} while (x < 3);
// OUTPUT:
// Value: 0
// Value: 1
// Value: 2
```

#### **B. Array Loops**

**1. for...of Loop (Modern)**
```javascript
let fruits = ["apple", "banana", "orange"];
for (let fruit of fruits) {
    console.log(fruit);
}
// OUTPUT:
// apple
// banana
// orange
```

**2. for...in Loop (for object properties)**
```javascript
let person = {name: "John", age: 30, city: "NYC"};
for (let key in person) {
    console.log(`${key}: ${person[key]}`);
}
// OUTPUT:
// name: John
// age: 30
// city: NYC
```

#### **C. forEach Method with Event Listeners and querySelectorAll**

**Input HTML:**
```html
<button class="btn">Button 1</button>
<button class="btn">Button 2</button>
<button class="btn">Button 3</button>
<div id="output"></div>
```

**JavaScript:**
```javascript
// Select all buttons
let buttons = document.querySelectorAll('.btn');
let output = document.getElementById('output');

// Using forEach to add event listeners to each button
buttons.forEach(function(button, index) {
    button.addEventListener('click', function() {
        output.textContent = `Button ${index + 1} was clicked!`;
    });
});
```

**Practical Example with Multiple Elements:**
```html
<div class="card" data-price="10">Product A - $10</div>
<div class="card" data-price="20">Product B - $20</div>
<div class="card" data-price="30">Product C - $30</div>
<p id="total">Total: $0</p>
```

```javascript
let cards = document.querySelectorAll('.card');
let totalDisplay = document.getElementById('total');
let total = 0;

cards.forEach(function(card) {
    card.addEventListener('click', function() {
        let price = parseInt(card.getAttribute('data-price'));
        total += price;
        totalDisplay.textContent = `Total: $${total}`;
        card.style.backgroundColor = 'lightgreen';
    });
});
```

#### **D. forEach vs Traditional Loop with querySelectorAll**

```javascript
let items = document.querySelectorAll('.item');

// Method 1: Traditional for loop
for (let i = 0; i < items.length; i++) {
    items[i].addEventListener('mouseover', function() {
        this.style.transform = 'scale(1.1)';
    });
}

// Method 2: forEach (Cleaner)
items.forEach(function(item) {
    item.addEventListener('mouseout', function() {
        this.style.transform = 'scale(1)';
    });
});

// Method 3: forEach with arrow function
items.forEach(item => {
    item.addEventListener('click', () => {
        console.log('Item clicked:', item.textContent);
    });
});
```

#### **E. Breaking Out of Loops**

```javascript
let numbers = [1, 2, 3, 4, 5];

// break in for loop
for (let num of numbers) {
    if (num === 3) break;
    console.log(num);
}
// OUTPUT: 1, 2

// Note: forEach doesn't support break, use return instead
numbers.forEach(num => {
    if (num === 3) return; // continues to next iteration
    console.log(num);
});
// OUTPUT: 1, 2, 4, 5
```

#### **F. Real-World Example: Dynamic List Management**

**Input HTML:**
```html
<ul id="task-list">
    <li class="task">Task 1 <button class="complete">Complete</button></li>
    <li class="task">Task 2 <button class="complete">Complete</button></li>
    <li class="task">Task 3 <button class="complete">Complete</button></li>
</ul>
```

```javascript
let completeButtons = document.querySelectorAll('.complete');

completeButtons.forEach(function(button, index) {
    button.addEventListener('click', function() {
        let task = this.parentElement;
        task.style.textDecoration = 'line-through';
        this.textContent = 'Completed!';
        this.disabled = true;
        console.log(`Completed task ${index + 1}`);
    });
});
```

**Key Points:**
- Use `for` loops when you need index control or breaking early
- Use `forEach` for cleaner array iteration
- `querySelectorAll` returns a NodeList that works with `forEach`
- Always use `querySelectorAll` (not `getElementsByClassName`) with `forEach`

---

**I have created the notes for Topic 21. Please say "Next" for me to proceed to Topic 22 (Switch Case).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
- [[Web Development/JavaScript/Event Listeners|Event Listeners in JavaScript]]
- [[Web Development/JavaScript/Switch Case in JavaScript|Switch Case]]
