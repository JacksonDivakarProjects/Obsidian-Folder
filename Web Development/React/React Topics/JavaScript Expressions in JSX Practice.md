## **7. JavaScript Expressions in JSX Practice - Complete Beginner's Guide**

### **Introduction**
Welcome to hands-on practice! Now that we've learned about JavaScript expressions in JSX and template literals, it's time to **apply what you've learned**. Practice is essential for building muscle memory and truly understanding these concepts.

### **How This Practice Session Works**
We'll work through exercises from **simple to complex**. For each exercise:
1. Try it yourself first
2. Check the solution
3. Understand why it works
4. Experiment with variations

### **Practice Environment Setup**

**Option 1: CodeSandbox (Recommended)**
1. Go to [codesandbox.io](https://codesandbox.io)
2. Create a new React sandbox
3. Replace `App.js` with our practice code

**Option 2: Local Setup (If you have it)**
```bash
npx create-react-app jsx-practice
cd jsx-practice
npm start
```

### **Exercise 1: Basic Variable Display**

**Goal:** Display variables in JSX

```jsx
// Exercise 1: Basic Variables
function BasicVariables() {
  const name = "Alex Johnson";
  const age = 28;
  const occupation = "Web Developer";
  
  return (
    <div className="exercise">
      <h2>Exercise 1: Basic Variables</h2>
      {/* Your code here */}
    </div>
  );
}
```

**Your Task:** Display:
- Name in an `<h3>` tag
- Age in a paragraph
- Occupation in a paragraph with "Job:" prefix

**Try it yourself before looking at the solution!**

---

**Solution:**
```jsx
function BasicVariables() {
  const name = "Alex Johnson";
  const age = 28;
  const occupation = "Web Developer";
  
  return (
    <div className="exercise">
      <h2>Exercise 1: Basic Variables</h2>
      <h3>{name}</h3>
      <p>Age: {age}</p>
      <p>Job: {occupation}</p>
    </div>
  );
}
```

**Key Learning:** Simple variables go directly inside `{}`

---

### **Exercise 2: Mathematical Operations**

**Goal:** Perform calculations inside JSX

```jsx
// Exercise 2: Math Operations
function MathOperations() {
  const price = 24.99;
  const quantity = 3;
  const taxRate = 0.08; // 8%
  
  return (
    <div className="exercise">
      <h2>Exercise 2: Math Operations</h2>
      {/* Calculate and display:
          1. Subtotal (price * quantity)
          2. Tax (subtotal * taxRate)
          3. Total (subtotal + tax)
          4. Round total to 2 decimal places
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function MathOperations() {
  const price = 24.99;
  const quantity = 3;
  const taxRate = 0.08;
  
  const subtotal = price * quantity;
  const tax = subtotal * taxRate;
  const total = subtotal + tax;
  
  return (
    <div className="exercise">
      <h2>Exercise 2: Math Operations</h2>
      <p>Price per item: ${price.toFixed(2)}</p>
      <p>Quantity: {quantity}</p>
      <p>Subtotal: ${subtotal.toFixed(2)}</p>
      <p>Tax (8%): ${tax.toFixed(2)}</p>
      <p><strong>Total: ${total.toFixed(2)}</strong></p>
    </div>
  );
}
```

**Alternative (calculations in JSX):**
```jsx
<p>Subtotal: ${(price * quantity).toFixed(2)}</p>
<p>Tax: ${(price * quantity * taxRate).toFixed(2)}</p>
<p>Total: ${(price * quantity * (1 + taxRate)).toFixed(2)}</p>
```

**Key Learning:** You can do math directly in JSX or calculate first

---

### **Exercise 3: Function Calls in JSX**

**Goal:** Call functions and use their return values

```jsx
// Exercise 3: Function Calls
function FunctionCalls() {
  // Function definitions
  const getGreeting = (time) => {
    if (time < 12) return "Good Morning";
    if (time < 18) return "Good Afternoon";
    return "Good Evening";
  };
  
  const formatCurrency = (amount) => {
    return `$${amount.toFixed(2)}`;
  };
  
  const getRandomNumber = () => {
    return Math.floor(Math.random() * 100) + 1;
  };
  
  const currentHour = new Date().getHours();
  const productPrice = 49.99;
  
  return (
    <div className="exercise">
      <h2>Exercise 3: Function Calls</h2>
      {/* Display:
          1. Greeting based on currentHour
          2. Formatted product price
          3. A random number
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function FunctionCalls() {
  const getGreeting = (time) => {
    if (time < 12) return "Good Morning";
    if (time < 18) return "Good Afternoon";
    return "Good Evening";
  };
  
  const formatCurrency = (amount) => {
    return `$${amount.toFixed(2)}`;
  };
  
  const getRandomNumber = () => {
    return Math.floor(Math.random() * 100) + 1;
  };
  
  const currentHour = new Date().getHours();
  const productPrice = 49.99;
  
  return (
    <div className="exercise">
      <h2>Exercise 3: Function Calls</h2>
      <p>{getGreeting(currentHour)}! It's {currentHour}:00</p>
      <p>Product Price: {formatCurrency(productPrice)}</p>
      <p>Random Number: {getRandomNumber()}</p>
      <p>Another Random: {getRandomNumber()}</p>
    </div>
  );
}
```

**Key Learning:** Functions are called and their return values are displayed

---

### **Exercise 4: Template Literals Practice**

**Goal:** Use template literals for string formatting

```jsx
// Exercise 4: Template Literals
function TemplateLiterals() {
  const firstName = "Maria";
  const lastName = "Garcia";
  const score = 87;
  const maxScore = 100;
  
  return (
    <div className="exercise">
      <h2>Exercise 4: Template Literals</h2>
      {/* Create these using template literals:
          1. Full name: "Maria Garcia"
          2. Score display: "Score: 87/100"
          3. Percentage: "Percentage: 87%"
          4. Welcome message: "Welcome, Maria Garcia! Your score is 87/100 (87%)"
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function TemplateLiterals() {
  const firstName = "Maria";
  const lastName = "Garcia";
  const score = 87;
  const maxScore = 100;
  const percentage = (score / maxScore) * 100;
  
  return (
    <div className="exercise">
      <h2>Exercise 4: Template Literals</h2>
      <p>{`Full name: ${firstName} ${lastName}`}</p>
      <p>{`Score: ${score}/${maxScore}`}</p>
      <p>{`Percentage: ${percentage}%`}</p>
      <p>{`Welcome, ${firstName} ${lastName}! Your score is ${score}/${maxScore} (${percentage}%)`}</p>
    </div>
  );
}
```

**Key Learning:** Template literals make string concatenation cleaner

---

### **Exercise 5: Conditional Rendering with Ternary Operator**

**Goal:** Show different content based on conditions

```jsx
// Exercise 5: Conditional Rendering
function ConditionalRendering() {
  const isLoggedIn = true;
  const userRole = "admin"; // "admin", "user", or "guest"
  const itemsInCart = 0;
  
  return (
    <div className="exercise">
      <h2>Exercise 5: Conditional Rendering</h2>
      {/* Display:
          1. If logged in: "Welcome back!"
             If not: "Please log in"
          2. Based on userRole:
             - "admin": "Administrator Dashboard"
             - "user": "User Dashboard"
             - "guest": "Limited Access"
          3. Cart status:
             - If 0: "Your cart is empty"
             - If 1-5: "You have X items in cart"
             - If >5: "You have many items (X) in cart"
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function ConditionalRendering() {
  const isLoggedIn = true;
  const userRole = "admin";
  const itemsInCart = 0;
  
  const getCartMessage = (count) => {
    if (count === 0) return "Your cart is empty";
    if (count <= 5) return `You have ${count} item${count > 1 ? 's' : ''} in cart`;
    return `You have many items (${count}) in cart`;
  };
  
  return (
    <div className="exercise">
      <h2>Exercise 5: Conditional Rendering</h2>
      
      {/* Login Status */}
      <div className="status">
        {isLoggedIn ? (
          <p className="welcome">Welcome back!</p>
        ) : (
          <p className="login-prompt">Please log in</p>
        )}
      </div>
      
      {/* User Role */}
      <div className="dashboard">
        {userRole === "admin" && <h3>Administrator Dashboard</h3>}
        {userRole === "user" && <h3>User Dashboard</h3>}
        {userRole === "guest" && <h3>Limited Access</h3>}
      </div>
      
      {/* Cart Status */}
      <div className="cart">
        <p>{getCartMessage(itemsInCart)}</p>
      </div>
    </div>
  );
}
```

**Key Learning:** Ternary operator `? :` for if-else, `&&` for simple if

---

### **Exercise 6: Array Methods in JSX**

**Goal:** Render lists using array methods

```jsx
// Exercise 6: Array Methods
function ArrayMethods() {
  const fruits = ["Apple", "Banana", "Orange", "Grapes", "Mango"];
  const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  
  return (
    <div className="exercise">
      <h2>Exercise 6: Array Methods</h2>
      {/* Display:
          1. Fruits as an unordered list
          2. Even numbers only
          3. Fruits in uppercase
          4. Sum of all numbers
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function ArrayMethods() {
  const fruits = ["Apple", "Banana", "Orange", "Grapes", "Mango"];
  const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  
  const evenNumbers = numbers.filter(n => n % 2 === 0);
  const sum = numbers.reduce((total, num) => total + num, 0);
  
  return (
    <div className="exercise">
      <h2>Exercise 6: Array Methods</h2>
      
      {/* Fruits List */}
      <div>
        <h3>Fruits List:</h3>
        <ul>
          {fruits.map((fruit, index) => (
            <li key={index}>{fruit}</li>
          ))}
        </ul>
      </div>
      
      {/* Even Numbers */}
      <div>
        <h3>Even Numbers:</h3>
        <p>{evenNumbers.join(", ")}</p>
      </div>
      
      {/* Uppercase Fruits */}
      <div>
        <h3>Uppercase Fruits:</h3>
        <p>{fruits.map(fruit => fruit.toUpperCase()).join(" | ")}</p>
      </div>
      
      {/* Sum */}
      <div>
        <h3>Sum of Numbers 1-10:</h3>
        <p>{sum}</p>
        <p>(Also calculated in JSX: {numbers.reduce((t, n) => t + n, 0)})</p>
      </div>
    </div>
  );
}
```

**Key Learning:** `map()` for rendering lists, `filter()` for filtering, `reduce()` for aggregating

---

### **Exercise 7: Object Properties in JSX**

**Goal:** Access and display object properties

```jsx
// Exercise 7: Object Properties
function ObjectProperties() {
  const product = {
    id: 101,
    name: "Wireless Headphones",
    brand: "AudioTech",
    price: 89.99,
    inStock: true,
    features: ["Noise Cancelling", "Bluetooth 5.0", "24h Battery"],
    ratings: {
      average: 4.5,
      count: 1287
    }
  };
  
  return (
    <div className="exercise">
      <h2>Exercise 7: Object Properties</h2>
      {/* Display:
          1. Product name and brand
          2. Price formatted as "$89.99"
          3. Stock status with emoji (✅ if in stock, ❌ if not)
          4. Features as a list
          5. Average rating with stars (4.5 = ⭐⭐⭐⭐⭐)
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function ObjectProperties() {
  const product = {
    id: 101,
    name: "Wireless Headphones",
    brand: "AudioTech",
    price: 89.99,
    inStock: true,
    features: ["Noise Cancelling", "Bluetooth 5.0", "24h Battery"],
    ratings: {
      average: 4.5,
      count: 1287
    }
  };
  
  const formatPrice = (price) => `$${price.toFixed(2)}`;
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = "⭐".repeat(fullStars);
    if (hasHalfStar) stars += "½";
    return stars;
  };
  
  return (
    <div className="exercise">
      <h2>Exercise 7: Object Properties</h2>
      
      <div className="product-card">
        <h3>{product.name}</h3>
        <p>Brand: {product.brand}</p>
        <p>Price: {formatPrice(product.price)}</p>
        <p>
          Stock: {product.inStock ? "✅ In Stock" : "❌ Out of Stock"}
        </p>
        
        <div>
          <h4>Features:</h4>
          <ul>
            {product.features.map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>
        
        <div>
          <h4>Ratings:</h4>
          <p>{renderStars(product.ratings.average)} ({product.ratings.average}/5)</p>
          <p>Based on {product.ratings.count} reviews</p>
        </div>
      </div>
    </div>
  );
}
```

**Key Learning:** Access nested object properties with dot notation

---

### **Exercise 8: Combining Everything - User Dashboard**

**Goal:** Create a complete component using all concepts

```jsx
// Exercise 8: User Dashboard
function UserDashboard() {
  const user = {
    name: "Sam Wilson",
    email: "sam@example.com",
    joinDate: new Date("2023-03-15"),
    isPremium: true,
    stats: {
      posts: 42,
      comments: 187,
      likes: 1024
    },
    skills: ["React", "JavaScript", "CSS", "Node.js"]
  };
  
  const today = new Date();
  const daysSinceJoin = Math.floor((today - user.joinDate) / (1000 * 60 * 60 * 24));
  
  return (
    <div className="dashboard">
      <h2>User Dashboard</h2>
      {/* Create a user dashboard displaying:
          1. Welcome message with name
          2. Email
          3. Membership status (Premium or Regular)
          4. How many days they've been a member
          5. Statistics in a nice format
          6. Skills as tags
          7. A summary using template literals
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function UserDashboard() {
  const user = {
    name: "Sam Wilson",
    email: "sam@example.com",
    joinDate: new Date("2023-03-15"),
    isPremium: true,
    stats: {
      posts: 42,
      comments: 187,
      likes: 1024
    },
    skills: ["React", "JavaScript", "CSS", "Node.js"]
  };
  
  const today = new Date();
  const daysSinceJoin = Math.floor((today - user.joinDate) / (1000 * 60 * 60 * 24));
  const monthsSinceJoin = Math.floor(daysSinceJoin / 30);
  
  const formatNumber = (num) => {
    if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
    return num.toString();
  };
  
  return (
    <div className="dashboard">
      <h2>User Dashboard</h2>
      
      {/* Welcome Section */}
      <div className="welcome-section">
        <h3>{`Welcome, ${user.name}! 👋`}</h3>
        <p>Email: {user.email}</p>
        <p className={user.isPremium ? "premium-badge" : "regular-badge"}>
          {user.isPremium ? "🌟 Premium Member" : "Regular Member"}
        </p>
      </div>
      
      {/* Membership Info */}
      <div className="membership-info">
        <p>{`Member for ${daysSinceJoin} days (about ${monthsSinceJoin} months)`}</p>
        <p>{`Joined: ${user.joinDate.toLocaleDateString()}`}</p>
      </div>
      
      {/* Statistics */}
      <div className="stats">
        <h4>Activity Statistics:</h4>
        <div className="stats-grid">
          <div className="stat-card">
            <h5>Posts</h5>
            <p className="stat-number">{formatNumber(user.stats.posts)}</p>
          </div>
          <div className="stat-card">
            <h5>Comments</h5>
            <p className="stat-number">{formatNumber(user.stats.comments)}</p>
          </div>
          <div className="stat-card">
            <h5>Likes Received</h5>
            <p className="stat-number">{formatNumber(user.stats.likes)}</p>
          </div>
        </div>
      </div>
      
      {/* Skills */}
      <div className="skills">
        <h4>Skills:</h4>
        <div className="skill-tags">
          {user.skills.map((skill, index) => (
            <span key={index} className="skill-tag">
              {skill}
            </span>
          ))}
        </div>
      </div>
      
      {/* Summary */}
      <div className="summary">
        <h4>Summary:</h4>
        <p>
          {`${user.name} has been a ${user.isPremium ? 'Premium' : 'Regular'} member for ${monthsSinceJoin} months, 
          with ${user.stats.posts} posts, ${user.stats.comments} comments, and ${formatNumber(user.stats.likes)} likes received. 
          ${user.name} is skilled in ${user.skills.length > 1 ? user.skills.slice(0, -1).join(', ') + ' and ' + user.skills.slice(-1) : user.skills[0]}.`}
        </p>
      </div>
    </div>
  );
}
```

---

### **Additional Practice Challenges**

#### **Challenge 1: Dynamic CSS Classes**
Create a notification component that changes style based on type:
```jsx
function Notification({ type, message }) {
  // type can be: "success", "error", "warning", "info"
  // Create dynamic class: "notification notification-success"
  
  return (
    <div className={`notification notification-${type}`}>
      {message}
    </div>
  );
}
```

#### **Challenge 2: Shopping Cart Summary**
```jsx
function CartSummary({ items, taxRate, discount }) {
  // Calculate: subtotal, tax, discount amount, total
  // Display all with proper formatting
}
```

#### **Challenge 3: Progress Tracker**
```jsx
function ProgressTracker({ current, total, unit = "steps" }) {
  // Calculate percentage
  // Show progress bar and text: "3/5 steps completed (60%)"
}
```

### **Common Mistakes and Debugging Tips**

#### **Mistake 1: Forgetting Curly Braces**
```jsx
// ❌
<p>Hello name</p>  // Shows literal "name"

// ✅
<p>Hello {name}</p>  // Shows variable value
```

#### **Mistake 2: Trying to Render Objects**
```jsx
// ❌ Can't render objects directly
<p>{user}</p>  // Error: Objects are not valid as a React child

// ✅ Render specific properties
<p>{user.name}</p>
<p>{JSON.stringify(user)}</p>  // If you need to debug
```

#### **Mistake 3: Forgetting Return in Functions**
```jsx
// ❌
const getMessage = () => {
  "Hello";  // No return statement
};

// ✅
const getMessage = () => {
  return "Hello";
};
// Or implicit return
const getMessage = () => "Hello";
```

### **Interactive Practice in CodeSandbox**

Create this interactive component:

```jsx
function InteractivePractice() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState("Hello");
  
  const doubleCount = count * 2;
  const isEven = count % 2 === 0;
  const wordCount = text.split(" ").length;
  
  return (
    <div>
      <h2>Interactive Practice</h2>
      
      <div>
        <p>Count: {count}</p>
        <button onClick={() => setCount(count + 1)}>Increment</button>
        <button onClick={() => setCount(count - 1)}>Decrement</button>
      </div>
      
      <div>
        <p>Double Count: {doubleCount}</p>
        <p>Count is {isEven ? "Even" : "Odd"}</p>
      </div>
      
      <div>
        <input 
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something..."
        />
        <p>Text: {text}</p>
        <p>Character Count: {text.length}</p>
        <p>Word Count: {wordCount}</p>
        <p>Uppercase: {text.toUpperCase()}</p>
      </div>
    </div>
  );
}
```

### **Practice Checklist**

✅ **Basic Mastery:**
- [ ] Display variables in JSX
- [ ] Perform calculations
- [ ] Call functions
- [ ] Use template literals

✅ **Intermediate Skills:**
- [ ] Conditional rendering
- [ ] Array methods (map, filter, reduce)
- [ ] Object property access
- [ ] Dynamic CSS classes

✅ **Advanced Practice:**
- [ ] Combine multiple expressions
- [ ] Create reusable formatting functions
- [ ] Handle edge cases
- [ ] Optimize for readability

### **What to Do Next**

1. **Create your own exercises** - Think of real scenarios
2. **Refactor** - Try different approaches to same problem
3. **Break things** - Intentionally create errors to learn debugging
4. **Review** - Go back to earlier exercises with new understanding

### **Summary**

**You've practiced:**
1. Variables and expressions in JSX
2. Template literals for clean strings
3. Conditional rendering
4. Array methods for lists
5. Object property access
6. Combining all concepts

**Remember:** The key to mastery is **consistent practice**. Every React component you'll ever write uses these concepts!

---

**Ready for Topic 8: "JSX Attributes & Styling React Elements"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/JavaScript Expressions in JSX & ES6 Template Literals|JavaScript Expressions in JSX & ES6 Template Literals]]
- [[Web Development/React/React Topics/Introduction to JSX and Babel|Introduction to JSX and Babel]]
- [[Web Development/React/React Topics/JSX Attributes & Styling React Elements|JSX Attributes & Styling React Elements]]
