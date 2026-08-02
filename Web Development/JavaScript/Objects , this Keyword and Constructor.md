***

### **18. Objects in JavaScript**

Objects are collections of key-value pairs used to store complex data structures.

#### **A. Object Creation**

**1. Object Literal Syntax (Most Common):**
```javascript
let person = {
    name: "John",
    age: 30,
    isStudent: false,
    hobbies: ["reading", "gaming"]
};

console.log(person.name);        // OUTPUT: "John"
console.log(person["age"]);      // OUTPUT: 30
console.log(person.hobbies[0]);  // OUTPUT: "reading"
```

**2. Adding/Modifying Properties:**
```javascript
let car = {};
car.make = "Toyota";        // Add property
car.model = "Camry";
car.year = 2020;

car.year = 2022;            // Modify property
car["color"] = "blue";      // Add using bracket notation

console.log(car);
// OUTPUT: {make: "Toyota", model: "Camry", year: 2022, color: "blue"}
```

**3. Object Methods:**
```javascript
let calculator = {
    add: function(a, b) {
        return a + b;
    },
    multiply(a, b) {        // Shorthand method syntax
        return a * b;
    }
};

console.log(calculator.add(5, 3));      // OUTPUT: 8
console.log(calculator.multiply(4, 2)); // OUTPUT: 8
```

---

### **19. The `this` Keyword**

The `this` keyword refers to the context in which a function is executed.

#### **A. `this` in Object Methods**
```javascript
let user = {
    name: "Alice",
    age: 25,
    introduce: function() {
        return `Hello, I'm ${this.name} and I'm ${this.age} years old.`;
    },
    birthday() {
        this.age++;
        return `Happy birthday! Now I'm ${this.age}.`;
    }
};

console.log(user.introduce()); // OUTPUT: "Hello, I'm Alice and I'm 25 years old."
console.log(user.birthday());  // OUTPUT: "Happy birthday! Now I'm 26."
console.log(user.age);         // OUTPUT: 26
```

#### **B. `this` Pitfalls**
```javascript
let obj = {
    value: 42,
    getValue: function() {
        return this.value;
    }
};

console.log(obj.getValue()); // OUTPUT: 42

let extractedFunction = obj.getValue;
console.log(extractedFunction()); // OUTPUT: undefined (lost 'this' context)
```

---

### **20. Constructor Functions**

Constructor functions create multiple objects with the same structure.

#### **A. Basic Constructor Function**
```javascript
function HouseKeeper(name, yearsExperience, cleaningRepertoire) {
    this.name = name;
    this.yearsExperience = yearsExperience;
    this.cleaningRepertoire = cleaningRepertoire;
    
    this.clean = function() {
        console.log(`${this.name} is cleaning...`);
    };
}

// Creating instances
let houseKeeper1 = new HouseKeeper("Jane", 5, ["bedroom", "bathroom"]);
let houseKeeper2 = new HouseKeeper("Mary", 3, ["kitchen", "living room"]);

console.log(houseKeeper1.name);  // OUTPUT: "Jane"
console.log(houseKeeper2.yearsExperience); // OUTPUT: 3
houseKeeper1.clean(); // OUTPUT: "Jane is cleaning..."
```

#### **B. Complete Working Example**
```javascript
// Helper functions
function cleanFloor(place) {
    console.log(`Cleaning the ${place} floor...`);
}

function move() {
    console.log("Moving to next task...");
}

// Constructor function
function HouseKeeper(name, year, cleaningRepertoire) {
    this.name = name;
    this.year = year;
    this.cleaningRepertoire = cleaningRepertoire;
    
    this.clean = function() {
        let place = prompt("What should I clean?");
        cleanFloor(place);
        move();
        return `Finished cleaning ${place}`;
    };
    
    this.workSchedule = function() {
        return `${this.name} with ${this.year} years experience can clean: ${this.cleaningRepertoire.join(", ")}`;
    };
}

// Creating object instance
let k1 = new HouseKeeper("Jane", 12, ["Hall", "Bike", "Kitchen"]);

console.log(k1.name);                    // OUTPUT: "Jane"
console.log(k1.year);                    // OUTPUT: 12
console.log(k1.cleaningRepertoire);      // OUTPUT: ["Hall", "Bike", "Kitchen"]
console.log(k1.workSchedule());          
// OUTPUT: "Jane with 12 years experience can clean: Hall, Bike, Kitchen"

// When k1.clean() is called:
// 1. Asks user "What should I clean?"
// 2. Calls cleanFloor() with user's input
// 3. Calls move()
// 4. Returns "Finished cleaning [user input]"
```

#### **C. Constructor Function Key Points**

1. **Function name starts with capital letter** (convention)
2. **Use `new` keyword** to create instances
3. **`this` refers to the new object** being created
4. **Properties/methods are attached to `this`**

```javascript
// Multiple instances
let k2 = new HouseKeeper("Bob", 8, ["Garage", "Office"]);
let k3 = new HouseKeeper("Sarah", 15, ["Whole House"]);

console.log(k2.workSchedule());
// OUTPUT: "Bob with 8 years experience can clean: Garage, Office"

console.log(k3.workSchedule());
// OUTPUT: "Sarah with 15 years experience can clean: Whole House"
```

#### **D. Checking Instance Type**
```javascript
console.log(k1 instanceof HouseKeeper);  // OUTPUT: true
console.log(typeof k1);                  // OUTPUT: "object"
```

**Key Takeaways:**
- Objects store data as key-value pairs
- `this` refers to the current object context
- Constructor functions create reusable object blueprints
- Use `new` keyword with constructor functions
- Methods can call external helper functions

---

**I have covered Topics 18, 19, and 20 together as requested. Please say "Next" for me to proceed to Topic 21 (Loops in JS).**

## 🔗 Related Notes
- [[Web Development/JavaScript/Higher Order Functions and Callback Functions|Higher Order Functions and Callback Functions]]
- [[Web Development/JavaScript/Loops in JavaScript|Loops in JavaScript and forEach with Event Listeners]]
