## **6. JavaScript Expressions in JSX & ES6 Template Literals - Complete Beginner's Guide**

### **Introduction**
Welcome to the magic of JSX! Today we're learning how to **embed JavaScript** inside your JSX using curly braces `{}`. This is what makes React dynamic and powerful. We'll also explore **ES6 Template Literals** - a cleaner way to work with strings in JavaScript.

### **JavaScript in JSX: The Power of Curly Braces {}**

Remember: **Everything inside curly braces `{}` in JSX is evaluated as JavaScript**.

#### **Basic Concept:**
```jsx
// JSX with embedded JavaScript
const element = <h1>Hello, {name}!</h1>;

// What happens:
// 1. React sees the curly braces
// 2. Evaluates the JavaScript expression inside
// 3. Renders the result
```

### **What Can Go Inside {}?**

Here's a comprehensive list of what you can put inside curly braces:

#### **1. Variables**
```jsx
const userName = "Alex";
const age = 30;

function Greeting() {
  return (
    <div>
      <p>Hello, {userName}!</p>
      <p>You are {age} years old.</p>
    </div>
  );
}
```

#### **2. Mathematical Expressions**
```jsx
function Calculator() {
  return (
    <div>
      <p>5 + 3 = {5 + 3}</p>
      <p>10 * 2 = {10 * 2}</p>
      <p>100 / 4 = {100 / 4}</p>
      <p>2 to the power of 3 = {Math.pow(2, 3)}</p>
    </div>
  );
}
```

#### **3. Function Calls**
```jsx
function formatDate(date) {
  return date.toLocaleDateString();
}

function CurrentDate() {
  const today = new Date();
  
  return (
    <div>
      <p>Today is {formatDate(today)}</p>
      <p>Formatted: {today.toLocaleString()}</p>
    </div>
  );
}
```

#### **4. Ternary Operators (Conditional Expressions)**
```jsx
function WelcomeMessage({ isLoggedIn, userName }) {
  return (
    <div>
      {isLoggedIn ? (
        <h1>Welcome back, {userName}!</h1>
      ) : (
        <h1>Please log in to continue</h1>
      )}
    </div>
  );
}
```

#### **5. Array Methods (map, filter, etc.)**
```jsx
function ShoppingList() {
  const items = ['Apples', 'Bananas', 'Milk', 'Bread'];
  
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}
```

#### **6. Object Properties**
```jsx
function UserProfile() {
  const user = {
    name: "Sarah",
    email: "sarah@example.com",
    age: 28,
    isAdmin: true
  };
  
  return (
    <div>
      <p>Name: {user.name}</p>
      <p>Email: {user.email}</p>
      <p>Age: {user.age}</p>
      <p>Status: {user.isAdmin ? 'Admin' : 'User'}</p>
    </div>
  );
}
```

### **Understanding JavaScript Expressions**

**Key Rule:** Anything that **returns a value** can go inside `{}`.

```jsx
// ✅ VALID - These return values:
{userName}                    // Variable
{calculateTotal()}            // Function call
{isActive ? 'Yes' : 'No'}    // Ternary
{[1, 2, 3].map(n => n * 2)}  // Array method
{Math.random()}              // Math function

// ❌ INVALID - These don't return values:
{if (x > 5) { return 'big' }} // if statement
{for (let i = 0; i < 5; i++) {}} // for loop
{let x = 5}                   // Variable declaration
```

### **ES6 Template Literals: A Better Way with Strings**

Before we combine template literals with JSX, let's understand what they are.

#### **The Old Way: String Concatenation**
```javascript
const name = "John";
const age = 25;

// Traditional concatenation
const message = "Hello, my name is " + name + " and I am " + age + " years old.";
```

#### **The ES6 Way: Template Literals**
```javascript
const name = "John";
const age = 25;

// Template literal (using backticks ``)
const message = `Hello, my name is ${name} and I am ${age} years old.`;
```

#### **Template Literal Features:**

1. **Embed variables with `${}`**
```javascript
const price = 19.99;
const item = "book";
console.log(`The ${item} costs $${price}`);
// Output: The book costs $19.99
```

2. **Multi-line strings**
```javascript
// Old way
const oldWay = "Line 1\n" +
               "Line 2\n" +
               "Line 3";

// New way
const newWay = `Line 1
Line 2
Line 3`;
```

3. **Expressions inside `${}`**
```javascript
const a = 5;
const b = 10;
console.log(`The sum is ${a + b}`);
// Output: The sum is 15
```

4. **Function calls inside `${}`**
```javascript
function double(x) {
  return x * 2;
}

console.log(`Double of 5 is ${double(5)}`);
// Output: Double of 5 is 10
```

### **Combining Template Literals with JSX**

This is where it gets powerful! You can use template literals **inside** JSX curly braces.

#### **Example 1: Dynamic Classes**
```jsx
function Button({ type, isDisabled }) {
  // Using template literal for dynamic className
  const buttonClass = `btn btn-${type} ${isDisabled ? 'disabled' : ''}`;
  
  return (
    <button className={buttonClass}>
      Click me
    </button>
  );
}

// Usage
<Button type="primary" isDisabled={false} />
// Renders: <button class="btn btn-primary">Click me</button>
```

#### **Example 2: Dynamic URLs**
```jsx
function UserAvatar({ userId, userName }) {
  const avatarUrl = `https://api.example.com/avatars/${userId}`;
  const altText = `${userName}'s avatar`;
  
  return (
    <img 
      src={avatarUrl}
      alt={altText}
      className={`avatar avatar-${userId}`}
    />
  );
}
```

#### **Example 3: Complex String Building**
```jsx
function ProductCard({ product }) {
  const formattedPrice = `$${product.price.toFixed(2)}`;
  const discountMessage = product.onSale 
    ? `On sale! Was $${product.originalPrice}, now ${formattedPrice}`
    : `Price: ${formattedPrice}`;
  
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p className="price">{discountMessage}</p>
      <p className="sku">SKU: {`PRD-${product.id.toString().padStart(6, '0')}`}</p>
    </div>
  );
}
```

### **Common Patterns and Examples**

#### **Pattern 1: Conditional Styling**
```jsx
function Alert({ type, message }) {
  // Template literal for dynamic classes
  const alertClass = `alert alert-${type}`;
  
  return (
    <div className={alertClass}>
      {message}
    </div>
  );
}

// Usage
<Alert type="success" message="Operation completed!" />
<Alert type="error" message="Something went wrong!" />
```

#### **Pattern 2: Dynamic URLs and Paths**
```jsx
function ImageGallery({ images, category }) {
  return (
    <div className="gallery">
      {images.map((image, index) => {
        const imagePath = `/images/${category}/${image.filename}`;
        const caption = `Image ${index + 1}: ${image.title}`;
        
        return (
          <div key={image.id} className="gallery-item">
            <img 
              src={imagePath} 
              alt={caption}
            />
            <p>{`${image.title} - ${image.date}`}</p>
          </div>
        );
      })}
    </div>
  );
}
```

#### **Pattern 3: Formatting Data Display**
```jsx
function Invoice({ invoice }) {
  const formattedDate = `${invoice.date.getMonth() + 1}/${invoice.date.getDate()}/${invoice.date.getFullYear()}`;
  const total = `$${invoice.total.toFixed(2)}`;
  const statusClass = `status status-${invoice.status.toLowerCase()}`;
  
  return (
    <div className="invoice">
      <h3>Invoice #{`INV-${invoice.number.toString().padStart(5, '0')}`}</h3>
      <p>Date: {formattedDate}</p>
      <p>Total: <strong>{total}</strong></p>
      <p className={statusClass}>
        Status: {invoice.status.toUpperCase()}
      </p>
    </div>
  );
}
```

### **Practice Exercises**

#### **Exercise 1: User Welcome Message**
Create a component that shows a personalized welcome message:
```jsx
function WelcomeMessage() {
  const userName = "Maria";
  const loginCount = 42;
  const isPremium = true;
  
  return (
    <div className="welcome">
      {/* 
        Show: 
        "Welcome back, Maria! You've logged in 42 times.
        Thank you for being a Premium member!"
        
        For non-premium: "Consider upgrading to Premium!"
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function WelcomeMessage() {
  const userName = "Maria";
  const loginCount = 42;
  const isPremium = true;
  
  return (
    <div className="welcome">
      <h2>{`Welcome back, ${userName}!`}</h2>
      <p>{`You've logged in ${loginCount} times.`}</p>
      {isPremium ? (
        <p className="premium">Thank you for being a Premium member!</p>
      ) : (
        <p className="upgrade">Consider upgrading to Premium!</p>
      )}
    </div>
  );
}
```

#### **Exercise 2: Price Calculator**
```jsx
function PriceDisplay() {
  const basePrice = 49.99;
  const taxRate = 0.08; // 8%
  const quantity = 3;
  
  // Calculate subtotal, tax, and total
  const subtotal = basePrice * quantity;
  const tax = subtotal * taxRate;
  const total = subtotal + tax;
  
  return (
    <div>
      <h3>Order Summary</h3>
      {/* Display calculations using template literals */}
    </div>
  );
}
```

### **Common Mistakes to Avoid**

#### **Mistake 1: Forgetting the $ in Template Literals**
```jsx
// ❌ WRONG
const message = `Price: {price}`; // Won't work in template literal

// ✅ CORRECT
const message = `Price: ${price}`; // Use $ before curly braces
```

#### **Mistake 2: Using Template Literals Outside JSX Braces**
```jsx
// ❌ WRONG
<p>`Hello, ${name}`</p> // Quotes will show in output

// ✅ CORRECT
<p>{`Hello, ${name}`}</p> // Put template literal inside JSX braces
```

#### **Mistake 3: Complex Logic Inside JSX**
```jsx
// ❌ HARD TO READ
<div>
  {`Welcome ${user.firstName} ${user.lastName}, you have ${user.notifications.filter(n => !n.read).length} unread ${user.notifications.filter(n => !n.read).length === 1 ? 'notification' : 'notifications'}`}
</div>

// ✅ BETTER - Calculate outside JSX
const fullName = `${user.firstName} ${user.lastName}`;
const unreadCount = user.notifications.filter(n => !n.read).length;
const notificationText = unreadCount === 1 ? 'notification' : 'notifications';

<div>
  {`Welcome ${fullName}, you have ${unreadCount} unread ${notificationText}`}
</div>
```

### **Real-World Example: E-commerce Product Display**

```jsx
function ProductDisplay({ product, currency = 'USD' }) {
  // Format price based on currency
  const formatPrice = (price) => {
    const symbols = {
      USD: '$',
      EUR: '€',
      GBP: '£'
    };
    return `${symbols[currency] || '$'}${price.toFixed(2)}`;
  };
  
  // Calculate discount percentage
  const discountPercent = product.originalPrice 
    ? Math.round((1 - product.price / product.originalPrice) * 100)
    : 0;
  
  // Build dynamic CSS class
  const productClass = `product ${product.category.toLowerCase()} ${product.featured ? 'featured' : ''}`;
  
  return (
    <div className={productClass}>
      {/* Product badge using template literal */}
      {product.isNew && (
        <span className={`badge badge-new`}>NEW</span>
      )}
      
      {discountPercent > 0 && (
        <span className={`badge badge-discount`}>
          {`-${discountPercent}%`}
        </span>
      )}
      
      <h3>{product.name}</h3>
      
      {/* Price display with template literals */}
      <div className="price">
        <span className="current-price">
          {formatPrice(product.price)}
        </span>
        
        {product.originalPrice && (
          <span className="original-price">
            {`Was ${formatPrice(product.originalPrice)}`}
          </span>
        )}
      </div>
      
      {/* Rating with template literal */}
      <div className="rating">
        {`⭐ ${product.rating.toFixed(1)} (${product.reviewCount} reviews)`}
      </div>
      
      {/* Stock status */}
      <p className={`stock ${product.inStock ? 'in-stock' : 'out-of-stock'}`}>
        {product.inStock 
          ? `${product.stockCount} items in stock`
          : 'Out of stock'}
      </p>
    </div>
  );
}
```

### **Template Literal Tips and Tricks**

#### **1. Tagged Template Literals (Advanced)**
```javascript
// Advanced feature - functions that process template literals
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    return result + str + (values[i] ? `<mark>${values[i]}</mark>` : '');
  }, '');
}

const name = "John";
const age = 30;
const message = highlight`Hello ${name}, you are ${age} years old`;
// Result: "Hello <mark>John</mark>, you are <mark>30</mark> years old"
```

#### **2. Nested Template Literals**
```jsx
function ComplexMessage({ user, items }) {
  const itemCount = items.length;
  const itemList = items.map(item => `• ${item}`).join('\n');
  
  return (
    <div>
      <pre>
        {`Hello ${user.name},

You have ${itemCount} item${itemCount !== 1 ? 's' : ''} in your cart:

${itemList}

Total: $${items.reduce((sum, item) => sum + item.price, 0).toFixed(2)}
Thank you for shopping with us!`}
      </pre>
    </div>
  );
}
```

### **Quick Reference Guide**

#### **JSX with JavaScript:**
```jsx
// Variable
<p>{variableName}</p>

// Expression
<p>{2 + 2}</p>

// Function call
<p>{formatDate(new Date())}</p>

// Ternary operator
<p>{isTrue ? 'Yes' : 'No'}</p>

// Template literal
<p>{`Hello, ${name}!`}</p>
```

#### **Template Literal Syntax:**
```javascript
// Basic
`Text ${variable} more text`

// Multi-line
`Line 1
Line 2
Line 3`

// Expression
`Result: ${5 * 10}`

// Nested
`Outer ${`Inner ${variable}`}`
```

### **Practice Challenge**

**Challenge: Create a Weather Widget**
```jsx
function WeatherWidget() {
  const city = "San Francisco";
  const temperature = 65;
  const condition = "Sunny";
  const humidity = 65; // percentage
  const windSpeed = 12; // mph
  
  // Use template literals to create:
  // 1. A dynamic class for temperature (hot/warm/cold)
  // 2. Formatted strings for display
  // 3. Condition emoji based on weather
  
  return (
    <div className="weather-widget">
      {/* Your implementation here */}
    </div>
  );
}
```

**Hints:**
- Temperature class: `temp-hot` (>80), `temp-warm` (60-80), `temp-cold` (<60)
- Emoji: ☀️ for Sunny, ☁️ for Cloudy, 🌧️ for Rainy
- Display format: `San Francisco: 65°F, Sunny`

### **Summary**

**Key Takeaways:**
1. **`{}` in JSX** = JavaScript expression evaluator
2. **Template literals** = Clean string formatting with backticks ``
3. **`${}` in template literals** = Embed variables/expressions
4. **Combine both** for dynamic, readable JSX

**Remember:**
- Keep complex logic outside JSX for readability
- Use template literals for string building
- Everything inside `{}` must return a value

### **Next Steps Practice**
Create a CodeSandbox with:
1. A user profile component using variables
2. A shopping cart with calculations
3. Dynamic CSS classes using template literals

**Next Up:** We'll practice JavaScript expressions in JSX with hands-on exercises!

---

**Ready for Topic 7: "Javascript Expressions in JSX Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/JavaScript Expressions in JSX Practice|JavaScript Expressions in JSX Practice]]
- [[Web Development/React/React Topics/Introduction to JSX and Babel|Introduction to JSX and Babel]]
- [[Web Development/React/JSX/JSX Guide|JSX Guide]]
