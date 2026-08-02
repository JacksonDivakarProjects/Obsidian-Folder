## **31. React Hooks - useState - Complete Beginner's Guide**

### **Introduction**
Welcome to **useState** - the most important React Hook! This is where React becomes truly interactive. The `useState` hook is what allows functional components to have state, making them as powerful as class components but with much cleaner syntax.

### **What is useState?**

**useState** is a React Hook that lets you add state to functional components.

#### **Before Hooks (Class Components):**
```jsx
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={() => this.setState({ count: this.state.count + 1 })}>
          Increment
        </button>
      </div>
    );
  }
}
```

#### **After Hooks (Functional Components with useState):**
```jsx
function Counter() {
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

**See the difference?** Much cleaner and simpler!

### **Basic useState Syntax**

#### **Import and Basic Usage:**
```jsx
import React, { useState } from 'react';

function Example() {
  // Declare a state variable
  const [state, setState] = useState(initialValue);
  
  // state: current state value
  // setState: function to update state
  // initialValue: starting value for state
}
```

#### **Simple Example:**
```jsx
function SimpleCounter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

### **Multiple State Variables**

You can use `useState` multiple times in a component:

```jsx
function UserForm() {
  // Multiple state variables
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState(0);
  const [isSubscribed, setIsSubscribed] = useState(false);
  
  return (
    <form>
      <input
        value={name}
        onChange={e => setName(e.target.value)}
        placeholder="Name"
      />
      <input
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="number"
        value={age}
        onChange={e => setAge(parseInt(e.target.value))}
        placeholder="Age"
      />
      <label>
        <input
          type="checkbox"
          checked={isSubscribed}
          onChange={e => setIsSubscribed(e.target.checked)}
        />
        Subscribe to newsletter
      </label>
    </form>
  );
}
```

### **State with Different Data Types**

#### **1. String State**
```jsx
function TextInput() {
  const [text, setText] = useState('');
  
  return (
    <div>
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Type something..."
      />
      <p>You typed: {text}</p>
      <p>Character count: {text.length}</p>
    </div>
  );
}
```

#### **2. Number State**
```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);
  const double = () => setCount(count * 2);
  
  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
      <button onClick={double}>×2</button>
    </div>
  );
}
```

#### **3. Boolean State (Toggles)**
```jsx
function Toggle() {
  const [isOn, setIsOn] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsOn(!isOn)}>
        {isOn ? 'ON' : 'OFF'}
      </button>
      <p>The switch is {isOn ? 'ON ✅' : 'OFF ❌'}</p>
      {isOn && <p>Light is shining! 💡</p>}
    </div>
  );
}
```

#### **4. Array State**
```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');
  
  const addTodo = () => {
    if (newTodo.trim() === '') return;
    setTodos([...todos, newTodo]);
    setNewTodo('');
  };
  
  const removeTodo = (index) => {
    setTodos(todos.filter((_, i) => i !== index));
  };
  
  return (
    <div>
      <input
        value={newTodo}
        onChange={e => setNewTodo(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && addTodo()}
      />
      <button onClick={addTodo}>Add Todo</button>
      
      <ul>
        {todos.map((todo, index) => (
          <li key={index}>
            {todo}
            <button onClick={() => removeTodo(index)}>×</button>
          </li>
        ))}
      </ul>
      
      <p>Total todos: {todos.length}</p>
    </div>
  );
}
```

#### **5. Object State**
```jsx
function UserProfile() {
  const [user, setUser] = useState({
    name: 'John Doe',
    age: 25,
    email: 'john@example.com',
    isActive: true
  });
  
  // Update specific property
  const updateName = (newName) => {
    setUser({ ...user, name: newName });
  };
  
  // Update multiple properties
  const updateProfile = (updates) => {
    setUser({ ...user, ...updates });
  };
  
  // Toggle boolean property
  const toggleActive = () => {
    setUser({ ...user, isActive: !user.isActive });
  };
  
  return (
    <div>
      <h2>{user.name}</h2>
      <p>Age: {user.age}</p>
      <p>Email: {user.email}</p>
      <p>Status: {user.isActive ? 'Active ✅' : 'Inactive ❌'}</p>
      
      <button onClick={() => updateName('Jane Smith')}>
        Change Name
      </button>
      
      <button onClick={() => updateProfile({ age: 30, email: 'new@example.com' })}>
        Update Profile
      </button>
      
      <button onClick={toggleActive}>
        Toggle Active Status
      </button>
    </div>
  );
}
```

### **Functional Updates**

When the new state depends on the previous state, use the functional update pattern:

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  // ❌ Problem with multiple updates
  const incrementTwiceWrong = () => {
    setCount(count + 1); // Uses stale count
    setCount(count + 1); // Uses same stale count
    // Result: count increases by 1, not 2
  };
  
  // ✅ Solution: Functional updates
  const incrementTwiceCorrect = () => {
    setCount(prevCount => prevCount + 1); // Gets latest state
    setCount(prevCount => prevCount + 1); // Gets updated state
    // Result: count increases by 2
  };
  
  // Complex functional update
  const complexUpdate = () => {
    setCount(prevCount => {
      // Can do complex calculations here
      const newCount = prevCount * 2 + 1;
      return newCount > 100 ? 100 : newCount; // Cap at 100
    });
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={incrementTwiceCorrect}>
        Increment Twice
      </button>
      <button onClick={complexUpdate}>
        Complex Update
      </button>
    </div>
  );
}
```

### **Lazy Initial State**

If the initial state is expensive to compute, use a function:

```jsx
function ExpensiveInitialState() {
  // ❌ Computed on every render
  const [data, setData] = useState(expensiveCalculation());
  
  // ✅ Only computed once on initial render
  const [data, setData] = useState(() => expensiveCalculation());
  
  // Example
  const [todos, setTodos] = useState(() => {
    const savedTodos = localStorage.getItem('todos');
    return savedTodos ? JSON.parse(savedTodos) : [];
  });
  
  const [user, setUser] = useState(() => {
    // Complex initialization logic
    const defaultUser = { name: 'Guest', role: 'user' };
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : defaultUser;
  });
}
```

### **Common Patterns with useState**

#### **Pattern 1: Controlled Forms**
```jsx
function ContactForm() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    message: ''
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', form);
    // Send form data to server
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={form.name}
        onChange={handleChange}
        placeholder="Your Name"
      />
      <input
        name="email"
        type="email"
        value={form.email}
        onChange={handleChange}
        placeholder="Your Email"
      />
      <textarea
        name="message"
        value={form.message}
        onChange={handleChange}
        placeholder="Your Message"
        rows="4"
      />
      <button type="submit">Send</button>
    </form>
  );
}
```

#### **Pattern 2: Toggle with Multiple States**
```jsx
function Accordion() {
  const [openSections, setOpenSections] = useState({});
  
  const toggleSection = (sectionId) => {
    setOpenSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };
  
  const sections = [
    { id: 'faq1', title: 'What is React?', content: 'React is a JavaScript library...' },
    { id: 'faq2', title: 'What are Hooks?', content: 'Hooks are functions that let you use state...' },
    { id: 'faq3', title: 'How to use useState?', content: 'useState is a hook that adds state...' }
  ];
  
  return (
    <div className="accordion">
      {sections.map(section => (
        <div key={section.id} className="accordion-item">
          <button
            className="accordion-header"
            onClick={() => toggleSection(section.id)}
          >
            {section.title}
            <span>{openSections[section.id] ? '−' : '+'}</span>
          </button>
          {openSections[section.id] && (
            <div className="accordion-content">
              {section.content}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

#### **Pattern 3: Shopping Cart**
```jsx
function ShoppingCart() {
  const [cart, setCart] = useState([
    { id: 1, name: 'Product A', price: 19.99, quantity: 1 },
    { id: 2, name: 'Product B', price: 29.99, quantity: 2 },
    { id: 3, name: 'Product C', price: 9.99, quantity: 3 }
  ]);
  
  const updateQuantity = (productId, newQuantity) => {
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === productId
          ? { ...item, quantity: Math.max(0, newQuantity) }
          : item
      ).filter(item => item.quantity > 0) // Remove if quantity is 0
    );
  };
  
  const addToCart = (product) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevCart, { ...product, quantity: 1 }];
      }
    });
  };
  
  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };
  
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  
  return (
    <div className="shopping-cart">
      <h2>Shopping Cart ({cart.length} items)</h2>
      
      {cart.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <>
          <ul>
            {cart.map(item => (
              <li key={item.id} className="cart-item">
                <span>{item.name}</span>
                <span>${item.price.toFixed(2)}</span>
                <div className="quantity-controls">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>
                    −
                  </button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>
                    +
                  </button>
                </div>
                <span>${(item.price * item.quantity).toFixed(2)}</span>
                <button
                  onClick={() => removeFromCart(item.id)}
                  className="remove-btn"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          
          <div className="cart-summary">
            <h3>Total: ${total.toFixed(2)}</h3>
            <button>Checkout</button>
          </div>
        </>
      )}
    </div>
  );
}
```

### **Rules of Hooks**

#### **Rule 1: Only Call Hooks at the Top Level**
```jsx
// ✅ Correct - at top level
function MyComponent() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  // ...
}

// ❌ Wrong - inside condition
function WrongComponent() {
  if (someCondition) {
    const [count, setCount] = useState(0); // ERROR!
  }
  // ...
}

// ❌ Wrong - inside loop
function WrongComponent() {
  for (let i = 0; i < 10; i++) {
    const [count, setCount] = useState(0); // ERROR!
  }
  // ...
}

// ❌ Wrong - inside nested function
function WrongComponent() {
  function innerFunction() {
    const [count, setCount] = useState(0); // ERROR!
  }
  // ...
}
```

#### **Rule 2: Only Call Hooks from React Functions**
```jsx
// ✅ Correct - in React function component
function MyComponent() {
  const [count, setCount] = useState(0);
  // ...
}

// ✅ Correct - in custom hook
function useCustomHook() {
  const [value, setValue] = useState('');
  return [value, setValue];
}

// ❌ Wrong - in regular JavaScript function
function regularFunction() {
  const [count, setCount] = useState(0); // ERROR!
}
```

### **Common Mistakes and Solutions**

#### **Mistake 1: Direct State Mutation**
```jsx
function UserProfile() {
  const [user, setUser] = useState({ name: 'Alice', age: 25 });
  
  // ❌ WRONG - directly mutating state
  const updateAgeWrong = () => {
    user.age = 26; // Mutation!
    setUser(user); // Won't trigger re-render
  };
  
  // ✅ CORRECT - create new object
  const updateAgeCorrect = () => {
    setUser({ ...user, age: 26 });
  };
  
  // ✅ Also correct - functional update
  const updateAgeCorrect2 = () => {
    setUser(prevUser => ({ ...prevUser, age: 26 }));
  };
}
```

#### **Mistake 2: Async State Updates**
```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  // ❌ Problem: async state updates
  const incrementAsyncWrong = () => {
    setTimeout(() => {
      setCount(count + 1); // Uses stale closure
    }, 1000);
  };
  
  // ✅ Solution: functional update
  const incrementAsyncCorrect = () => {
    setTimeout(() => {
      setCount(prev => prev + 1); // Gets latest state
    }, 1000);
  };
}
```

#### **Mistake 3: Unnecessary State**
```jsx
// ❌ Storing derived state
function UserDisplay() {
  const [user, setUser] = useState({ firstName: 'John', lastName: 'Doe' });
  const [fullName, setFullName] = useState(''); // Unnecessary!
  
  useEffect(() => {
    setFullName(`${user.firstName} ${user.lastName}`);
  }, [user]);
  
  // ...
}

// ✅ Compute derived values
function UserDisplay() {
  const [user, setUser] = useState({ firstName: 'John', lastName: 'Doe' });
  const fullName = `${user.firstName} ${user.lastName}`; // Derived!
  
  // ...
}
```

### **Advanced useState Patterns**

#### **Pattern 1: State with useReducer Pattern**
```jsx
function useReducerState(reducer, initialState) {
  const [state, setState] = useState(initialState);
  
  const dispatch = (action) => {
    setState(prev => reducer(prev, action));
  };
  
  return [state, dispatch];
}

// Usage
const todoReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_TODO':
      return [...state, action.payload];
    case 'REMOVE_TODO':
      return state.filter(todo => todo.id !== action.payload);
    case 'TOGGLE_TODO':
      return state.map(todo =>
        todo.id === action.payload
          ? { ...todo, completed: !todo.completed }
          : todo
      );
    default:
      return state;
  }
};

function TodoApp() {
  const [todos, dispatch] = useReducerState(todoReducer, []);
  
  const addTodo = (text) => {
    dispatch({
      type: 'ADD_TODO',
      payload: { id: Date.now(), text, completed: false }
    });
  };
  
  // ...
}
```

#### **Pattern 2: State with Local Storage**
```jsx
function useLocalStorage(key, initialValue) {
  // Get from localStorage or use initial value
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });
  
  // Update both state and localStorage
  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };
  
  return [storedValue, setValue];
}

// Usage
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };
  
  return (
    <div className={`app ${theme}`}>
      <button onClick={toggleTheme}>
        Switch to {theme === 'light' ? 'Dark' : 'Light'} Mode
      </button>
    </div>
  );
}
```

#### **Pattern 3: Debounced State**
```jsx
function useDebouncedState(initialValue, delay) {
  const [value, setValue] = useState(initialValue);
  const [debouncedValue, setDebouncedValue] = useState(initialValue);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, delay]);
  
  return [value, setValue, debouncedValue];
}

// Usage - for search input
function SearchBox() {
  const [query, setQuery, debouncedQuery] = useDebouncedState('', 500);
  
  // API call with debounced query
  useEffect(() => {
    if (debouncedQuery) {
      fetchResults(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return (
    <input
      value={query}
      onChange={e => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### **Performance Considerations**

#### **1. State Updates Cause Re-renders**
```jsx
function ExpensiveComponent() {
  const [count, setCount] = useState(0);
  
  // This expensive calculation runs on every render
  const expensiveValue = expensiveCalculation();
  
  return (
    <div>
      <p>Count: {count}</p>
      <p>Expensive: {expensiveValue}</p>
      <button onClick={() => setCount(count + 1)}>
        Re-render
      </button>
    </div>
  );
}
```

#### **2. Multiple State Updates Batch Together**
```jsx
function BatchUpdateExample() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');
  
  // React batches these updates in React 18+
  const handleClick = () => {
    setCount(count + 1);
    setText('Updated');
    // Only one re-render happens
  };
  
  console.log('Rendering with:', count, text);
  
  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
}
```

### **Real-World Complete Example**

```jsx
function TaskManager() {
  // State declarations
  const [tasks, setTasks] = useState(() => {
    const saved = localStorage.getItem('tasks');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [newTask, setNewTask] = useState('');
  const [filter, setFilter] = useState('all');
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  
  // Derived state
  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });
  
  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => t.completed).length,
    pending: tasks.filter(t => !t.completed).length
  };
  
  // State update functions
  const addTask = () => {
    if (newTask.trim() === '') return;
    
    const task = {
      id: Date.now(),
      text: newTask,
      completed: false,
      createdAt: new Date().toISOString()
    };
    
    setTasks(prev => {
      const newTasks = [...prev, task];
      localStorage.setItem('tasks', JSON.stringify(newTasks));
      return newTasks;
    });
    
    setNewTask('');
  };
  
  const toggleTask = (id) => {
    setTasks(prev => {
      const newTasks = prev.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      );
      localStorage.setItem('tasks', JSON.stringify(newTasks));
      return newTasks;
    });
  };
  
  const deleteTask = (id) => {
    setTasks(prev => {
      const newTasks = prev.filter(task => task.id !== id);
      localStorage.setItem('tasks', JSON.stringify(newTasks));
      return newTasks;
    });
  };
  
  const startEdit = (task) => {
    setEditingId(task.id);
    setEditText(task.text);
  };
  
  const saveEdit = () => {
    if (editText.trim() === '') {
      deleteTask(editingId);
    } else {
      setTasks(prev => {
        const newTasks = prev.map(task =>
          task.id === editingId ? { ...task, text: editText } : task
        );
        localStorage.setItem('tasks', JSON.stringify(newTasks));
        return newTasks;
      });
    }
    setEditingId(null);
    setEditText('');
  };
  
  const clearCompleted = () => {
    setTasks(prev => {
      const newTasks = prev.filter(task => !task.completed);
      localStorage.setItem('tasks', JSON.stringify(newTasks));
      return newTasks;
    });
  };
  
  return (
    <div className="task-manager">
      <h1>Task Manager</h1>
      
      {/* Add Task */}
      <div className="add-task">
        <input
          value={newTask}
          onChange={e => setNewTask(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && addTask()}
          placeholder="Add a new task..."
        />
        <button onClick={addTask} disabled={!newTask.trim()}>
          Add
        </button>
      </div>
      
      {/* Stats */}
      <div className="stats">
        <span>Total: {stats.total}</span>
        <span>Pending: {stats.pending}</span>
        <span>Completed: {stats.completed}</span>
      </div>
      
      {/* Filters */}
      <div className="filters">
        {['all', 'active', 'completed'].map(f => (
          <button
            key={f}
            className={filter === f ? 'active' : ''}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        {stats.completed > 0 && (
          <button onClick={clearCompleted} className="clear-btn">
            Clear Completed
          </button>
        )}
      </div>
      
      {/* Task List */}
      <ul className="task-list">
        {filteredTasks.map(task => (
          <li
            key={task.id}
            className={`task-item ${task.completed ? 'completed' : ''} ${
              editingId === task.id ? 'editing' : ''
            }`}
          >
            {editingId === task.id ? (
              // Edit mode
              <div className="edit-mode">
                <input
                  value={editText}
                  onChange={e => setEditText(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && saveEdit()}
                  autoFocus
                />
                <button onClick={saveEdit}>Save</button>
                <button onClick={() => setEditingId(null)}>Cancel</button>
              </div>
            ) : (
              // View mode
              <>
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggleTask(task.id)}
                />
                <span
                  className="task-text"
                  onDoubleClick={() => startEdit(task)}
                >
                  {task.text}
                </span>
                <div className="task-actions">
                  <button onClick={() => startEdit(task)}>Edit</button>
                  <button onClick={() => deleteTask(task.id)}>Delete</button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
      
      {/* Empty state */}
      {filteredTasks.length === 0 && (
        <div className="empty-state">
          <p>
            {filter === 'all' && tasks.length === 0
              ? 'No tasks yet. Add one above!'
              : filter === 'active'
              ? 'No active tasks'
              : 'No completed tasks'}
          </p>
        </div>
      )}
    </div>
  );
}
```

### **Summary**

**Key Takeaways:**
1. **`useState` adds state** to functional components
2. **Returns array** `[state, setState]` - destructure it
3. **State updates trigger re-renders**
4. **Use functional updates** when new state depends on old state
5. **Never mutate state directly** - always create new values
6. **Follow Rules of Hooks** - top level, in React functions only

**Common Patterns:**
- **Strings** for text inputs
- **Numbers** for counters
- **Booleans** for toggles
- **Arrays** for lists
- **Objects** for forms/complex data
- **Functional updates** for dependent state

**Remember:** `useState` is your gateway to interactive React components. Master it, and you've mastered the foundation of React state management!

---

**Ready for Topic 32: "useState Hook Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/State in React - Declarative vs. Imperative Programming|State in React (Declarative vs Imperative)]]
- [[Web Development/React/React Topics/React Components|React Components]]
- [[Web Development/React/React Topics/JavaScript ES6 Spread Operator|JavaScript ES6 Spread Operator]]
- [[Web Development/React/React Topics/Async-Await|Async/Await]]
