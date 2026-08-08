***

### **24. Higher Order Functions and Callback Functions**

Higher order functions are a fundamental concept in JavaScript that enable powerful functional programming patterns.

#### **A. What are Higher Order Functions?**

A higher order function is a function that:
1. Takes another function as an argument, **OR**
2. Returns a function as its result

#### **B. `addEventListener` as a Higher Order Function**

**Example 1: Basic Higher Order Function**
```javascript
// addEventListener is a Higher Order Function
// It takes a function (callback) as its second argument
button.addEventListener('click', function() {
    console.log('Button was clicked!');
});
```

**Example 2: Named Callback Function**
```javascript
// The function being passed is called a "callback function"
function handleClick() {
    console.log('Button clicked!');
}

// addEventListener (HOF) receives handleClick (callback)
button.addEventListener('click', handleClick);
```

#### **C. Creating Your Own Higher Order Functions**

**Example 1: HOF that takes a function**
```javascript
// Higher Order Function
function calculate(a, b, operation) {
    return operation(a, b);  // Calling the callback function
}

// Callback functions
function add(x, y) {
    return x + y;
}

function multiply(x, y) {
    return x * y;
}

// Using the HOF with different callbacks
console.log(calculate(5, 3, add));       // OUTPUT: 8
console.log(calculate(5, 3, multiply));  // OUTPUT: 15
```

**Example 2: HOF that returns a function**
```javascript
// Higher Order Function that returns a function
function createMultiplier(multiplier) {
    return function(number) {
        return number * multiplier;
    };
}

// Creating specialized functions
const double = createMultiplier(2);
const triple = createMultiplier(3);

console.log(double(5));  // OUTPUT: 10
console.log(triple(5));  // OUTPUT: 15
```

#### **D. Common Built-in Higher Order Functions**

**Array Methods as HOFs:**
```javascript
let numbers = [1, 2, 3, 4, 5];

// forEach - takes a callback function
numbers.forEach(function(number) {
    console.log(number * 2);
});
// OUTPUT: 2, 4, 6, 8, 10

// map - returns new array based on callback
let doubled = numbers.map(function(num) {
    return num * 2;
});
console.log(doubled); // OUTPUT: [2, 4, 6, 8, 10]

// filter - uses callback to test each element
let evenNumbers = numbers.filter(function(num) {
    return num % 2 === 0;
});
console.log(evenNumbers); // OUTPUT: [2, 4]
```

#### **E. Real-World Example: Data Processing Pipeline**

```javascript
// Higher Order Function for data processing
function processUserData(users, filterCallback, transformCallback) {
    const filtered = users.filter(filterCallback);
    const transformed = filtered.map(transformCallback);
    return transformed;
}

// Sample data
const users = [
    { name: "Alice", age: 25, role: "admin" },
    { name: "Bob", age: 17, role: "user" },
    { name: "Charlie", age: 30, role: "user" },
    { name: "Diana", age: 16, role: "moderator" }
];

// Callback functions
function isAdult(user) {
    return user.age >= 18;
}

function createUserDisplay(user) {
    return `${user.name} (${user.role})`;
}

// Using the HOF
const result = processUserData(users, isAdult, createUserDisplay);
console.log(result);
// OUTPUT: ["Alice (admin)", "Charlie (user)"]
```

#### **F. Event Handler with Custom HOF**

```javascript
// Higher Order Function for creating event handlers
function createEventHandler(callback, delay = 0) {
    return function(event) {
        if (delay > 0) {
            setTimeout(() => {
                callback(event);
            }, delay);
        } else {
            callback(event);
        }
    };
}

// Callback function
function logClick(event) {
    console.log('Clicked at:', event.clientX, event.clientY);
}

// Creating specialized event handler
const delayedClickHandler = createEventHandler(logClick, 1000);

// Usage
button.addEventListener('click', delayedClickHandler);
// When clicked, waits 1 second then logs coordinates
```

#### **G. Callback Functions with Parameters**

```javascript
// Higher Order Function
function repeatAction(times, action) {
    for (let i = 0; i < times; i++) {
        action(i);  // Pass current iteration to callback
    }
}

// Callback with parameter
function logIteration(iteration) {
    console.log(`Iteration number: ${iteration + 1}`);
}

// Another callback
function squareAndLog(num) {
    console.log(num * num);
}

repeatAction(3, logIteration);
// OUTPUT:
// Iteration number: 1
// Iteration number: 2
// Iteration number: 3

repeatAction(4, squareAndLog);
// OUTPUT: 0, 1, 4, 9
```

#### **H. The Pattern in addEventListener**

```javascript
// Behind the scenes concept (simplified)
function addEventListener(eventType, callbackFunction) {
    // Browser stores this information
    // When event occurs, browser calls:
    const eventObject = { 
        type: eventType, 
        target: element, 
        timestamp: Date.now() 
    };
    callbackFunction(eventObject);  // This is the callback execution
}

// This explains why we can access event object in our callbacks
button.addEventListener('click', function(event) {
    console.log(event.type);    // "click"
    console.log(event.target);  // The button element
});
```

#### **Key Points:**
- **Higher Order Functions** accept or return other functions
- **Callback Functions** are passed as arguments to HOFs
- `addEventListener` is a built-in HOF
- Array methods (`forEach`, `map`, `filter`) are HOFs
- Callbacks enable flexible, reusable code patterns

---

**I have created the notes for Topic 24. Please say "Next" for me to proceed to Topic 25 (Event in callback function).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Event Listeners|Event Listeners in JavaScript]]
- [[Web Development/JavaScript/Loops in JavaScript|Loops in JavaScript and forEach with Event Listeners]]
- [[Web Development/JavaScript/setTimeout Function|setTimeout Function]]
