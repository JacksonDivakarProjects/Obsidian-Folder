***

### **22. Switch Case**

The `switch` statement is used to perform different actions based on different conditions. It's a cleaner alternative to long `if...else if` chains when testing a single value against multiple possible matches.

#### **A. Basic Syntax**

```javascript
switch(expression) {
    case value1:
        // Code to execute when expression === value1
        break;
    case value2:
        // Code to execute when expression === value2
        break;
    default:
        // Code to execute if no cases match
}
```

#### **B. Simple Example**

```javascript
let day = "Monday";

switch(day) {
    case "Monday":
        console.log("Start of work week");
        break;
    case "Friday":
        console.log("Weekend is near!");
        break;
    case "Saturday":
    case "Sunday":
        console.log("Weekend!");
        break;
    default:
        console.log("Regular work day");
}

// OUTPUT: "Start of work week"
```

#### **C. Without Break (Fall-through)**

```javascript
let grade = "B";

switch(grade) {
    case "A":
        console.log("Excellent");
        break;
    case "B":
        console.log("Good");
        // No break - will fall through to next case
    case "C":
        console.log("Average");
        break;
    case "D":
        console.log("Poor");
        break;
    default:
        console.log("Fail");
}

// OUTPUT: 
// "Good"
// "Average"
```

#### **D. Practical Example: User Role System**

```javascript
let userRole = "editor";

switch(userRole) {
    case "admin":
        console.log("Full access to all features");
        console.log("Can manage users");
        console.log("Can modify settings");
        break;
    case "editor":
        console.log("Can create and edit content");
        console.log("Can moderate comments");
        break;
    case "author":
        console.log("Can create own content");
        console.log("Can edit own posts");
        break;
    case "subscriber":
        console.log("Can read content");
        console.log("Can comment on posts");
        break;
    default:
        console.log("Guest user - limited access");
}

// OUTPUT:
// "Can create and edit content"
// "Can moderate comments"
```

#### **E. Using Expressions in Cases**

```javascript
let score = 85;

switch(true) {
    case (score >= 90):
        console.log("Grade: A");
        break;
    case (score >= 80):
        console.log("Grade: B");
        break;
    case (score >= 70):
        console.log("Grade: C");
        break;
    case (score >= 60):
        console.log("Grade: D");
        break;
    default:
        console.log("Grade: F");
}

// OUTPUT: "Grade: B"
```

#### **F. Multiple Conditions per Case**

```javascript
let fruit = "apple";

switch(fruit) {
    case "apple":
    case "pear":
    case "banana":
        console.log("This is a common fruit");
        break;
    case "dragonfruit":
    case "rambutan":
    case "durian":
        console.log("This is an exotic fruit");
        break;
    case "tomato":
    case "cucumber":
        console.log("This is technically a fruit");
        break;
    default:
        console.log("Unknown fruit");
}

// OUTPUT: "This is a common fruit"
```

#### **G. Switch vs If-Else Comparison**

```javascript
let trafficLight = "red";

// Using if-else
if (trafficLight === "red") {
    console.log("Stop");
} else if (trafficLight === "yellow") {
    console.log("Slow down");
} else if (trafficLight === "green") {
    console.log("Go");
} else {
    console.log("Invalid light");
}

// Using switch (cleaner for multiple conditions)
switch(trafficLight) {
    case "red":
        console.log("Stop");
        break;
    case "yellow":
        console.log("Slow down");
        break;
    case "green":
        console.log("Go");
        break;
    default:
        console.log("Invalid light");
}

// Both OUTPUT: "Stop"
```

#### **H. Real-World Example: Menu System**

```javascript
let userChoice = "profile";

switch(userChoice) {
    case "home":
        showHomePage();
        updateNavigation("home");
        break;
    case "profile":
        showProfilePage();
        updateNavigation("profile");
        highlightActiveTab();
        break;
    case "settings":
        showSettingsPage();
        checkPermissions();
        break;
    case "logout":
        confirmLogout();
        clearSession();
        redirectToLogin();
        break;
    default:
        showErrorPage();
        logInvalidChoice(userChoice);
}

function showProfilePage() {
    console.log("Displaying user profile...");
}
function updateNavigation(page) {
    console.log(`Navigation updated to: ${page}`);
}
// OUTPUT: "Displaying user profile..."
// OUTPUT: "Navigation updated to: profile"
```

#### **Key Points:**
- Use `switch` when testing one variable against multiple specific values
- Always use `break` unless you want fall-through behavior
- `default` case handles unexpected values
- More readable than long `if...else if` chains for multiple conditions
- Cases use strict equality (`===`) comparison

---

**I have created the notes for Topic 22. Please say "Next" for me to proceed to Topic 23 (Keystrokes).**


## 🔗 Related Notes
- [[Web Development/JavaScript/Keystrokes in JavaScript|Keystrokes: keypress Event and Event Object]]
- [[Web Development/JavaScript/Loops in JavaScript|Loops in JavaScript and forEach with Event Listeners]]
