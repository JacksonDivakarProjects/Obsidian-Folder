## **35. Event Handling in React - Complete Beginner's Guide**

### **Introduction**
Welcome to **event handling** in React! This is what makes your components interactive. When users click buttons, type in forms, hover over elements, or perform any action - events are how React responds. Let's learn how to handle events the React way!

### **How Events Work in React**

#### **HTML vs React Events:**
```html
<!-- HTML Event Handling -->
<button onclick="handleClick()">Click me</button>

<!-- React Event Handling -->
<button onClick={handleClick}>Click me</button>
```

**Key Differences:**
1. **camelCase** vs lowercase (`onClick` not `onclick`)
2. **Function reference** vs string (`{handleClick}` not `"handleClick()"`)
3. **Prevent default** differently
4. **Event pooling** in React

### **Basic Event Handling Syntax**

#### **Simple Click Event:**
```jsx
function Button() {
  const handleClick = () => {
    alert('Button clicked!');
  };
  
  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
}
```

#### **Inline Event Handler:**
```jsx
function InlineExample() {
  return (
    <button onClick={() => alert('Clicked!')}>
      Click me
    </button>
  );
}
```

### **Common React Events**

#### **Mouse Events:**
```jsx
function MouseEvents() {
  return (
    <div>
      {/* Click events */}
      <button onClick={() => console.log('Clicked')}>
        Click
      </button>
      
      {/* Double click */}
      <button onDoubleClick={() => console.log('Double clicked')}>
        Double Click
      </button>
      
      {/* Mouse enter/leave */}
      <div
        onMouseEnter={() => console.log('Mouse entered')}
        onMouseLeave={() => console.log('Mouse left')}
        style={{ padding: '20px', background: 'lightblue' }}
      >
        Hover over me
      </div>
      
      {/* Mouse move */}
      <div
        onMouseMove={(e) => console.log(`Mouse at: ${e.clientX}, ${e.clientY}`)}
        style={{ padding: '20px', background: 'lightgreen' }}
      >
        Move mouse here
      </div>
    </div>
  );
}
```

#### **Form Events:**
```jsx
function FormEvents() {
  const [inputValue, setInputValue] = useState('');
  
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      console.log('Form submitted:', inputValue);
    }}>
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onFocus={() => console.log('Input focused')}
        onBlur={() => console.log('Input lost focus')}
        placeholder="Type something..."
      />
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

#### **Keyboard Events:**
```jsx
function KeyboardEvents() {
  const handleKeyDown = (e) => {
    console.log(`Key pressed: ${e.key}`);
    
    // Check for specific keys
    if (e.key === 'Enter') {
      console.log('Enter pressed!');
    }
    
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault(); // Prevent browser save
      console.log('Ctrl+S pressed');
    }
  };
  
  return (
    <div>
      <input
        onKeyDown={handleKeyDown}
        onKeyUp={() => console.log('Key released')}
        onKeyPress={(e) => console.log(`Character: ${e.key}`)}
        placeholder="Press keys here..."
      />
      
      {/* Global keyboard events */}
      <div
        tabIndex={0} // Make div focusable for keyboard events
        onKeyDown={handleKeyDown}
        style={{ padding: '20px', background: '#f0f0f0' }}
      >
        Click here then press keys
      </div>
    </div>
  );
}
```

#### **Focus & Clipboard Events:**
```jsx
function FocusClipboardEvents() {
  return (
    <div>
      <input
        onFocus={() => console.log('Element focused')}
        onBlur={() => console.log('Element blurred')}
        placeholder="Focus me"
      />
      
      <textarea
        onCopy={() => console.log('Text copied')}
        onCut={() => console.log('Text cut')}
        onPaste={() => console.log('Text pasted')}
        defaultValue="Try copying this text"
      />
    </div>
  );
}
```

### **The Event Object**

React passes a **synthetic event object** to event handlers. It's similar to native browser events but works consistently across browsers.

#### **Accessing Event Properties:**
```jsx
function EventObjectExample() {
  const handleClick = (event) => {
    // Common event properties
    console.log('Event type:', event.type); // "click"
    console.log('Target element:', event.target); // The button element
    console.log('Current target:', event.currentTarget); // Element handler is attached to
    console.log('Timestamp:', event.timeStamp);
    
    // Mouse event properties
    console.log('Client X:', event.clientX);
    console.log('Client Y:', event.clientY);
    console.log('Page X:', event.pageX);
    console.log('Page Y:', event.pageY);
    
    // Keyboard event properties
    console.log('Key:', event.key);
    console.log('Code:', event.code);
    console.log('Ctrl key:', event.ctrlKey);
    console.log('Shift key:', event.shiftKey);
    
    // Prevent default behavior
    event.preventDefault();
    
    // Stop event bubbling
    event.stopPropagation();
  };
  
  return (
    <button onClick={handleClick}>
      Click for event details
    </button>
  );
}
```

### **Event Handler Patterns**

#### **Pattern 1: Passing Arguments to Event Handlers**
```jsx
function ItemList() {
  const items = ['Apple', 'Banana', 'Orange'];
  
  // Method 1: Inline arrow function
  const handleClick1 = (itemName) => {
    console.log(`Clicked: ${itemName}`);
  };
  
  // Method 2: Function that returns handler
  const handleClick2 = (itemName) => () => {
    console.log(`Clicked: ${itemName}`);
  };
  
  // Method 3: Using data attributes
  const handleClick3 = (e) => {
    const itemName = e.target.dataset.item;
    console.log(`Clicked: ${itemName}`);
  };
  
  return (
    <ul>
      {/* Method 1 */}
      {items.map(item => (
        <li key={item}>
          <button onClick={() => handleClick1(item)}>
            {item} (Method 1)
          </button>
        </li>
      ))}
      
      {/* Method 2 */}
      {items.map(item => (
        <li key={item}>
          <button onClick={handleClick2(item)}>
            {item} (Method 2)
          </button>
        </li>
      ))}
      
      {/* Method 3 */}
      {items.map(item => (
        <li key={item}>
          <button data-item={item} onClick={handleClick3}>
            {item} (Method 3)
          </button>
        </li>
      ))}
    </ul>
  );
}
```

#### **Pattern 2: Event Delegation**
```jsx
function EventDelegation() {
  const handleListClick = (e) => {
    // Check if a list item was clicked
    if (e.target.tagName === 'LI') {
      console.log('Clicked item:', e.target.textContent);
    }
    
    // Check if a button inside list item was clicked
    if (e.target.tagName === 'BUTTON') {
      console.log('Clicked button in:', 
        e.target.parentElement.textContent.replace('Delete', ''));
    }
  };
  
  return (
    <ul onClick={handleListClick}>
      <li>Item 1 <button>Delete</button></li>
      <li>Item 2 <button>Delete</button></li>
      <li>Item 3 <button>Delete</button></li>
    </ul>
  );
}
```

#### **Pattern 3: Custom Event Handlers with State**
```jsx
function SmartButton() {
  const [clickCount, setClickCount] = useState(0);
  const [lastClickTime, setLastClickTime] = useState(null);
  
  const handleClick = (e) => {
    const now = new Date();
    
    // Update state
    setClickCount(prev => prev + 1);
    setLastClickTime(now);
    
    // Use event properties
    const buttonText = e.target.textContent;
    const clickPosition = { x: e.clientX, y: e.clientY };
    
    console.log(`Button "${buttonText}" clicked at`, clickPosition);
    console.log(`Total clicks: ${clickCount + 1}`);
    console.log(`Time: ${now.toLocaleTimeString()}`);
    
    // Special behavior on 5th click
    if (clickCount + 1 === 5) {
      alert('Congratulations! You clicked 5 times!');
    }
  };
  
  return (
    <div>
      <button onClick={handleClick}>
        Click me ({clickCount} times)
      </button>
      
      {lastClickTime && (
        <p>Last clicked: {lastClickTime.toLocaleTimeString()}</p>
      )}
      
      {clickCount >= 10 && (
        <p style={{ color: 'green' }}>You're really clicking a lot! 🎉</p>
      )}
    </div>
  );
}
```

### **Form Event Handling**

Forms in React use **controlled components** - form data is handled by React state.

#### **Basic Form Handling:**
```jsx
function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Send data to server
  };
  
  const handleReset = () => {
    setFormData({
      username: '',
      password: '',
      rememberMe: false
    });
  };
  
  return (
    <form onSubmit={handleSubmit} onReset={handleReset}>
      <div>
        <label>
          Username:
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            onFocus={() => console.log('Username focused')}
            onBlur={() => console.log('Username blurred')}
          />
        </label>
      </div>
      
      <div>
        <label>
          Password:
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
          />
        </label>
      </div>
      
      <div>
        <label>
          <input
            type="checkbox"
            name="rememberMe"
            checked={formData.rememberMe}
            onChange={handleChange}
          />
          Remember me
        </label>
      </div>
      
      <button type="submit">Login</button>
      <button type="reset">Reset</button>
      <button type="button" onClick={handleReset}>
        Clear (Custom)
      </button>
    </form>
  );
}
```

#### **Complex Form with Validation:**
```jsx
function RegistrationForm() {
  const [form, setForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  // Validation function
  const validate = () => {
    const newErrors = {};
    
    if (!form.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!form.password) {
      newErrors.password = 'Password is required';
    } else if (form.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!form.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the terms';
    }
    
    return newErrors;
  };
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    
    // Validate on blur
    const newErrors = validate();
    setErrors(prev => ({ ...prev, [name]: newErrors[name] || '' }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const newErrors = validate();
    setErrors(newErrors);
    setTouched(Object.keys(form).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));
    
    if (Object.keys(newErrors).length === 0) {
      console.log('Form submitted successfully:', form);
      // Submit to server
    } else {
      console.log('Form has errors:', newErrors);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label>Email:</label>
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.email && touched.email ? 'error' : ''}
        />
        {errors.email && touched.email && (
          <span className="error-message">{errors.email}</span>
        )}
      </div>
      
      <div>
        <label>Password:</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.password && touched.password ? 'error' : ''}
        />
        {errors.password && touched.password && (
          <span className="error-message">{errors.password}</span>
        )}
      </div>
      
      <div>
        <label>Confirm Password:</label>
        <input
          type="password"
          name="confirmPassword"
          value={form.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.confirmPassword && touched.confirmPassword ? 'error' : ''}
        />
        {errors.confirmPassword && touched.confirmPassword && (
          <span className="error-message">{errors.confirmPassword}</span>
        )}
      </div>
      
      <div>
        <label>
          <input
            type="checkbox"
            name="agreeToTerms"
            checked={form.agreeToTerms}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          I agree to the terms and conditions
        </label>
        {errors.agreeToTerms && touched.agreeToTerms && (
          <span className="error-message">{errors.agreeToTerms}</span>
        )}
      </div>
      
      <button type="submit" disabled={Object.keys(errors).length > 0}>
        Register
      </button>
    </form>
  );
}
```

### **Custom Event Handlers and Hooks**

#### **Creating Custom Event Hooks:**
```jsx
// Custom hook for click outside detection
function useClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (event) => {
      // Do nothing if clicking ref's element or descendent elements
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      handler(event);
    };
    
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);
    
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

// Usage
function Dropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef();
  
  useClickOutside(dropdownRef, () => setIsOpen(false));
  
  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button onClick={() => setIsOpen(!isOpen)}>
        Menu {isOpen ? '▲' : '▼'}
      </button>
      
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          background: 'white',
          border: '1px solid #ccc',
          padding: '10px'
        }}>
          <div onClick={() => console.log('Option 1')}>Option 1</div>
          <div onClick={() => console.log('Option 2')}>Option 2</div>
          <div onClick={() => console.log('Option 3')}>Option 3</div>
        </div>
      )}
    </div>
  );
}
```

#### **Keyboard Shortcuts Hook:**
```jsx
function useKeyboardShortcut(key, callback) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === key && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        callback();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [key, callback]);
}

// Usage
function DocumentEditor() {
  const [content, setContent] = useState('');
  
  useKeyboardShortcut('s', () => {
    alert('Document saved!');
    // Save logic here
  });
  
  useKeyboardShortcut('z', () => {
    console.log('Undo');
    // Undo logic here
  });
  
  return (
    <textarea
      value={content}
      onChange={(e) => setContent(e.target.value)}
      placeholder="Type here... (Ctrl+S to save, Ctrl+Z to undo)"
      rows={10}
      cols={50}
    />
  );
}
```

### **Performance Considerations**

#### **Problem: Inline Function Creation**
```jsx
// ❌ Creates new function on every render
function ProblemComponent() {
  return (
    <button onClick={() => console.log('Clicked')}>
      Click me
    </button>
  );
}

// ✅ Use useCallback for stable references
function SolutionComponent() {
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);
  
  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
}
```

#### **Problem: Event Bubbling Performance**
```jsx
function LargeList() {
  const items = Array(1000).fill().map((_, i) => `Item ${i + 1}`);
  
  // ❌ Adds 1000 event listeners
  return (
    <ul>
      {items.map(item => (
        <li key={item} onClick={() => console.log(item)}>
          {item}
        </li>
      ))}
    </ul>
  );
  
  // ✅ Better: Event delegation
  const handleListClick = useCallback((e) => {
    if (e.target.tagName === 'LI') {
      console.log(e.target.textContent);
    }
  }, []);
  
  return (
    <ul onClick={handleListClick}>
      {items.map(item => (
        <li key={item} data-item={item}>
          {item}
        </li>
      ))}
    </ul>
  );
}
```

### **Common Event Patterns in Real Applications**

#### **Pattern 1: Debounced Search**
```jsx
function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Debounce search input
  const debouncedSearch = useDebouncedCallback((searchTerm) => {
    if (searchTerm) {
      setLoading(true);
      fetchResults(searchTerm).then(data => {
        setResults(data);
        setLoading(false);
      });
    } else {
      setResults([]);
    }
  }, 500);
  
  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };
  
  const handleKeyDown = (e) => {
    // Navigate results with arrow keys
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      // Focus next result
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      // Focus previous result
    }
    if (e.key === 'Enter') {
      // Submit search
    }
    if (e.key === 'Escape') {
      setQuery('');
      setResults([]);
    }
  };
  
  return (
    <div className="search-container">
      <input
        type="search"
        value={query}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onFocus={() => console.log('Search focused')}
        onBlur={() => setTimeout(() => setResults([]), 200)} // Close on blur with delay
        placeholder="Search..."
      />
      
      {loading && <div className="spinner">Searching...</div>}
      
      {results.length > 0 && (
        <div className="search-results">
          {results.map(result => (
            <div
              key={result.id}
              onClick={() => {
                setQuery(result.title);
                setResults([]);
                console.log('Selected:', result);
              }}
              onMouseEnter={(e) => e.currentTarget.classList.add('hovered')}
              onMouseLeave={(e) => e.currentTarget.classList.remove('hovered')}
              className="search-result"
            >
              {result.title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### **Pattern 2: Drag and Drop**
```jsx
function DraggableList() {
  const [items, setItems] = useState(['Item 1', 'Item 2', 'Item 3', 'Item 4']);
  const [draggedItem, setDraggedItem] = useState(null);
  
  const handleDragStart = (e, index) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.currentTarget);
  };
  
  const handleDragOver = (e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };
  
  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    
    if (draggedItem !== null && draggedItem !== dropIndex) {
      const newItems = [...items];
      const [removed] = newItems.splice(draggedItem, 1);
      newItems.splice(dropIndex, 0, removed);
      setItems(newItems);
    }
    
    setDraggedItem(null);
  };
  
  return (
    <ul className="draggable-list">
      {items.map((item, index) => (
        <li
          key={item}
          draggable
          onDragStart={(e) => handleDragStart(e, index)}
          onDragOver={(e) => handleDragOver(e, index)}
          onDrop={(e) => handleDrop(e, index)}
          onDragEnd={() => setDraggedItem(null)}
          className={draggedItem === index ? 'dragging' : ''}
        >
          {item} ↕
        </li>
      ))}
    </ul>
  );
}
```

#### **Pattern 3: Infinite Scroll**
```jsx
function InfiniteScrollList() {
  const [items, setItems] = useState(Array(20).fill().map((_, i) => `Item ${i + 1}`));
  const [loading, setLoading] = useState(false);
  const observerRef = useRef();
  
  const loadMoreItems = () => {
    if (loading) return;
    
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const newItems = Array(10).fill().map((_, i) => 
        `Item ${items.length + i + 1}`
      );
      setItems(prev => [...prev, ...newItems]);
      setLoading(false);
    }, 1000);
  };
  
  // Intersection Observer for detecting when to load more
  const lastItemRef = useCallback(node => {
    if (loading) return;
    
    if (observerRef.current) {
      observerRef.current.disconnect();
    }
    
    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        loadMoreItems();
      }
    });
    
    if (node) {
      observerRef.current.observe(node);
    }
  }, [loading]);
  
  const handleScroll = (e) => {
    // Alternative: Check if user scrolled near bottom
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    
    if (isNearBottom && !loading) {
      loadMoreItems();
    }
  };
  
  return (
    <div 
      className="scroll-container"
      onScroll={handleScroll}
      style={{ height: '400px', overflow: 'auto' }}
    >
      <ul>
        {items.map((item, index) => {
          if (index === items.length - 1) {
            return (
              <li 
                key={item}
                ref={lastItemRef}
                style={{ padding: '20px', borderBottom: '1px solid #ccc' }}
              >
                {item}
              </li>
            );
          }
          
          return (
            <li 
              key={item}
              style={{ padding: '20px', borderBottom: '1px solid #ccc' }}
            >
              {item}
            </li>
          );
        })}
      </ul>
      
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          Loading more items...
        </div>
      )}
    </div>
  );
}
```

### **Event Best Practices**

#### **1. Use Synthetic Events Properly:**
```jsx
function EventBestPractices() {
  const handleClick = (e) => {
    // ✅ Access synthetic event properties
    console.log(e.type); // "click"
    console.log(e.target); // The clicked element
    
    // ✅ Prevent default behavior
    e.preventDefault();
    
    // ✅ Stop propagation
    e.stopPropagation();
    
    // ❌ Don't access native event directly (usually)
    // console.log(e.nativeEvent);
    
    // ❌ Synthetic events are pooled - don't access asynchronously
    setTimeout(() => {
      // console.log(e.type); // This might not work
    }, 0);
    
    // ✅ If you need event in async code, persist it
    e.persist(); // Now you can access it asynchronously
    setTimeout(() => {
      console.log(e.type); // This works after persist()
    }, 0);
  };
  
  return <button onClick={handleClick}>Click</button>;
}
```

#### **2. Clean Up Event Listeners:**
```jsx
function EventCleanup() {
  useEffect(() => {
    const handleResize = () => {
      console.log('Window resized');
    };
    
    const handleClick = (e) => {
      console.log('Document clicked at:', e.clientX, e.clientY);
    };
    
    // Add event listeners
    window.addEventListener('resize', handleResize);
    document.addEventListener('click', handleClick);
    
    // Cleanup function
    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('click', handleClick);
    };
  }, []);
  
  return <div>Check console for events</div>;
}
```

### **Common Event-Related Errors**

#### **Error 1: Calling Instead of Passing Function**
```jsx
// ❌ Wrong: Calls function immediately
<button onClick={handleClick()}>Click</button>

// ✅ Correct: Passes function reference
<button onClick={handleClick}>Click</button>

// ✅ Also correct: Inline arrow function
<button onClick={() => handleClick()}>Click</button>
```

#### **Error 2: Not Preventing Default Form Submission**
```jsx
function Form() {
  const handleSubmit = () => {
    console.log('Submitting...');
    // Forgot to prevent default - page will refresh!
  };
  
  // ❌ Page refreshes
  return <form onSubmit={handleSubmit}>...</form>;
  
  // ✅ Prevents page refresh
  const handleSubmitCorrect = (e) => {
    e.preventDefault();
    console.log('Submitting...');
  };
  
  return <form onSubmit={handleSubmitCorrect}>...</form>;
}
```

#### **Error 3: Event Bubbling Issues**
```jsx
function NestedClicks() {
  const handleParentClick = () => {
    console.log('Parent clicked');
  };
  
  const handleChildClick = (e) => {
    console.log('Child clicked');
    // ❌ Without this, both parent and child log
    e.stopPropagation();
  };
  
  return (
    <div onClick={handleParentClick} style={{ padding: '50px', background: 'lightblue' }}>
      Parent Area
      <button onClick={handleChildClick} style={{ margin: '20px' }}>
        Click me
      </button>
    </div>
  );
}
```

### **Summary**

**Key Takeaways:**
1. **React events use camelCase** (`onClick`, `onChange`)
2. **Pass function references**, not function calls
3. **Event handlers receive synthetic events** with browser consistency
4. **Forms use controlled components** with React state
5. **Prevent default behavior** with `e.preventDefault()`
6. **Stop event bubbling** with `e.stopPropagation()`
7. **Clean up event listeners** in useEffect cleanup

**Common Event Types:**
- **Mouse:** `onClick`, `onDoubleClick`, `onMouseEnter`, `onMouseLeave`
- **Keyboard:** `onKeyDown`, `onKeyUp`, `onKeyPress`
- **Form:** `onChange`, `onSubmit`, `onFocus`, `onBlur`
- **Touch:** `onTouchStart`, `onTouchMove`, `onTouchEnd`
- **Drag:** `onDragStart`, `onDragOver`, `onDrop`

**Remember:** Event handling is what makes React apps interactive. Master events, and you can build any user interaction!

---

**Ready for Topic 36: "React Forms"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/JavaScript ES6 Arrow Functions|JavaScript ES6 Arrow Functions]]
- [[Web Development/React/React Topics/React Forms|React Forms]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
