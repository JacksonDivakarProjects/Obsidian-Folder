***

### **17. Event Listeners in JavaScript**

Event listeners allow you to make web pages interactive by responding to user actions and browser events.

#### **A. Basic Event Listener Syntax**

```javascript
element.addEventListener(event, callbackFunction);
```

**Input HTML:**
```html
<button id="click-btn">Click Me</button>
<div id="output"></div>
```

**JavaScript:**
```javascript
let button = document.getElementById('click-btn');
let output = document.getElementById('output');

button.addEventListener('click', function() {
    output.textContent = 'Button was clicked!';
});
```

#### **B. Common Event Types**

```javascript
let element = document.getElementById('myElement');

// Mouse events
element.addEventListener('click', handleClick);
element.addEventListener('dblclick', handleDoubleClick);
element.addEventListener('mouseover', handleMouseOver);
element.addEventListener('mouseout', handleMouseOut);

// Keyboard events  
element.addEventListener('keydown', handleKeyDown);
element.addEventListener('keyup', handleKeyUp);

// Form events
element.addEventListener('submit', handleSubmit);
element.addEventListener('change', handleChange);
element.addEventListener('focus', handleFocus);
element.addEventListener('blur', handleBlur);

// Window events
window.addEventListener('load', handlePageLoad);
window.addEventListener('resize', handleResize);
```

#### **C. Using Named Functions vs Anonymous Functions**

**Named Function Approach:**
```javascript
function handleButtonClick() {
    console.log('Button clicked!');
}

let button = document.getElementById('myButton');
button.addEventListener('click', handleButtonClick);
```

**Anonymous Function Approach:**
```javascript
let button = document.getElementById('myButton');
button.addEventListener('click', function() {
    console.log('Button clicked!');
});
```

#### **D. The Event Object**

When an event occurs, the browser passes an **event object** to the callback function containing information about the event.

**Input HTML:**
```html
<button id="event-btn">Click for Event Info</button>
<div id="event-info"></div>
```

**JavaScript:**
```javascript
let button = document.getElementById('event-btn');
let infoDiv = document.getElementById('event-info');

button.addEventListener('click', function(event) {
    infoDiv.innerHTML = `
        Event Type: ${event.type}<br>
        Target: ${event.target.id}<br>
        X Position: ${event.clientX}<br>
        Y Position: ${event.clientY}<br>
        Timestamp: ${event.timeStamp}
    `;
});
```

#### **E. Removing Event Listeners**

To remove an event listener, you must use a named function.

```javascript
function handleClick() {
    console.log('This will only work once');
    button.removeEventListener('click', handleClick);
}

let button = document.getElementById('myButton');
button.addEventListener('click', handleClick);
```

#### **F. Event Bubbling and `this` Context**

**Input HTML:**
```html
<div id="parent">
    Parent
    <button id="child">Child Button</button>
</div>
```

**JavaScript:**
```javascript
let parent = document.getElementById('parent');
let child = document.getElementById('child');

parent.addEventListener('click', function(event) {
    console.log('Parent clicked');
    console.log('Event target:', event.target.id); // Element that triggered event
    console.log('This refers to:', this.id); // Element that has the listener
});

child.addEventListener('click', function(event) {
    console.log('Child button clicked');
    event.stopPropagation(); // Prevents bubbling to parent
});
```

**OUTPUT when clicking the button:**
```
Child button clicked
// Without stopPropagation(), it would also show "Parent clicked"
```

#### **G. Multiple Events on Same Element**

```javascript
let box = document.getElementById('color-box');

function turnRed() {
    box.style.backgroundColor = 'red';
}

function turnBlue() {
    box.style.backgroundColor = 'blue';
}

function logEvent(event) {
    console.log('Event:', event.type);
}

// Multiple events with different handlers
box.addEventListener('mouseenter', turnRed);
box.addEventListener('mouseleave', turnBlue);
box.addEventListener('click', logEvent);
```

#### **H. Event Listener with Parameters**

If you need to pass parameters, wrap the function call in another function:

```javascript
function greetUser(name, age) {
    console.log(`Hello ${name}, you are ${age} years old!`);
}

let button = document.getElementById('user-btn');
button.addEventListener('click', function() {
    greetUser('John', 25);
});
```

**Key Points:**
- Use `addEventListener()` instead of `onclick` properties for better flexibility
- The event object provides details about what happened
- Use named functions when you need to remove listeners later
- Events bubble up through the DOM tree unless stopped

---

**I have created the notes for Topic 17. Please say "Next" for me to proceed to Topic 18 (Objects).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
- [[Web Development/JavaScript/Keystrokes in JavaScript|Keystrokes: keypress Event and Event Object]]
- [[Web Development/JavaScript/Loops in JavaScript|Loops in JavaScript and forEach with Event Listeners]]
