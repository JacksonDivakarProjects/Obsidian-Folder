## **37. Class Components vs. Functional Components - Complete Beginner's Guide**

### **Introduction**
Welcome to the **Great Debate** in React! Understanding the difference between Class Components and Functional Components is crucial. While modern React uses Functional Components almost exclusively, you'll still encounter Class Components in older codebases. Let's understand both so you can work with any React code you encounter!

### **Quick History Lesson**

- **2013-2018:** Class Components were king
- **2019:** React Hooks introduced (useState, useEffect)
- **2020-Present:** Functional Components + Hooks are standard

**Today:** Use Functional Components for new projects. Know Class Components to read old code.

### **The Simple Comparison**

| Aspect | Class Components | Functional Components |
|--------|-----------------|----------------------|
| **Syntax** | `class Component extends React.Component` | `function Component()` |
| **State** | `this.state` and `this.setState()` | `useState()` hook |
| **Lifecycle** | `componentDidMount()`, `componentDidUpdate()`, etc. | `useEffect()` hook |
| **Props** | `this.props` | Function parameters |
| **`this` keyword** | Required | Not used |
| **Complexity** | More verbose | Cleaner, simpler |
| **Modern Usage** | Legacy | Standard |

### **1. Functional Components (Modern Way)**

#### **Basic Structure:**
```jsx
import React from 'react';

// Simple Functional Component
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}

// With arrow function (also common)
const Welcome = (props) => {
  return <h1>Hello, {props.name}</h1>;
};

// Usage
<Welcome name="Alice" />
```

#### **With State (using Hooks):**
```jsx
import React, { useState } from 'react';

function Counter() {
  // State with useState hook
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

#### **With Side Effects (using Hooks):**
```jsx
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  // Similar to componentDidMount and componentDidUpdate
  useEffect(() => {
    // Fetch user data
    fetchUser(userId).then(setUser);
  }, [userId]); // Re-run when userId changes
  
  if (!user) return <div>Loading...</div>;
  
  return <div>{user.name}</div>;
}
```

### **2. Class Components (Legacy Way)**

#### **Basic Structure:**
```jsx
import React from 'react';

// Class Component
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
```

#### **With State:**
```jsx
class Counter extends React.Component {
  // Initialize state in constructor
  constructor(props) {
    super(props); // Always call super(props) first!
    this.state = {
      count: 0
    };
  }
  
  // Update state with setState
  increment = () => {
    this.setState({
      count: this.state.count + 1
    });
  };
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>
          Increment
        </button>
      </div>
    );
  }
}
```

#### **With Lifecycle Methods:**
```jsx
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null
    };
  }
  
  // Called after component is mounted (added to DOM)
  componentDidMount() {
    this.fetchUser(this.props.userId);
  }
  
  // Called when props change
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser(this.props.userId);
    }
  }
  
  // Called before component is removed
  componentWillUnmount() {
    // Cleanup (cancel API calls, remove event listeners)
  }
  
  fetchUser = (userId) => {
    // Fetch user data
    fetchUser(userId).then(user => {
      this.setState({ user });
    });
  };
  
  render() {
    if (!this.state.user) {
      return <div>Loading...</div>;
    }
    
    return <div>{this.state.user.name}</div>;
  }
}
```

### **Side-by-Side Comparison**

#### **Example 1: Simple Component**
```jsx
// FUNCTIONAL COMPONENT (Modern)
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// CLASS COMPONENT (Legacy)
class Greeting extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}!</h1>;
  }
}
```

#### **Example 2: Counter with State**
```jsx
// FUNCTIONAL COMPONENT
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}

// CLASS COMPONENT
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.handleClick}>
          Click me
        </button>
      </div>
    );
  }
}
```

#### **Example 3: Form with State**
```jsx
// FUNCTIONAL COMPONENT
function LoginForm() {
  const [form, setForm] = useState({
    username: '',
    password: ''
  });
  
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };
  
  return (
    <form>
      <input
        name="username"
        value={form.username}
        onChange={handleChange}
      />
      <input
        name="password"
        type="password"
        value={form.password}
        onChange={handleChange}
      />
    </form>
  );
}

// CLASS COMPONENT
class LoginForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: ''
    };
  }
  
  handleChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };
  
  render() {
    return (
      <form>
        <input
          name="username"
          value={this.state.username}
          onChange={this.handleChange}
        />
        <input
          name="password"
          type="password"
          value={this.state.password}
          onChange={this.handleChange}
        />
      </form>
    );
  }
}
```

### **Converting Class Components to Functional Components**

You'll often need to convert old Class Components to Functional Components. Here's how:

#### **Step-by-Step Conversion:**

**Original Class Component:**
```jsx
class UserProfile extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
      loading: true,
      error: null
    };
  }
  
  componentDidMount() {
    this.fetchUser(this.props.userId);
  }
  
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser(this.props.userId);
    }
  }
  
  componentWillUnmount() {
    // Cleanup if needed
  }
  
  fetchUser = async (userId) => {
    try {
      this.setState({ loading: true });
      const user = await api.getUser(userId);
      this.setState({ user, loading: false });
    } catch (error) {
      this.setState({ error, loading: false });
    }
  };
  
  render() {
    const { user, loading, error } = this.state;
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    if (!user) return null;
    
    return (
      <div>
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    );
  }
}
```

**Converted Functional Component:**
```jsx
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  // 1. Convert state to useState
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 2. Convert lifecycle methods to useEffect
  useEffect(() => {
    let isMounted = true;
    
    const fetchUser = async () => {
      try {
        setLoading(true);
        const userData = await api.getUser(userId);
        
        if (isMounted) {
          setUser(userData);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err);
          setLoading(false);
        }
      }
    };
    
    fetchUser();
    
    // 3. Convert componentWillUnmount to cleanup function
    return () => {
      isMounted = false;
    };
  }, [userId]); // 4. Add dependencies (like componentDidUpdate check)
  
  // 5. Copy render logic
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return null;
  
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### **Lifecycle Methods vs Hooks**

Here's how Class Component lifecycle methods map to Functional Component hooks:

| Class Component Lifecycle | Functional Component Equivalent |
|--------------------------|--------------------------------|
| `constructor()` | `useState()` initialization |
| `componentDidMount()` | `useEffect(() => {}, [])` |
| `componentDidUpdate()` | `useEffect(() => {}, [deps])` |
| `componentWillUnmount()` | `useEffect(() => { return cleanup }, [])` |
| `shouldComponentUpdate()` | `React.memo()` or `useMemo()` |
| `getDerivedStateFromProps()` | Update state during render |
| `getSnapshotBeforeUpdate()` | Rarely needed, use refs |

### **Common Patterns Comparison**

#### **Pattern 1: Event Handlers**
```jsx
// FUNCTIONAL
function Button() {
  const handleClick = () => {
    console.log('Clicked');
  };
  
  return <button onClick={handleClick}>Click</button>;
}

// CLASS
class Button extends React.Component {
  handleClick = () => {
    console.log('Clicked');
  };
  
  render() {
    return <button onClick={this.handleClick}>Click</button>;
  }
}
```

#### **Pattern 2: Conditional Rendering**
```jsx
// FUNCTIONAL
function UserGreeting({ isLoggedIn, userName }) {
  return (
    <div>
      {isLoggedIn ? (
        <h1>Welcome back, {userName}!</h1>
      ) : (
        <h1>Please sign in.</h1>
      )}
    </div>
  );
}

// CLASS
class UserGreeting extends React.Component {
  render() {
    const { isLoggedIn, userName } = this.props;
    
    return (
      <div>
        {isLoggedIn ? (
          <h1>Welcome back, {userName}!</h1>
        ) : (
          <h1>Please sign in.</h1>
        )}
      </div>
    );
  }
}
```

#### **Pattern 3: Lists**
```jsx
// FUNCTIONAL
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
}

// CLASS
class TodoList extends React.Component {
  render() {
    const { todos } = this.props;
    
    return (
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    );
  }
}
```

### **When You Might Still See Class Components**

1. **Old codebases** (written before 2019)
2. **Error Boundaries** (still need Class Components in React 17)
3. **Some third-party libraries** that haven't been updated
4. **Legacy projects** that haven't been migrated

#### **Error Boundary Example (Class Component Required):**
```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    // Update state so the next render shows the fallback UI
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return <h1>Something went wrong.</h1>;
    }
    
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

### **Why Functional Components Won**

#### **Advantages of Functional Components:**
1. **Less code** - More concise and readable
2. **No `this` confusion** - No binding issues
3. **Easier to test** - Pure functions are predictable
4. **Better performance** - No instance creation
5. **Hooks** - Reusable stateful logic
6. **Future of React** - All new features target Functional Components

#### **Common `this` Problems in Class Components:**
```jsx
class ProblemComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    
    // Need to bind this for class methods
    this.handleClick = this.handleClick.bind(this);
  }
  
  // Or use arrow function to auto-bind
  handleClick = () => {
    // Can access this.state here
    this.setState({ count: this.state.count + 1 });
  };
  
  // Regular method - loses this context
  problematicMethod() {
    // ❌ this is undefined when called as callback
    console.log(this.state.count);
  }
  
  render() {
    return (
      <div>
        <button onClick={this.handleClick}>Works</button>
        <button onClick={this.problematicMethod}>Broken</button>
        <button onClick={() => this.problematicMethod()}>Works with wrapper</button>
      </div>
    );
  }
}
```

### **Migration Guide: Class → Functional**

If you need to update old code, follow these steps:

1. **Change the declaration:**
   ```jsx
   // From:
   class MyComponent extends React.Component
   
   // To:
   function MyComponent(props)
   ```

2. **Convert state:**
   ```jsx
   // From:
   this.state = { count: 0 }
   this.setState({ count: 1 })
   
   // To:
   const [count, setCount] = useState(0)
   setCount(1)
   ```

3. **Convert lifecycle methods:**
   ```jsx
   // From:
   componentDidMount() { /* code */ }
   componentDidUpdate() { /* code */ }
   componentWillUnmount() { /* code */ }
   
   // To:
   useEffect(() => {
     // componentDidMount + componentDidUpdate
     
     return () => {
       // componentWillUnmount
     };
   }, [dependencies]);
   ```

4. **Convert `this.props` to `props`:**
   ```jsx
   // From:
   this.props.name
   
   // To:
   props.name
   // Or destructure: function MyComponent({ name })
   ```

### **Practical Example: Complete Conversion**

**Before (Class Component):**
```jsx
class ProductDetail extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      product: null,
      loading: true,
      quantity: 1
    };
  }
  
  componentDidMount() {
    this.fetchProduct(this.props.productId);
  }
  
  componentDidUpdate(prevProps) {
    if (prevProps.productId !== this.props.productId) {
      this.fetchProduct(this.props.productId);
    }
  }
  
  fetchProduct = async (id) => {
    this.setState({ loading: true });
    try {
      const product = await api.getProduct(id);
      this.setState({ product, loading: false });
    } catch (error) {
      console.error('Failed to fetch product:', error);
      this.setState({ loading: false });
    }
  };
  
  handleQuantityChange = (e) => {
    this.setState({ quantity: parseInt(e.target.value) });
  };
  
  addToCart = () => {
    const { product, quantity } = this.state;
    this.props.onAddToCart(product.id, quantity);
  };
  
  render() {
    const { product, loading, quantity } = this.state;
    
    if (loading) return <div>Loading product...</div>;
    if (!product) return <div>Product not found</div>;
    
    return (
      <div className="product-detail">
        <h2>{product.name}</h2>
        <p>${product.price}</p>
        <div>
          <label>
            Quantity:
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={this.handleQuantityChange}
            />
          </label>
        </div>
        <button onClick={this.addToCart}>
          Add to Cart
        </button>
      </div>
    );
  }
}
```

**After (Functional Component):**
```jsx
import { useState, useEffect } from 'react';

function ProductDetail({ productId, onAddToCart }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchProduct = async () => {
      setLoading(true);
      try {
        const productData = await api.getProduct(productId);
        if (isMounted) {
          setProduct(productData);
          setLoading(false);
        }
      } catch (error) {
        console.error('Failed to fetch product:', error);
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    fetchProduct();
    
    return () => {
      isMounted = false;
    };
  }, [productId]);
  
  const handleQuantityChange = (e) => {
    setQuantity(parseInt(e.target.value));
  };
  
  const addToCart = () => {
    onAddToCart(product.id, quantity);
  };
  
  if (loading) return <div>Loading product...</div>;
  if (!product) return <div>Product not found</div>;
  
  return (
    <div className="product-detail">
      <h2>{product.name}</h2>
      <p>${product.price}</p>
      <div>
        <label>
          Quantity:
          <input
            type="number"
            min="1"
            value={quantity}
            onChange={handleQuantityChange}
          />
        </label>
      </div>
      <button onClick={addToCart}>
        Add to Cart
      </button>
    </div>
  );
}
```

### **Quick Reference: Syntax Comparison**

```jsx
// FUNCTIONAL COMPONENT SYNTAX
function Component(props) {
  // State
  const [state, setState] = useState(initialValue);
  
  // Effects
  useEffect(() => { /* code */ }, [deps]);
  
  // Return JSX
  return <div>{props.name}</div>;
}

// CLASS COMPONENT SYNTAX
class Component extends React.Component {
  constructor(props) {
    super(props);
    this.state = { /* initial state */ };
  }
  
  componentDidMount() { /* code */ }
  componentDidUpdate() { /* code */ }
  componentWillUnmount() { /* code */ }
  
  render() {
    return <div>{this.props.name}</div>;
  }
}
```

### **Should You Learn Class Components?**

**Yes, but only enough to:**
1. Read and understand old code
2. Convert them to Functional Components
3. Work with Error Boundaries
4. Maintain legacy applications

**For new projects:** Always use Functional Components with Hooks.

### **Summary**

**Class Components (Legacy):**
- Use `class` syntax
- Have `this.state` and `this.setState()`
- Use lifecycle methods
- More verbose
- Needed for Error Boundaries

**Functional Components (Modern):**
- Use `function` syntax
- Use `useState()` for state
- Use `useEffect()` for side effects
- Cleaner, simpler
- Standard for new code

**The Bottom Line:**
- **Learn Functional Components** thoroughly
- **Understand Class Components** enough to read old code
- **Use Functional Components** for all new development
- **Convert Class Components** when maintaining old code

The React community has moved to Functional Components. They're simpler, cleaner, and more powerful with Hooks. But knowing Class Components helps you work with any React codebase you encounter!

---

**Ready for Topic 40: "Javascript ES6 Spread Operator"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/React Components|React Components]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
- [[Web Development/React/React Topics/State in React - Declarative vs. Imperative Programming|State in React (Declarative vs Imperative)]]
