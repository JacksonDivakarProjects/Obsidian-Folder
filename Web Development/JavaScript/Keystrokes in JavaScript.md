***

### **23. Keystrokes: `keypress` Event and Event Object**

Keyboard events allow you to respond to user keyboard input. The `keypress` event (and related events) provide information about which key was pressed through the event object.

#### **A. Keyboard Events Overview**

```javascript
// Three main keyboard events
element.addEventListener('keydown', handler);  // Key is pressed down
element.addEventListener('keypress', handler); // Character key is pressed (deprecated but still used)
element.addEventListener('keyup', handler);    // Key is released
```

#### **B. The `keypress` Event and Event Object**

**Input HTML:**
```html
<input type="text" id="text-input" placeholder="Type something...">
<p id="output"></p>
```

**JavaScript:**
```javascript
let input = document.getElementById('text-input');
let output = document.getElementById('output');

input.addEventListener('keypress', function(event) {
    console.log(event); // Full event object
    console.log("Key pressed:", event.key);
    console.log("Key code:", event.keyCode);
    console.log("Character:", String.fromCharCode(event.keyCode));
    
    output.textContent = `You pressed: ${event.key} (Code: ${event.keyCode})`;
});
```

**Example OUTPUT when typing "A":**
```
Key pressed: "A"
Key code: 65
Character: "A"
// Display shows: "You pressed: A (Code: 65)"
```

#### **C. Key Properties in Event Object**

```javascript
document.addEventListener('keypress', function(event) {
    console.log("=== Key Event Info ===");
    console.log("event.key:", event.key);        // Character value
    console.log("event.code:", event.code);      // Physical key name
    console.log("event.keyCode:", event.keyCode); // Legacy code (deprecated)
    console.log("event.charCode:", event.charCode); // Character code
    console.log("event.which:", event.which);    // Legacy property
    console.log("event.shiftKey:", event.shiftKey); // Boolean
    console.log("event.ctrlKey:", event.ctrlKey);   // Boolean
    console.log("event.altKey:", event.altKey);     // Boolean
});
```

**Example OUTPUT when pressing "Shift + A":**
```
=== Key Event Info ===
event.key: "A"
event.code: "KeyA"
event.keyCode: 65
event.charCode: 65
event.which: 65
event.shiftKey: true
event.ctrlKey: false
event.altKey: false
```

#### **D. `key` vs `code` Properties**

```javascript
document.addEventListener('keypress', function(event) {
    console.log(`Key: "${event.key}" | Code: ${event.code}`);
});
```

**Example OUTPUTs:**
- Pressing "a": `Key: "a" | Code: KeyA`
- Pressing "A" (Shift+a): `Key: "A" | Code: KeyA`
- Pressing "1": `Key: "1" | Code: Digit1`
- Pressing Enter: `Key: "Enter" | Code: Enter`
- Pressing Space: `Key: " " | Code: Space`

#### **E. Practical Example: Keyboard Shortcuts**

```javascript
document.addEventListener('keypress', function(event) {
    switch(event.key) {
        case 's':
            if (event.ctrlKey) {
                event.preventDefault(); // Prevent browser save dialog
                console.log("Ctrl+S pressed - Saving document...");
                saveDocument();
            }
            break;
        case 'p':
            if (event.ctrlKey) {
                event.preventDefault();
                console.log("Ctrl+P pressed - Printing...");
                printDocument();
            }
            break;
        case 'Enter':
            console.log("Enter pressed - Submitting form...");
            submitForm();
            break;
        case 'Escape':
            console.log("Escape pressed - Closing modal...");
            closeModal();
            break;
    }
});

function saveDocument() {
    console.log("Document saved!");
}

function printDocument() {
    console.log("Printing document...");
}
```

#### **F. Detecting Special Keys**

```javascript
let inputField = document.getElementById('text-input');

inputField.addEventListener('keypress', function(event) {
    // Prevent numbers from being entered
    if (event.key >= '0' && event.key <= '9') {
        event.preventDefault();
        console.log("Numbers not allowed!");
    }
    
    // Limit to 10 characters
    if (this.value.length >= 10) {
        event.preventDefault();
        console.log("Maximum 10 characters reached!");
    }
});
```

#### **G. Real-World Example: Game Controls**

```javascript
let playerPosition = { x: 50, y: 50 };

document.addEventListener('keydown', function(event) {
    switch(event.code) {
        case 'ArrowUp':
            playerPosition.y -= 10;
            console.log("Moving UP - Position:", playerPosition);
            break;
        case 'ArrowDown':
            playerPosition.y += 10;
            console.log("Moving DOWN - Position:", playerPosition);
            break;
        case 'ArrowLeft':
            playerPosition.x -= 10;
            console.log("Moving LEFT - Position:", playerPosition);
            break;
        case 'ArrowRight':
            playerPosition.x += 10;
            console.log("Moving RIGHT - Position:", playerPosition);
            break;
        case 'Space':
            console.log("Jumping!");
            jump();
            break;
    }
});

function jump() {
    console.log("Player jumped!");
}
```

#### **H. Modern vs Legacy Approach**

```javascript
// ✅ Modern approach (recommended)
element.addEventListener('keypress', function(event) {
    console.log("Modern - Key:", event.key, "Code:", event.code);
});

// ❌ Legacy approach (deprecated but still works)
element.addEventListener('keypress', function(event) {
    console.log("Legacy - KeyCode:", event.keyCode);
    let char = String.fromCharCode(event.keyCode);
    console.log("Character:", char);
});
```

#### **Key Points:**
- Use `event.key` for the character value
- Use `event.code` for the physical key location
- `keypress` is being phased out - consider using `keydown` for new code
- Always use `event.preventDefault()` to stop default browser behavior
- Check modifier keys (`shiftKey`, `ctrlKey`, `altKey`) for keyboard shortcuts

---

**I have created the notes for Topic 23. Please say "Next" for me to proceed to Topic 24 (Higher Order Functions).**


## 🔗 Related Notes
- [[Web Development/JavaScript/Event Listeners|Event Listeners in JavaScript]]
- [[Web Development/JavaScript/Switch Case in JavaScript|Switch Case]]
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
