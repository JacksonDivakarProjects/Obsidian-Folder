## **23. Mapping Data to Components - Complete Beginner's Guide**

### **Introduction**
Welcome to one of React's most powerful patterns! **Mapping data to components** is how you display dynamic lists of data in React. This is where React truly shines - taking arrays of data and transforming them into beautiful, interactive UI elements.

### **Why Map Data to Components?**

Imagine you have 100 products to display. Would you write 100 `<ProductCard>` components manually? Of course not! That's where `map()` comes in.

#### **Before Mapping:**
```jsx
// ❌ Terrible, repetitive code
function ProductList() {
  return (
    <div>
      <ProductCard product={products[0]} />
      <ProductCard product={products[1]} />
      <ProductCard product={products[2]} />
      <ProductCard product={products[3]} />
      {/* ... and 96 more lines! */}
    </div>
  );
}
```

#### **After Mapping:**
```jsx
// ✅ Clean, dynamic code
function ProductList() {
  return (
    <div>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### **The JavaScript `map()` Method**

Before React, let's understand the JavaScript `map()` method:

```javascript
// Basic array map example
const numbers = [1, 2, 3, 4, 5];

// Double each number
const doubled = numbers.map(num => num * 2);
// Result: [2, 4, 6, 8, 10]

// Convert numbers to strings
const strings = numbers.map(num => `Number: ${num}`);
// Result: ["Number: 1", "Number: 2", ...]
```

### **Basic Pattern: Array.map() in JSX**

The fundamental pattern is simple:
```jsx
{array.map(item => (
  <Component key={item.id} data={item} />
))}
```

#### **Example 1: Simple List**
```jsx
function SimpleList() {
  const fruits = ['Apple', 'Banana', 'Orange', 'Grapes'];
  
  return (
    <ul>
      {fruits.map((fruit, index) => (
        <li key={index}>{fruit}</li>
      ))}
    </ul>
  );
}
```

#### **Example 2: List with Objects**
```jsx
function UserList() {
  const users = [
    { id: 1, name: 'Alice', age: 25 },
    { id: 2, name: 'Bob', age: 30 },
    { id: 3, name: 'Charlie', age: 35 }
  ];
  
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>
          <h3>{user.name}</h3>
          <p>Age: {user.age}</p>
        </div>
      ))}
    </div>
  );
}
```

### **The `key` Prop: React's Secret Sauce**

#### **Why Keys are CRITICAL:**
When React renders a list, it needs a way to identify each item uniquely. The `key` prop helps React:
1. **Identify which items changed**
2. **Re-render efficiently**
3. **Maintain component state**

#### **Good Keys:**
```jsx
// ✅ Unique IDs from data
{users.map(user => (
  <UserCard key={user.id} user={user} />
))}

// ✅ Index as last resort
{items.map((item, index) => (
  <Item key={index} item={item} />
))}
```

#### **Bad Keys:**
```jsx
// ❌ Random values (changes every render)
{users.map(user => (
  <UserCard key={Math.random()} user={user} />
))}

// ❌ Non-unique values
{users.map(user => (
  <UserCard key={user.name} user={user} /> // Names might repeat!
))}
```

### **Complete Examples**

#### **Example 1: E-commerce Product Grid**
```jsx
function ProductGrid() {
  const products = [
    { 
      id: 1, 
      name: 'Wireless Headphones', 
      price: 199.99, 
      image: 'headphones.jpg',
      rating: 4.5 
    },
    { 
      id: 2, 
      name: 'Smart Watch', 
      price: 299.99, 
      image: 'watch.jpg',
      rating: 4.2 
    },
    { 
      id: 3, 
      name: 'Laptop Stand', 
      price: 49.99, 
      image: 'stand.jpg',
      rating: 4.8 
    },
    // ... more products
  ];
  
  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCard 
          key={product.id}
          name={product.name}
          price={product.price}
          image={product.image}
          rating={product.rating}
        />
      ))}
    </div>
  );
}

function ProductCard({ name, price, image, rating }) {
  return (
    <div className="product-card">
      <img src={image} alt={name} />
      <h3>{name}</h3>
      <div className="rating">
        {'★'.repeat(Math.floor(rating))}
        <span> ({rating})</span>
      </div>
      <p className="price">${price.toFixed(2)}</p>
      <button>Add to Cart</button>
    </div>
  );
}
```

#### **Example 2: Social Media Feed**
```jsx
function SocialFeed() {
  const posts = [
    {
      id: 101,
      username: 'alex_johnson',
      avatar: 'alex.jpg',
      content: 'Just learned React mapping! So powerful!',
      likes: 245,
      comments: 42,
      timestamp: '2 hours ago'
    },
    {
      id: 102,
      username: 'sarah_webdev',
      avatar: 'sarah.jpg',
      content: 'Building my portfolio with React. Any tips?',
      likes: 189,
      comments: 31,
      timestamp: '5 hours ago'
    },
    // ... more posts
  ];
  
  return (
    <div className="feed">
      {posts.map(post => (
        <Post 
          key={post.id}
          username={post.username}
          avatar={post.avatar}
          content={post.content}
          likes={post.likes}
          comments={post.comments}
          timestamp={post.timestamp}
        />
      ))}
    </div>
  );
}

function Post({ username, avatar, content, likes, comments, timestamp }) {
  return (
    <div className="post">
      <div className="post-header">
        <img src={avatar} alt={username} className="avatar" />
        <div>
          <h4>@{username}</h4>
          <span className="timestamp">{timestamp}</span>
        </div>
      </div>
      <p className="content">{content}</p>
      <div className="post-stats">
        <span>👍 {likes} likes</span>
        <span>💬 {comments} comments</span>
      </div>
    </div>
  );
}
```

### **Advanced Mapping Patterns**

#### **Pattern 1: Conditional Rendering in Map**
```jsx
function TaskList() {
  const tasks = [
    { id: 1, text: 'Learn React', completed: true },
    { id: 2, text: 'Build project', completed: false },
    { id: 3, text: 'Deploy app', completed: false }
  ];
  
  return (
    <ul>
      {tasks.map(task => (
        <li 
          key={task.id}
          style={{
            textDecoration: task.completed ? 'line-through' : 'none',
            color: task.completed ? '#999' : '#333'
          }}
        >
          {task.text}
          {task.completed && ' ✓'}
        </li>
      ))}
    </ul>
  );
}
```

#### **Pattern 2: Nested Mapping**
```jsx
function CommentSection() {
  const posts = [
    {
      id: 1,
      title: 'React is awesome!',
      comments: [
        { id: 101, text: 'I agree!', user: 'Alice' },
        { id: 102, text: 'Great post!', user: 'Bob' }
      ]
    },
    {
      id: 2,
      title: 'Learning hooks',
      comments: [
        { id: 103, text: 'Very helpful', user: 'Charlie' }
      ]
    }
  ];
  
  return (
    <div>
      {posts.map(post => (
        <div key={post.id} className="post">
          <h3>{post.title}</h3>
          <div className="comments">
            {post.comments.map(comment => (
              <div key={comment.id} className="comment">
                <strong>{comment.user}:</strong> {comment.text}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

#### **Pattern 3: Map with Filter**
```jsx
function ActiveUsers() {
  const users = [
    { id: 1, name: 'Alice', active: true },
    { id: 2, name: 'Bob', active: false },
    { id: 3, name: 'Charlie', active: true },
    { id: 4, name: 'Diana', active: false }
  ];
  
  // Filter THEN map
  const activeUsers = users
    .filter(user => user.active)
    .map(user => (
      <li key={user.id}>{user.name} (Active)</li>
    ));
  
  return <ul>{activeUsers}</ul>;
}
```

#### **Pattern 4: Map with Reduce (Complex Transformation)**
```jsx
function OrderSummary() {
  const items = [
    { id: 1, name: 'Product A', price: 25.99, quantity: 2 },
    { id: 2, name: 'Product B', price: 19.99, quantity: 1 },
    { id: 3, name: 'Product C', price: 34.99, quantity: 3 }
  ];
  
  // Calculate total using reduce
  const total = items.reduce((sum, item) => 
    sum + (item.price * item.quantity), 0);
  
  return (
    <div>
      <h2>Order Summary</h2>
      {items.map(item => (
        <div key={item.id} className="order-item">
          <span>{item.name} × {item.quantity}</span>
          <span>${(item.price * item.quantity).toFixed(2)}</span>
        </div>
      ))}
      <div className="total">
        <strong>Total: ${total.toFixed(2)}</strong>
      </div>
    </div>
  );
}
```

### **Performance Considerations**

#### **1. Avoid Inline Functions in Map**
```jsx
// ❌ Creates new function on every render
{array.map(item => (
  <Component 
    key={item.id}
    onClick={() => handleClick(item.id)} // New function each time
  />
))}

// ✅ Define handler outside or use useCallback
const handleItemClick = (id) => {
  // handle click
};

{array.map(item => (
  <Component 
    key={item.id}
    onClick={() => handleItemClick(item.id)}
  />
))}
```

#### **2. Virtualize Long Lists**
For very long lists (1000+ items), use virtualization:
```jsx
import { FixedSizeList as List } from 'react-window';

function BigList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );
  
  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
      width={300}
    >
      {Row}
    </List>
  );
}
```

### **Common Mistakes and Solutions**

#### **Mistake 1: Forgetting the Return Statement**
```jsx
// ❌ No return (returns undefined)
{array.map(item => 
  <Component key={item.id} data={item} />
)}

// ✅ Implicit return with parentheses
{array.map(item => (
  <Component key={item.id} data={item} />
))}

// ✅ Explicit return
{array.map(item => {
  return <Component key={item.id} data={item} />;
})}
```

#### **Mistake 2: Using Index as Key When Items Change**
```jsx
// ❌ Bad when items can be reordered/removed
{todos.map((todo, index) => (
  <TodoItem key={index} todo={todo} />
))}

// ✅ Use stable IDs
{todos.map(todo => (
  <TodoItem key={todo.id} todo={todo} />
))}
```

#### **Mistake 3: Mutating Original Array**
```jsx
// ❌ Modifies original array
const doubled = numbers.map(num => {
  num.value = num.value * 2; // Mutation!
  return num;
});

// ✅ Create new objects
const doubled = numbers.map(num => ({
  ...num,
  value: num.value * 2
}));
```

### **Real-World Example: Dashboard with Multiple Mappings**

```jsx
function Dashboard() {
  // Data from API
  const dashboardData = {
    recentOrders: [
      { id: 1, customer: 'Alice', amount: 125.50, status: 'Delivered' },
      { id: 2, customer: 'Bob', amount: 89.99, status: 'Processing' },
      { id: 3, customer: 'Charlie', amount: 234.75, status: 'Shipped' }
    ],
    topProducts: [
      { id: 101, name: 'Wireless Earbuds', sales: 1245, rating: 4.7 },
      { id: 102, name: 'Smart Watch', sales: 987, rating: 4.5 },
      { id: 103, name: 'Phone Case', sales: 2156, rating: 4.3 }
    ],
    notifications: [
      { id: 1001, message: 'New order received', type: 'success', time: '10 min ago' },
      { id: 1002, message: 'Inventory low for Product X', type: 'warning', time: '1 hour ago' }
    ]
  };
  
  return (
    <div className="dashboard">
      {/* Orders Section */}
      <section className="orders-section">
        <h2>Recent Orders</h2>
        <div className="orders-grid">
          {dashboardData.recentOrders.map(order => (
            <OrderCard 
              key={order.id}
              customer={order.customer}
              amount={order.amount}
              status={order.status}
            />
          ))}
        </div>
      </section>
      
      {/* Products Section */}
      <section className="products-section">
        <h2>Top Products</h2>
        <div className="products-list">
          {dashboardData.topProducts.map(product => (
            <ProductItem 
              key={product.id}
              name={product.name}
              sales={product.sales}
              rating={product.rating}
            />
          ))}
        </div>
      </section>
      
      {/* Notifications Section */}
      <section className="notifications-section">
        <h2>Notifications</h2>
        <div className="notifications">
          {dashboardData.notifications.map(notification => (
            <Notification 
              key={notification.id}
              message={notification.message}
              type={notification.type}
              time={notification.time}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

// Reusable Card Components
function OrderCard({ customer, amount, status }) {
  return (
    <div className="order-card">
      <h3>{customer}</h3>
      <p className="amount">${amount.toFixed(2)}</p>
      <span className={`status ${status.toLowerCase()}`}>
        {status}
      </span>
    </div>
  );
}

function ProductItem({ name, sales, rating }) {
  return (
    <div className="product-item">
      <h4>{name}</h4>
      <p>Sales: {sales.toLocaleString()}</p>
      <div className="rating">
        {'★'.repeat(Math.floor(rating))}
        <span>({rating})</span>
      </div>
    </div>
  );
}

function Notification({ message, type, time }) {
  return (
    <div className={`notification ${type}`}>
      <p>{message}</p>
      <span className="time">{time}</span>
    </div>
  );
}
```

### **Best Practices Summary**

1. **Always use a `key` prop** - Use unique IDs when possible
2. **Keep mapping logic simple** - Extract complex transformations
3. **Consider performance** for large lists
4. **Use fragments** for cleaner JSX
5. **Combine with other array methods** (filter, reduce)
6. **Handle empty arrays** gracefully
7. **Memoize callbacks** in mapped components

### **Quick Reference Cheat Sheet**

```jsx
// Basic pattern
{items.map(item => (
  <Component key={item.id} data={item} />
))}

// With index (avoid if possible)
{items.map((item, index) => (
  <Component key={index} data={item} />
))}

// With destructuring
{users.map(({ id, name, email }) => (
  <User key={id} name={name} email={email} />
))}

// With conditional rendering
{tasks.map(task => (
  task.completed && <Task key={task.id} task={task} />
))}

// Chaining with filter
{products
  .filter(p => p.inStock)
  .map(product => (
    <Product key={product.id} product={product} />
  ))
}
```

### **Common Use Cases**

1. **Displaying API data** - Users, products, posts
2. **Rendering navigation menus** - Menu items
3. **Building tables** - Table rows
4. **Creating forms dynamically** - Form fields
5. **Generating select options** - Dropdown options
6. **Building breadcrumbs** - Navigation path
7. **Rendering tabs/accordions** - Tab items

### **Summary**

**Key Takeaways:**
1. **`map()` transforms arrays into React elements**
2. **`key` prop is REQUIRED** for list items
3. **Use unique, stable keys** (not index if possible)
4. **Combine with other array methods** for powerful data transformations
5. **Keep mapping logic readable** and maintainable

**Remember:** Mapping is React's way of saying "for each item in this array, render this component." It's how dynamic data becomes dynamic UI!

---

**Ready for Topic 24: "Mapping Data to Components Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/JavaScript ES6 Map-Filter-Reduce|JavaScript ES6 Map/Filter/Reduce]]
- [[Web Development/React/React Topics/React Components|React Components]]
- [[Web Development/React/React Topics/React Conditional Rendering with the Ternary Operator & AND Operator|React Conditional Rendering]]
