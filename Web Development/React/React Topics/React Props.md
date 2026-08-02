I understand you want to move past the project section. Let me continue with the core React concepts. 

**Note:** Since you want to skip the project practice sessions, I'll continue with the next core topic from your list. Based on the topics you provided, I see you skipped Topic 5, 10, and some others. Let me pick up with:

---

## **20. React Props - Complete Beginner's Guide**

### **Introduction**
Welcome to **Props** - one of React's most important concepts! Props (short for properties) are how data flows between components in React. Think of props as **arguments** you pass to a function, but for React components!

### **What are Props?**

**Props** are read-only data that gets passed from parent components to child components. They allow components to be dynamic and reusable.

#### **Simple Analogy:**
- **Component** = A recipe
- **Props** = Ingredients you pass to the recipe
- **Result** = A customized dish based on the ingredients

### **Why Props are Essential**

Without props, every component would be static and identical. Props make components:
1. **Reusable** - Same component, different data
2. **Dynamic** - Content changes based on props
3. **Maintainable** - Data flow is predictable
4. **Testable** - Easy to test with different props

### **Basic Props Syntax**

#### **Parent Component (Passing Props):**
```jsx
function App() {
  return (
    <div>
      {/* Passing props to ChildComponent */}
      <ChildComponent name="John" age={25} />
      <ChildComponent name="Sarah" age={30} />
      <ChildComponent name="Mike" age={22} />
    </div>
  );
}
```

#### **Child Component (Receiving Props):**
```jsx
function ChildComponent(props) {
  return (
    <div>
      <h1>Hello, {props.name}!</h1>
      <p>You are {props.age} years old.</p>
    </div>
  );
}
```

### **Different Ways to Access Props**

#### **Method 1: Using `props` Parameter (Object)**
```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}</h1>;
}
```

#### **Method 2: Destructuring Props in Function Parameter**
```jsx
function Greeting({ name, age }) {
  return (
    <div>
      <h1>Hello, {name}</h1>
      <p>Age: {age}</p>
    </div>
  );
}
```

#### **Method 3: Destructuring Inside Function Body**
```jsx
function Greeting(props) {
  const { name, age } = props;
  return (
    <div>
      <h1>Hello, {name}</h1>
      <p>Age: {age}</p>
    </div>
  );
}
```

### **Types of Props You Can Pass**

#### **1. String Props**
```jsx
<Component text="Hello World" name="Alice" />
```

#### **2. Number Props**
```jsx
<Component count={42} age={25} rating={4.5} />
```

#### **3. Boolean Props**
```jsx
<Component isActive={true} disabled={false} />
// Shorthand for true:
<Component isActive disabled={false} />
```

#### **4. Array Props**
```jsx
<Component items={['Apple', 'Banana', 'Orange']} 
           numbers={[1, 2, 3, 4, 5]} />
```

#### **5. Object Props**
```jsx
<Component user={{ name: 'John', age: 30, email: 'john@example.com' }} 
           style={{ color: 'red', fontSize: '16px' }} />
```

#### **6. Function Props (Callbacks)**
```jsx
<Component onClick={() => alert('Clicked!')} 
           onChange={(value) => console.log(value)} />
```

#### **7. React Element/Component Props**
```jsx
<Component icon={<span>🔥</span>} 
           header={<h1>Custom Header</h1>} />
```

#### **8. Children Prop (Special)**
```jsx
<Component>
  <p>This is the children content</p>
  <button>Click me</button>
</Component>
```

### **Children Prop: A Special Case**

The `children` prop is special - it contains whatever is between the opening and closing tags of a component.

```jsx
// Parent Component
function Card() {
  return (
    <div className="card">
      <CardHeader>Welcome!</CardHeader>
      <CardContent>
        <p>This is the card content</p>
        <button>Click me</button>
      </CardContent>
    </div>
  );
}

// Child Component using children
function CardHeader({ children }) {
  return <div className="card-header">{children}</div>;
}

function CardContent({ children }) {
  return <div className="card-content">{children}</div>;
}
```

### **Default Props**

You can provide default values for props when they're not provided:

```jsx
// Method 1: Default parameters (ES6)
function Greeting({ name = "Guest", age = 18 }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>Age: {age}</p>
    </div>
  );
}

// Method 2: Using defaultProps property
function Greeting({ name, age }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>Age: {age}</p>
    </div>
  );
}

Greeting.defaultProps = {
  name: "Guest",
  age: 18
};

// Usage - both work the same way
<Greeting /> // Renders: Hello, Guest! Age: 18
<Greeting name="Alice" /> // Renders: Hello, Alice! Age: 18
<Greeting name="Bob" age={25} /> // Renders: Hello, Bob! Age: 25
```

### **Prop Types Validation**

While not required, it's good practice to validate props (using PropTypes or TypeScript):

```jsx
import PropTypes from 'prop-types';

function UserProfile({ name, age, email, isVerified }) {
  return (
    <div>
      <h2>{name} {isVerified && '✓'}</h2>
      <p>Age: {age}</p>
      <p>Email: {email}</p>
    </div>
  );
}

UserProfile.propTypes = {
  name: PropTypes.string.isRequired,
  age: PropTypes.number,
  email: PropTypes.string.isRequired,
  isVerified: PropTypes.bool
};

UserProfile.defaultProps = {
  age: 18,
  isVerified: false
};
```

### **Real-World Examples**

#### **Example 1: Button Component with Props**
```jsx
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  onClick, 
  disabled = false 
}) {
  const baseStyle = {
    padding: size === 'small' ? '8px 16px' : 
             size === 'large' ? '12px 24px' : '10px 20px',
    borderRadius: '4px',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: size === 'small' ? '14px' : 
              size === 'large' ? '18px' : '16px',
    opacity: disabled ? 0.6 : 1
  };
  
  const variantStyles = {
    primary: { backgroundColor: '#007bff', color: 'white' },
    secondary: { backgroundColor: '#6c757d', color: 'white' },
    danger: { backgroundColor: '#dc3545', color: 'white' },
    success: { backgroundColor: '#28a745', color: 'white' }
  };
  
  return (
    <button
      style={{ ...baseStyle, ...variantStyles[variant] }}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

// Usage
<Button variant="primary" onClick={() => alert('Clicked!')}>
  Click Me
</Button>

<Button variant="danger" size="small" disabled>
  Delete
</Button>

<Button variant="success" size="large">
  Save Changes ✓
</Button>
```

#### **Example 2: Product Card Component**
```jsx
function ProductCard({ product, onAddToCart, onWishlist }) {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="description">{product.description}</p>
        <div className="price-section">
          <span className="price">${product.price}</span>
          {product.originalPrice && (
            <span className="original-price">${product.originalPrice}</span>
          )}
        </div>
        <div className="actions">
          <button onClick={() => onAddToCart(product.id)}>
            Add to Cart
          </button>
          <button onClick={() => onWishlist(product.id)}>
            {product.inWishlist ? '❤️' : '🤍'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Usage
const product = {
  id: 1,
  name: "Wireless Headphones",
  description: "Noise cancelling over-ear headphones",
  price: 199.99,
  originalPrice: 249.99,
  image: "headphones.jpg",
  inWishlist: false
};

function App() {
  const handleAddToCart = (productId) => {
    console.log(`Added product ${productId} to cart`);
  };
  
  const handleWishlist = (productId) => {
    console.log(`Toggled wishlist for product ${productId}`);
  };
  
  return (
    <ProductCard 
      product={product}
      onAddToCart={handleAddToCart}
      onWishlist={handleWishlist}
    />
  );
}
```

#### **Example 3: User Profile with Conditional Rendering**
```jsx
function UserProfile({ user, showDetails = true, onFollow }) {
  return (
    <div className="user-profile">
      <div className="avatar-section">
        <img src={user.avatar} alt={user.name} />
        {user.isOnline && <span className="online-dot"></span>}
      </div>
      
      <div className="user-info">
        <h2>{user.name}</h2>
        <p className="username">@{user.username}</p>
        
        {showDetails && (
          <div className="details">
            <p>{user.bio}</p>
            <div className="stats">
              <span>Posts: {user.postCount}</span>
              <span>Followers: {user.followerCount}</span>
              <span>Following: {user.followingCount}</span>
            </div>
          </div>
        )}
        
        <button 
          onClick={() => onFollow(user.id)}
          className={user.isFollowing ? 'following' : 'follow'}
        >
          {user.isFollowing ? 'Following' : 'Follow'}
        </button>
      </div>
    </div>
  );
}

// Usage
const user = {
  id: 1,
  name: "Alex Johnson",
  username: "alexj",
  avatar: "avatar.jpg",
  bio: "Frontend developer passionate about React",
  postCount: 42,
  followerCount: 1250,
  followingCount: 340,
  isOnline: true,
  isFollowing: false
};

function App() {
  const handleFollow = (userId) => {
    console.log(`Followed user ${userId}`);
  };
  
  return (
    <div>
      <UserProfile user={user} onFollow={handleFollow} />
      <UserProfile user={user} showDetails={false} onFollow={handleFollow} />
    </div>
  );
}
```

### **Props vs State: Key Differences**

| Aspect | Props | State |
|--------|-------|-------|
| **Ownership** | Parent component | Component itself |
| **Mutability** | Immutable (read-only) | Mutable (can change) |
| **Purpose** | Pass data down | Manage internal data |
| **Updates** | Parent re-renders | setState() triggers re-render |
| **Access** | Passed as parameters | Managed with useState hook |

### **Common Patterns with Props**

#### **1. Prop Drilling**
```jsx
// Passing props through multiple levels
function App() {
  const user = { name: "John", settings: { theme: "dark" } };
  return <Header user={user} />;
}

function Header({ user }) {
  return <Navbar user={user} />;
}

function Navbar({ user }) {
  return <UserMenu user={user} />;
}

function UserMenu({ user }) {
  return <div>Welcome, {user.name}</div>;
}
```

#### **2. Render Props Pattern**
```jsx
// Component that accepts a function as a prop
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, [url]);
  
  return render({ data, loading });
}

// Usage
<DataFetcher 
  url="/api/users"
  render={({ data, loading }) => {
    if (loading) return <div>Loading...</div>;
    return (
      <ul>
        {data.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    );
  }}
/>
```

#### **3. Higher-Order Components (HOC)**
```jsx
// Function that returns a component with enhanced props
function withAuthentication(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    
    // Authentication logic here
    
    return (
      <WrappedComponent 
        {...props} 
        isAuthenticated={isAuthenticated}
        onLogin={() => setIsAuthenticated(true)}
        onLogout={() => setIsAuthenticated(false)}
      />
    );
  };
}

// Usage
const AuthenticatedButton = withAuthentication(Button);
```

### **Best Practices with Props**

#### **1. Keep Props Minimal**
```jsx
// ❌ Too many props
<UserProfile 
  name="John"
  age={30}
  email="john@example.com"
  address="123 Street"
  phone="555-1234"
  bio="Lorem ipsum..."
  // ... many more
/>

// ✅ Group related props into objects
<UserProfile 
  user={{
    name: "John",
    age: 30,
    email: "john@example.com",
    address: "123 Street",
    phone: "555-1234",
    bio: "Lorem ipsum..."
  }}
/>
```

#### **2. Use Descriptive Prop Names**
```jsx
// ❌ Unclear
<Button c="red" t="Submit" />

// ✅ Clear and descriptive
<Button color="red" text="Submit" />
```

#### **3. Destructure Props for Clarity**
```jsx
// ❌ Hard to read
function Component(props) {
  return (
    <div>
      <h1>{props.user.name}</h1>
      <p>{props.user.bio}</p>
      <button onClick={props.onClick}>{props.buttonText}</button>
    </div>
  );
}

// ✅ Much clearer
function Component({ user, onClick, buttonText }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
      <button onClick={onClick}>{buttonText}</button>
    </div>
  );
}
```

#### **4. Provide Default Props**
```jsx
// Always provide sensible defaults
Button.defaultProps = {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  onClick: () => {}
};
```

### **Common Pitfalls and Solutions**

#### **Pitfall 1: Mutating Props**
```jsx
// ❌ NEVER DO THIS - Props are read-only
function UserProfile({ user }) {
  user.name = "Changed Name"; // This will cause errors
  return <div>{user.name}</div>;
}

// ✅ Create a copy if you need to modify
function UserProfile({ user }) {
  const modifiedUser = { ...user, name: "Changed Name" };
  return <div>{modifiedUser.name}</div>;
}
```

#### **Pitfall 2: Passing New Objects/Arrays Unnecessarily**
```jsx
// ❌ Creates new object on every render
function App() {
  return <Component style={{ color: 'red' }} />;
}

// ✅ Define outside component or use useMemo
const style = { color: 'red' };
function App() {
  return <Component style={style} />;
}
```

#### **Pitfall 3: Forgetting to Pass Required Props**
```jsx
// ❌ Missing required prop
<UserProfile /> // Error if name is required

// ✅ Use defaultProps or optional chaining
function UserProfile({ name = "Guest" }) {
  return <div>Hello, {name}</div>;
}
```

### **Props with TypeScript (Bonus)**

If using TypeScript, you can define prop types with interfaces:

```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  disabled?: boolean;
}

function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  onClick, 
  disabled = false 
}: ButtonProps) {
  // Component implementation
}
```

### **Summary**

**Key Takeaways:**
1. **Props** = Data passed from parent to child components
2. **Props are read-only** - children cannot modify them
3. **Use destructuring** for cleaner code
4. **Provide default values** for optional props
5. **Validate props** with PropTypes or TypeScript
6. **Children prop** is special for content between tags
7. **Props make components reusable** and dynamic

**Remember:** Props are one-way data flow (parent → child). For data that needs to change, you'll need state (which we'll cover next).

---

**Ready for Topic 21: "React Props Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/React Components|React Components]]
- [[Web Development/React/React Topics/JavaScript ES6 Object & Array Destructuring|JavaScript ES6 Object & Array Destructuring]]
- [[Web Development/React/React Topics/State in React - Declarative vs. Imperative Programming|State in React (Declarative vs Imperative)]]
