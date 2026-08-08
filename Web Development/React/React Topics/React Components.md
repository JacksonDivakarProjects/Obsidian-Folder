## **11. React Components - Complete Beginner's Guide**

### **Introduction**
Welcome to the heart of React! **Components** are the building blocks of every React application. Think of them as LEGO bricks - small, reusable pieces that come together to build something amazing. Today, we'll learn everything about React components from the ground up.

### **What are React Components?**

**Components** are independent, reusable pieces of code that return React elements (JSX) to be rendered on the screen.

#### **Simple Analogy:**
Imagine building a house:
- **House** = Your React App
- **Rooms** = Components (Kitchen, Bedroom, Bathroom)
- **Furniture** = Smaller components (Table, Chair, Bed)

Each component manages its own structure, style, and behavior.

### **Why Components Matter**

#### **Benefits of Component-Based Architecture:**
1. **Reusability**: Write once, use everywhere
2. **Maintainability**: Fix bugs in one place
3. **Separation of Concerns**: Each component does one thing well
4. **Team Collaboration**: Different developers can work on different components
5. **Testing**: Test components in isolation

### **Types of React Components**

There are two main ways to create components:

#### **1. Function Components (Modern)**
```jsx
// Simple Function Component
function Welcome() {
  return <h1>Hello, World!</h1>;
}
```

#### **2. Class Components (Legacy)**
```jsx
// Class Component (we'll cover this later)
class Welcome extends React.Component {
  render() {
    return <h1>Hello, World!</h1>;
  }
}
```

**For beginners:** We'll focus on **Function Components** as they're simpler and modern React's standard.

### **Creating Your First Component**

#### **Step-by-Step Creation:**

```jsx
// 1. Define the component (always start with capital letter)
function Greeting() {
  // 2. Return JSX
  return (
    <div>
      <h1>Welcome to React!</h1>
      <p>This is my first component.</p>
    </div>
  );
}

// 3. Export the component (so other files can use it)
export default Greeting;
```

#### **Component Naming Rules:**
```jsx
// ✅ CORRECT - PascalCase
function UserProfile() { }
function NavigationBar() { }
function ShoppingCart() { }

// ❌ WRONG - camelCase or lowercase
function userProfile() { }  // Won't be recognized as component
function navigation_bar() { } // Not conventional
```

### **Using Components**

Components can be used inside other components:

```jsx
// Header.js
function Header() {
  return (
    <header>
      <h1>My Awesome App</h1>
    </header>
  );
}

// App.js
function App() {
  return (
    <div>
      <Header />  {/* Using the Header component */}
      <main>
        <p>Welcome to my app!</p>
      </main>
    </div>
  );
}
```

### **Component Structure: The Complete Picture**

```jsx
// 1. Import dependencies
import React from 'react';
import './Header.css';

// 2. Define the component
function Header() {
  // 3. Component logic (if any)
  const currentYear = new Date().getFullYear();
  
  // 4. Return JSX
  return (
    <header className="header">
      <h1>My App {currentYear}</h1>
      <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
    </header>
  );
}

// 5. Export the component
export default Header;
```

### **Component Hierarchy: Parent and Child Components**

```jsx
// Child Component
function Button() {
  return <button>Click Me</button>;
}

// Parent Component
function App() {
  return (
    <div>
      <h1>My App</h1>
      <Button /> {/* Button is a child of App */}
      <Button /> {/* Reusing the same component */}
      <Button /> {/* Three instances of the same component */}
    </div>
  );
}
```

### **Real-World Component Examples**

#### **Example 1: User Card Component**
```jsx
function UserCard({ user }) {
  return (
    <div className="user-card">
      <img 
        src={user.avatar} 
        alt={user.name}
        className="avatar"
      />
      <div className="user-info">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
        <p className="role">{user.role}</p>
      </div>
      <button className="message-btn">
        Message
      </button>
    </div>
  );
}

// Usage
const user = {
  name: "Alex Johnson",
  email: "alex@example.com",
  avatar: "https://example.com/avatar.jpg",
  role: "Frontend Developer"
};

function App() {
  return <UserCard user={user} />;
}
```

#### **Example 2: Product Card Component**
```jsx
function ProductCard({ product }) {
  return (
    <div className="product-card">
      <img 
        src={product.image} 
        alt={product.name}
        className="product-image"
      />
      <div className="product-details">
        <h3>{product.name}</h3>
        <p className="description">{product.description}</p>
        <div className="price-section">
          <span className="price">${product.price}</span>
          {product.oldPrice && (
            <span className="old-price">${product.oldPrice}</span>
          )}
        </div>
        <button className="add-to-cart">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
```

#### **Example 3: Navigation Bar Component**
```jsx
function Navbar() {
  const navItems = ['Home', 'Products', 'About', 'Contact'];
  
  return (
    <nav className="navbar">
      <div className="logo">
        <h2>MyStore</h2>
      </div>
      
      <ul className="nav-links">
        {navItems.map(item => (
          <li key={item}>
            <a href={`/${item.toLowerCase()}`}>
              {item}
            </a>
          </li>
        ))}
      </ul>
      
      <div className="nav-actions">
        <button className="search-btn">
          🔍 Search
        </button>
        <button className="cart-btn">
          🛒 Cart (0)
        </button>
      </div>
    </nav>
  );
}
```

### **Component Composition: Building Complex UIs**

```jsx
// Small, focused components
function Avatar({ src, alt }) {
  return <img src={src} alt={alt} className="avatar" />;
}

function UserName({ name }) {
  return <h3>{name}</h3>;
}

function UserBio({ bio }) {
  return <p className="bio">{bio}</p>;
}

// Compose them into larger components
function UserProfile() {
  return (
    <div className="user-profile">
      <Avatar 
        src="https://example.com/avatar.jpg" 
        alt="User avatar" 
      />
      <UserName name="Jane Smith" />
      <UserBio bio="Frontend developer passionate about React" />
    </div>
  );
}
```

### **Components with Logic**

Components can contain JavaScript logic:

```jsx
function Counter() {
  // Component logic
  const count = 0;
  const maxCount = 10;
  const isMaxReached = count >= maxCount;
  
  return (
    <div className="counter">
      <h3>Current Count: {count}</h3>
      <p>Maximum: {maxCount}</p>
      
      {isMaxReached ? (
        <p className="warning">Maximum count reached!</p>
      ) : (
        <button>Increment</button>
      )}
    </div>
  );
}
```

### **Components in Different Files**

#### **File Structure:**
```
src/
├── components/
│   ├── Header.js
│   ├── Footer.js
│   └── Button.js
├── App.js
└── index.js
```

#### **Header.js:**
```jsx
// Header.js
function Header() {
  return (
    <header>
      <h1>My Application</h1>
    </header>
  );
}

export default Header;
```

#### **App.js:**
```jsx
// App.js
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <div>
      <Header />
      <main>Content goes here</main>
      <Footer />
    </div>
  );
}

export default App;
```

### **Default vs Named Exports**

#### **Default Export (One per file):**
```jsx
// Button.js - Default export
function Button() {
  return <button>Click me</button>;
}

export default Button;

// Import in another file
import Button from './Button';
```

#### **Named Exports (Multiple per file):**
```jsx
// utils.js - Multiple named exports
export function formatDate(date) {
  return date.toLocaleDateString();
}

export function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Import in another file
import { formatDate, capitalize } from './utils';
```

### **Component Lifecycle (Conceptual)**

Think of components like living organisms:
1. **Birth**: Component is created and rendered
2. **Life**: Component updates based on data changes
3. **Death**: Component is removed from screen

We'll learn about state and effects later to manage this lifecycle.

### **Practice Exercises**

#### **Exercise 1: Create a Social Media Post Component**
```jsx
function SocialMediaPost() {
  // Create a post component with:
  // - User avatar and name
  // - Post content
  // - Post image
  // - Like, comment, share buttons
  // - Timestamp
  
  return (
    <div className="post">
      {/* Your code here */}
    </div>
  );
}
```

**Solution:**
```jsx
function SocialMediaPost() {
  return (
    <div className="post">
      <div className="post-header">
        <img 
          src="https://example.com/avatar.jpg" 
          alt="User avatar"
          className="post-avatar"
        />
        <div className="post-user-info">
          <h4>Alex Johnson</h4>
          <span className="post-time">2 hours ago</span>
        </div>
      </div>
      
      <div className="post-content">
        <p>Just learned about React components! They're amazing building blocks for web applications. #React #WebDev</p>
      </div>
      
      <img 
        src="https://example.com/post-image.jpg" 
        alt="Post content"
        className="post-image"
      />
      
      <div className="post-stats">
        <span>👍 245 Likes</span>
        <span>💬 42 Comments</span>
        <span>↪️ 18 Shares</span>
      </div>
      
      <div className="post-actions">
        <button className="like-btn">Like</button>
        <button className="comment-btn">Comment</button>
        <button className="share-btn">Share</button>
      </div>
    </div>
  );
}
```

#### **Exercise 2: Create a Weather Widget Component**
```jsx
function WeatherWidget() {
  // Create a weather widget showing:
  // - Location
  // - Current temperature
  // - Weather condition (sunny, rainy, etc.)
  // - High and low temperatures
  // - Weather icon
  
  return (
    <div className="weather-widget">
      {/* Your code here */}
    </div>
  );
}
```

### **Component Best Practices**

#### **1. Single Responsibility Principle**
```jsx
// ❌ BAD - Too many responsibilities
function UserDashboard() {
  // Handles user profile, settings, notifications, etc.
}

// ✅ GOOD - Each component does one thing
function UserProfile() { }
function UserSettings() { }
function Notifications() { }
```

#### **2. Keep Components Small**
```jsx
// ❌ BAD - Giant component
function MassiveComponent() {
  return (
    // 200+ lines of JSX
  );
}

// ✅ GOOD - Break into smaller components
function ParentComponent() {
  return (
    <Header />
    <Sidebar />
    <MainContent />
    <Footer />
  );
}
```

#### **3. Descriptive Names**
```jsx
// ❌ BAD - Unclear names
function Comp1() { }
function MyComponent() { }
function Stuff() { }

// ✅ GOOD - Clear, descriptive names
function ProductCard() { }
function UserRegistrationForm() { }
function NavigationMenu() { }
```

#### **4. Use Meaningful JSX**
```jsx
// ❌ BAD - Just divs everywhere
<div>
  <div>
    <div>Content</div>
  </div>
</div>

// ✅ GOOD - Semantic HTML
<article>
  <header>
    <h2>Article Title</h2>
  </header>
  <section>
    <p>Article content</p>
  </section>
  <footer>
    <p>Article footer</p>
  </footer>
</article>
```

### **Common Component Patterns**

#### **1. Container/Presentational Pattern**
```jsx
// Container Component (handles logic)
function UserListContainer() {
  const [users, setUsers] = useState([]);
  
  useEffect(() => {
    fetchUsers().then(setUsers);
  }, []);
  
  return <UserList users={users} />;
}

// Presentational Component (handles UI)
function UserList({ users }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

#### **2. Layout Components**
```jsx
function Layout({ children, sidebar }) {
  return (
    <div className="layout">
      <Header />
      <div className="content">
        <main>{children}</main>
        <aside>{sidebar}</aside>
      </div>
      <Footer />
    </div>
  );
}

// Usage
function App() {
  return (
    <Layout sidebar={<Sidebar />}>
      <h1>Main Content</h1>
      <p>This is the main content area</p>
    </Layout>
  );
}
```

#### **3. Higher-Order Components (HOC) Pattern**
```jsx
// A component that enhances another component
function withLoading(Component) {
  return function EnhancedComponent({ isLoading, ...props }) {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    return <Component {...props} />;
  };
}

// Usage
const UserProfileWithLoading = withLoading(UserProfile);
```

### **Debugging Components**

#### **Common Errors and Solutions:**

**Error 1: Component Not Rendering**
```jsx
// ❌ Forgot to return JSX
function MyComponent() {
  <div>Hello</div>  // Missing return
}

// ✅ Always return JSX
function MyComponent() {
  return <div>Hello</div>;
}
```

**Error 2: Wrong Component Name**
```jsx
// ❌ Using lowercase
<mycomponent />  // React thinks this is HTML element

// ✅ Use PascalCase
<MyComponent />
```

**Error 3: Missing Export**
```jsx
// ❌ Forgot to export
function MyComponent() { }

// ✅ Export the component
export default MyComponent;
```

### **Component Visualization**

Think of components as a tree structure:
```
App
├── Header
│   ├── Logo
│   ├── Navigation
│   │   ├── NavItem
│   │   ├── NavItem
│   │   └── NavItem
│   └── SearchBar
├── MainContent
│   ├── Sidebar
│   │   ├── Widget
│   │   └── Widget
│   └── Article
│       ├── Title
│       ├── Author
│       └── Content
└── Footer
    ├── Links
    └── Copyright
```

### **Interactive Component Example**

```jsx
function InteractiveCounter() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);
  
  return (
    <div className="counter">
      <h2>Interactive Counter</h2>
      <div className="count-display">
        <span className="count">{count}</span>
      </div>
      <div className="controls">
        <button onClick={decrement} disabled={count <= 0}>
          Decrement
        </button>
        <button onClick={reset}>
          Reset
        </button>
        <button onClick={increment}>
          Increment
        </button>
      </div>
      <p className="status">
        {count === 0 && "Start counting!"}
        {count > 0 && count < 10 && "Keep going!"}
        {count >= 10 && "Great job!"}
      </p>
    </div>
  );
}
```

### **Component Documentation Practice**

Always document your components:

```jsx
/**
 * Button Component
 * 
 * A reusable button component with various styles and sizes.
 * 
 * @param {Object} props
 * @param {string} props.children - Button text/content
 * @param {string} props.variant - Button style: 'primary', 'secondary', 'danger'
 * @param {string} props.size - Button size: 'small', 'medium', 'large'
 * @param {boolean} props.disabled - Whether the button is disabled
 * @param {function} props.onClick - Click handler function
 * @returns {JSX.Element} Rendered button component
 */
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick 
}) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Button;
```

### **Practice Challenge: Build a Todo Component**

```jsx
function TodoApp() {
  // Create a Todo application with:
  // 1. Input to add new todos
  // 2. List of todos
  // 3. Each todo should have:
  //    - Text
  //    - Checkbox to mark complete
  //    - Delete button
  // 4. Show count of active todos
  // 5. Filter options: All, Active, Completed
  
  return (
    <div className="todo-app">
      <h1>Todo List</h1>
      {/* Your implementation here */}
    </div>
  );
}
```

**Hints:**
- Create separate components: `TodoInput`, `TodoItem`, `TodoList`, `TodoFilter`
- Use state to manage todos
- Style with CSS classes

### **Summary**

**Key Takeaways:**
1. **Components** are reusable building blocks of React apps
2. **Function components** are the modern standard
3. **Components must return JSX** with a single parent element
4. **Component names must be PascalCase**
5. **Export components** to use them in other files
6. **Break complex UIs** into smaller components
7. **Components can contain logic** and state (coming next!)

**Remember:** Think in components! Every piece of UI should be a component or composed of components.

---

**Ready for Topic 12: "React Components Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Class Components vs. Functional Components|Class Components vs. Functional Components]]
- [[Web Development/React/React Topics/React Props|React Props]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
- [[Web Development/React/React Topics/Mapping Data to Components|Mapping Data to Components]]
