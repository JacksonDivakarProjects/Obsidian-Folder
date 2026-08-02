***

### **26. setTimeout Function**

#### **Definition**
`setTimeout` is a function that executes a callback function after a specified delay (in milliseconds).

#### **Syntax**
```javascript
setTimeout(callbackFunction, delayInMilliseconds);
```

#### **Parameters**
- `callbackFunction`: The function to execute after the delay
- `delayInMilliseconds`: Time to wait before execution (1000ms = 1 second)

#### **Examples**

**Basic Example:**
```javascript
console.log("Start");

setTimeout(function() {
    console.log("This runs after 2 seconds");
}, 2000);

console.log("End");

// OUTPUT:
// "Start"
// "End"
// (2 second delay)
// "This runs after 2 seconds"
```

**With Arrow Function:**
```javascript
setTimeout(() => {
    console.log("Hello after 3 seconds");
}, 3000);
```

**Passing Parameters:**
```javascript
setTimeout((name, age) => {
    console.log(`Hello ${name}, age ${age}`);
}, 1000, "John", 25);
// OUTPUT after 1 second: "Hello John, age 25"
```

**Storing and Cancelling:**
```javascript
const timeoutId = setTimeout(() => {
    console.log("This won't run");
}, 5000);

clearTimeout(timeoutId); // Cancels the timeout
```


## 🔗 Related Notes
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
- [[Web Development/JavaScript/Event Listeners|Event Listeners in JavaScript]]
