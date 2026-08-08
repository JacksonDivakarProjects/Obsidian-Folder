## **25. JavaScript ES6 Map/Filter/Reduce - Complete Beginner's Guide**

### **Introduction**
Welcome to JavaScript's superpowers! **map(), filter(), and reduce()** are three of the most important array methods in modern JavaScript. They're essential for React development because they help you transform data before rendering it. Let's master these powerful tools!

### **Why These Methods Matter in React**

In React, you often need to:
1. **Transform** data before displaying it (map)
2. **Filter** data based on conditions (filter) 
3. **Calculate** values from data (reduce)

These methods are **declarative** - you say **what** you want, not **how** to do it.

### **The Old Way vs The New Way**

#### **Old Way: Imperative (How)**
```javascript
// Using for loops - telling HOW to do everything
const numbers = [1, 2, 3, 4, 5];
const doubled = [];

for (let i = 0; i < numbers.length; i++) {
  doubled.push(numbers[i] * 2);
}
// doubled = [2, 4, 6, 8, 10]
```

#### **New Way: Declarative (What)**
```javascript
// Using map - telling WHAT you want
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
// doubled = [2, 4, 6, 8, 10]
```

### **1. The `map()` Method**

**Purpose:** Transform each item in an array

**Analogy:** Like a factory assembly line - each item goes through the same process

#### **Basic Syntax:**
```javascript
array.map(callbackFunction)
// callbackFunction receives: (currentItem, index, originalArray)
```

#### **Examples:**

**Example 1: Simple Transformation**
```javascript
const numbers = [1, 2, 3, 4, 5];

// Double each number
const doubled = numbers.map(num => num * 2);
// [2, 4, 6, 8, 10]

// Convert to strings
const strings = numbers.map(num => `Number: ${num}`);
// ["Number: 1", "Number: 2", ...]
```

**Example 2: Transforming Objects**
```javascript
const users = [
  { id: 1, name: 'Alice', age: 25 },
  { id: 2, name: 'Bob', age: 30 },
  { id: 3, name: 'Charlie', age: 35 }
];

// Extract just names
const names = users.map(user => user.name);
// ["Alice", "Bob", "Charlie"]

// Create new objects with modified properties
const usersWithStatus = users.map(user => ({
  ...user,
  isAdult: user.age >= 18,
  greeting: `Hello, ${user.name}!`
}));
// Result: [{id: 1, name: 'Alice', age: 25, isAdult: true, greeting: 'Hello, Alice!'}, ...]
```

**Example 3: Practical React Usage**
```javascript
// Before mapping - raw data
const products = [
  { id: 1, name: 'Laptop', price: 999.99, inStock: true },
  { id: 2, name: 'Mouse', price: 25.99, inStock: false },
  { id: 3, name: 'Keyboard', price: 75.50, inStock: true }
];

// Transform for display
const productDisplay = products.map(product => ({
  id: product.id,
  title: product.name.toUpperCase(),
  price: `$${product.price.toFixed(2)}`,
  availability: product.inStock ? 'In Stock' : 'Out of Stock',
  badge: product.inStock ? '🟢' : '🔴'
}));

// Result:
// [
//   {id: 1, title: 'LAPTOP', price: '$999.99', availability: 'In Stock', badge: '🟢'},
//   {id: 2, title: 'MOUSE', price: '$25.99', availability: 'Out of Stock', badge: '🔴'},
//   ...
// ]
```

### **2. The `filter()` Method**

**Purpose:** Create a new array with only items that pass a test

**Analogy:** Like a sieve - only lets through what matches criteria

#### **Basic Syntax:**
```javascript
array.filter(callbackFunction)
// callbackFunction should return true (keep) or false (remove)
```

#### **Examples:**

**Example 1: Simple Filtering**
```javascript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Get even numbers
const evens = numbers.filter(n => n % 2 === 0);
// [2, 4, 6, 8, 10]

// Get numbers greater than 5
const largeNumbers = numbers.filter(n => n > 5);
// [6, 7, 8, 9, 10]
```

**Example 2: Filtering Objects**
```javascript
const users = [
  { id: 1, name: 'Alice', age: 25, active: true },
  { id: 2, name: 'Bob', age: 30, active: false },
  { id: 3, name: 'Charlie', age: 17, active: true },
  { id: 4, name: 'Diana', age: 35, active: true }
];

// Get active users
const activeUsers = users.filter(user => user.active);
// [{id: 1, name: 'Alice', ...}, {id: 3, name: 'Charlie', ...}, {id: 4, name: 'Diana', ...}]

// Get users over 18
const adults = users.filter(user => user.age >= 18);
// [{id: 1, name: 'Alice', ...}, {id: 2, name: 'Bob', ...}, {id: 4, name: 'Diana', ...}]

// Get active users over 18
const activeAdults = users.filter(user => user.active && user.age >= 18);
// [{id: 1, name: 'Alice', ...}, {id: 4, name: 'Diana', ...}]
```

**Example 3: Search/Filter Functionality**
```javascript
const products = [
  { id: 1, name: 'iPhone', category: 'electronics', price: 999 },
  { id: 2, name: 'T-shirt', category: 'clothing', price: 25 },
  { id: 3, name: 'Laptop', category: 'electronics', price: 1200 },
  { id: 4, name: 'Jeans', category: 'clothing', price: 60 }
];

// Filter by category
const electronics = products.filter(p => p.category === 'electronics');
// [{id: 1, name: 'iPhone', ...}, {id: 3, name: 'Laptop', ...}]

// Filter by price range
const affordable = products.filter(p => p.price < 100);
// [{id: 2, name: 'T-shirt', ...}, {id: 4, name: 'Jeans', ...}]

// Search by name (case-insensitive)
const searchTerm = 'lap';
const searchResults = products.filter(p => 
  p.name.toLowerCase().includes(searchTerm.toLowerCase())
);
// [{id: 3, name: 'Laptop', ...}]
```

### **3. The `reduce()` Method**

**Purpose:** Reduce an array to a single value

**Analogy:** Like a cooking recipe that combines ingredients into one dish

#### **Basic Syntax:**
```javascript
array.reduce(callbackFunction, initialValue)
// callbackFunction receives: (accumulator, currentItem, index, array)
```

#### **Examples:**

**Example 1: Simple Summation**
```javascript
const numbers = [1, 2, 3, 4, 5];

// Sum all numbers
const sum = numbers.reduce((total, num) => total + num, 0);
// 15

// Product of all numbers
const product = numbers.reduce((total, num) => total * num, 1);
// 120
```

**Example 2: Complex Reductions**
```javascript
const orders = [
  { id: 1, amount: 100, currency: 'USD' },
  { id: 2, amount: 150, currency: 'USD' },
  { id: 3, amount: 200, currency: 'EUR' }
];

// Total amount in USD
const totalUSD = orders
  .filter(order => order.currency === 'USD')
  .reduce((sum, order) => sum + order.amount, 0);
// 250

// Group by currency
const groupedByCurrency = orders.reduce((groups, order) => {
  const currency = order.currency;
  if (!groups[currency]) {
    groups[currency] = [];
  }
  groups[currency].push(order);
  return groups;
}, {});

// Result: { USD: [{id:1,...}, {id:2,...}], EUR: [{id:3,...}] }
```

**Example 3: Finding Maximum/Minimum**
```javascript
const scores = [85, 92, 78, 95, 88];

// Highest score
const highest = scores.reduce((max, score) => 
  score > max ? score : max, scores[0]
);
// 95

// Average score
const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
// 87.6
```

### **Combining All Three Methods**

This is where the real power comes in! You can chain these methods together.

#### **Example: E-commerce Cart Analysis**
```javascript
const cartItems = [
  { id: 1, name: 'Laptop', price: 999.99, quantity: 1, category: 'electronics' },
  { id: 2, name: 'Mouse', price: 25.99, quantity: 2, category: 'electronics' },
  { id: 3, name: 'T-shirt', price: 19.99, quantity: 3, category: 'clothing' },
  { id: 4, name: 'Book', price: 15.99, quantity: 1, category: 'books' }
];

// Get total cart value
const totalValue = cartItems
  .map(item => item.price * item.quantity)  // [999.99, 51.98, 59.97, 15.99]
  .reduce((sum, itemTotal) => sum + itemTotal, 0); // 1127.93

// Get only electronics, apply 10% discount, then calculate total
const electronicsTotal = cartItems
  .filter(item => item.category === 'electronics')  // Filter electronics
  .map(item => ({
    ...item,
    discountedPrice: item.price * 0.9  // Apply 10% discount
  }))
  .reduce((sum, item) => 
    sum + (item.discountedPrice * item.quantity), 0
  ); // Calculate total

// Get summary by category
const categorySummary = cartItems.reduce((summary, item) => {
  const category = item.category;
  if (!summary[category]) {
    summary[category] = {
      totalItems: 0,
      totalValue: 0
    };
  }
  summary[category].totalItems += item.quantity;
  summary[category].totalValue += item.price * item.quantity;
  return summary;
}, {});

// Result:
// {
//   electronics: { totalItems: 3, totalValue: 1051.97 },
//   clothing: { totalItems: 3, totalValue: 59.97 },
//   books: { totalItems: 1, totalValue: 15.99 }
// }
```

### **Practical React Examples**

#### **Example 1: Data Processing for Display**
```javascript
// Raw API data
const rawUsers = [
  { userId: 1, firstName: 'john', lastName: 'doe', age: 25, email: 'john@test.com', status: 'active' },
  { userId: 2, firstName: 'jane', lastName: 'smith', age: 17, email: 'jane@test.com', status: 'inactive' },
  { userId: 3, firstName: 'bob', lastName: 'johnson', age: 30, email: 'bob@test.com', status: 'active' }
];

// Process for UI display
const processedUsers = rawUsers
  .filter(user => user.status === 'active' && user.age >= 18) // Only active adults
  .map(user => ({
    id: user.userId,
    fullName: `${user.firstName} ${user.lastName}`.toUpperCase(),
    email: user.email,
    age: user.age,
    displayText: `${user.firstName} (${user.age}) - ${user.email}`,
    isEligible: user.age >= 21
  }))
  .sort((a, b) => a.age - b.age); // Sort by age

// Result ready for React rendering
```

#### **Example 2: Dashboard Statistics**
```javascript
const transactions = [
  { id: 1, type: 'income', amount: 1000, category: 'salary', date: '2024-01-01' },
  { id: 2, type: 'expense', amount: 150, category: 'food', date: '2024-01-02' },
  { id: 3, type: 'expense', amount: 300, category: 'rent', date: '2024-01-03' },
  { id: 4, type: 'income', amount: 500, category: 'freelance', date: '2024-01-04' }
];

// Calculate dashboard stats
const dashboardStats = {
  // Total income
  totalIncome: transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0),
  
  // Total expenses
  totalExpenses: transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0),
  
  // Balance
  balance: transactions.reduce((sum, t) => 
    t.type === 'income' ? sum + t.amount : sum - t.amount, 0),
  
  // Expenses by category
  expensesByCategory: transactions
    .filter(t => t.type === 'expense')
    .reduce((categories, t) => {
      if (!categories[t.category]) {
        categories[t.category] = 0;
      }
      categories[t.category] += t.amount;
      return categories;
    }, {})
};

// Result:
// {
//   totalIncome: 1500,
//   totalExpenses: 450,
//   balance: 1050,
//   expensesByCategory: { food: 150, rent: 300 }
// }
```

### **Performance Considerations**

#### **1. Method Chaining vs Single Reduce**
```javascript
// ❌ Less efficient - creates intermediate arrays
const result = array
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((sum, val) => sum + val, 0);

// ✅ More efficient - single pass
const result = array.reduce((sum, x) => {
  if (x.active) {
    return sum + x.value;
  }
  return sum;
}, 0);
```

#### **2. Large Arrays**
For very large arrays (10,000+ items), consider:
- Using for loops for better performance
- Web Workers for parallel processing
- Pagination or virtual scrolling

### **Common Mistakes and Solutions**

#### **Mistake 1: Forgetting to Return in Callback**
```javascript
// ❌ No return statement
const doubled = numbers.map(num => {
  num * 2; // Oops, no return!
});

// ✅ Always return
const doubled = numbers.map(num => {
  return num * 2;
});

// ✅ Or use implicit return
const doubled = numbers.map(num => num * 2);
```

#### **Mistake 2: Mutating Original Array**
```javascript
// ❌ Modifies original array
const users = [{ name: 'Alice', age: 25 }];
const updated = users.map(user => {
  user.age += 1; // Mutation!
  return user;
});

// ✅ Create new objects
const updated = users.map(user => ({
  ...user,
  age: user.age + 1
}));
```

#### **Mistake 3: Incorrect Initial Value in Reduce**
```javascript
// ❌ Wrong initial value for strings
const words = ['hello', 'world'];
const sentence = words.reduce((acc, word) => 
  acc + word, 0 // 0 is number, but we want string!
);

// ✅ Correct initial value
const sentence = words.reduce((acc, word) => 
  acc + ' ' + word, ''
);
```

### **Comparison Table**

| Method | Returns | Purpose | Common Use Cases |
|--------|---------|---------|-----------------|
| **map()** | New array (same length) | Transform each item | Formatting data, extracting properties |
| **filter()** | New array (same or shorter) | Select items that match criteria | Search, filtering, validation |
| **reduce()** | Single value (any type) | Combine items into one result | Summation, grouping, finding max/min |

### **Quick Reference Cheat Sheet**

```javascript
// MAP - Transform
arr.map(item => transformedItem)
arr.map((item, index) => transformedItem)

// FILTER - Select
arr.filter(item => condition)
arr.filter((item, index) => condition)

// REDUCE - Combine
arr.reduce((accumulator, item) => newAccumulator, initialValue)
arr.reduce((acc, item, index) => newAccumulator, initialValue)

// Chaining
arr
  .filter(item => condition)
  .map(item => transformedItem)
  .reduce((acc, item) => combined, initialValue)
```

### **Advanced Patterns**

#### **1. FlatMap (ES2019)**
```javascript
// Combine map and flatten
const arrays = [[1, 2], [3, 4], [5, 6]];
const flattened = arrays.flatMap(arr => arr.map(n => n * 2));
// [2, 4, 6, 8, 10, 12]
```

#### **2. Reduce to Create Lookup Objects**
```javascript
const products = [
  { id: 1, name: 'Laptop', category: 'electronics' },
  { id: 2, name: 'Shirt', category: 'clothing' }
];

// Create lookup object by ID
const productById = products.reduce((lookup, product) => {
  lookup[product.id] = product;
  return lookup;
}, {});

// Usage: productById[1] returns the laptop object
```

#### **3. Pipeline Pattern**
```javascript
// Create reusable transformation functions
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

const transformations = [
  data => data.filter(item => item.active),
  data => data.map(item => ({ ...item, processed: true })),
  data => data.sort((a, b) => a.id - b.id)
];

const processData = pipe(...transformations);
const result = processData(rawData);
```

### **Real-World React Example**

```javascript
// Component that uses all three methods
function UserDashboard({ users, filters }) {
  // Process data for display
  const processedData = users
    // Filter based on props
    .filter(user => {
      if (filters.activeOnly && !user.isActive) return false;
      if (filters.minAge && user.age < filters.minAge) return false;
      return true;
    })
    // Transform for display
    .map(user => ({
      ...user,
      displayName: `${user.firstName} ${user.lastName}`,
      initials: `${user.firstName[0]}${user.lastName[0]}`,
      ageGroup: user.age < 30 ? 'Young' : user.age < 50 ? 'Middle' : 'Senior'
    }))
    // Sort
    .sort((a, b) => a.lastName.localeCompare(b.lastName));
  
  // Calculate statistics
  const stats = users.reduce((acc, user) => {
    acc.totalUsers++;
    if (user.isActive) acc.activeUsers++;
    if (user.age >= 18) acc.adults++;
    return acc;
  }, { totalUsers: 0, activeUsers: 0, adults: 0 });
  
  // Group by department
  const byDepartment = users.reduce((groups, user) => {
    const dept = user.department || 'Unassigned';
    if (!groups[dept]) groups[dept] = [];
    groups[dept].push(user);
    return groups;
  }, {});
  
  return (
    <div className="dashboard">
      <StatsDisplay stats={stats} />
      <UserList users={processedData} />
      <DepartmentSummary groups={byDepartment} />
    </div>
  );
}
```

### **Summary**

**Key Takeaways:**
1. **`map()`** - Transform each item (1:1 mapping)
2. **`filter()`** - Select items that match criteria
3. **`reduce()`** - Combine items into a single result
4. **Chain them** for complex data transformations
5. **They don't mutate** the original array
6. **Essential for React** data processing

**Remember:** These methods are **declarative** - you describe **what** you want, not **how** to do it. This leads to cleaner, more maintainable code.

---

**Ready for Topic 26: "Javascript ES6 Arrow functions"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Mapping Data to Components|Mapping Data to Components]]
- [[Web Development/React/React Topics/JavaScript ES6 Arrow Functions|JavaScript ES6 Arrow Functions]]
- [[Web Development/React/React Topics/JavaScript ES6 Spread Operator|JavaScript ES6 Spread Operator]]
