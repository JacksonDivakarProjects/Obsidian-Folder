## **13. JavaScript ES6 - Import, Export and Modules - Complete Beginner's Guide**

### **Introduction**
Welcome to JavaScript modules! This is a crucial concept that makes modern React development possible. Today we'll learn how to **organize, share, and reuse** code across multiple files using ES6 modules. This is the foundation of how React applications are structured.

### **Why Modules Matter?**

**Before Modules (The Problem):**
```html
<!-- Old way - everything in one file -->
<script src="utils.js"></script>
<script src="components.js"></script>
<script src="app.js"></script>
<!-- Global namespace pollution -->
<!-- Dependency management issues -->
<!-- Hard to maintain -->
```

**After Modules (The Solution):**
```javascript
// Modern way - organized modules
import { formatDate } from './utils';
import Button from './components/Button';
import App from './App';
// Clean, organized, maintainable
```

### **What are ES6 Modules?**

**Modules** are reusable pieces of JavaScript code that can be exported from one file and imported into another. Think of them as **code packages** that you can share between files.

#### **Simple Analogy:**
- **Module** = A book chapter
- **Export** = Publishing the chapter
- **Import** = Reading the chapter in another book
- **Default Export** = The main chapter
- **Named Export** = Specific sections within the chapter

### **Basic Module Syntax**

#### **1. Exporting (Making Code Available)**
```javascript
// mathUtils.js

// Named export - export individual items
export const PI = 3.14159;

export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

// Default export - export one main thing
export default function calculator(operation, a, b) {
  switch(operation) {
    case 'add': return add(a, b);
    case 'multiply': return multiply(a, b);
    default: return null;
  }
}
```

#### **2. Importing (Using Code from Other Files)**
```javascript
// app.js

// Import named exports (must use exact names)
import { PI, add } from './mathUtils.js';

// Import with alias (rename if needed)
import { multiply as times } from './mathUtils.js';

// Import default export (any name works)
import calculator from './mathUtils.js';

// Import everything
import * as MathUtils from './mathUtils.js';

// Usage
console.log(PI); // 3.14159
console.log(add(2, 3)); // 5
console.log(times(2, 3)); // 6
console.log(calculator('add', 5, 10)); // 15
console.log(MathUtils.multiply(4, 5)); // 20
```

### **Export Types Explained**

#### **1. Named Exports (Multiple per file)**
```javascript
// constants.js

// Export individual values
export const API_URL = 'https://api.example.com';
export const MAX_RETRIES = 3;
export const TIMEOUT = 5000;

// Export functions
export function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Export classes
export class User {
  constructor(name) {
    this.name = name;
  }
}

// Export after declaration
const SECRET_KEY = 'abc123';
export { SECRET_KEY };

// Export with alias
const internalFunction = () => { /* ... */ };
export { internalFunction as publicFunction };
```

#### **2. Default Export (One per file)**
```javascript
// UserService.js

// Only one default export per file
const UserService = {
  getAllUsers: () => { /* ... */ },
  getUserById: (id) => { /* ... */ },
  createUser: (userData) => { /* ... */ }
};

export default UserService;

// Alternative syntax
export default class Product {
  constructor(name, price) {
    this.name = name;
    this.price = price;
  }
}
```

#### **3. Mixed Exports (Both named and default)**
```javascript
// utils.js

// Named exports
export const formatCurrency = (amount) => `$${amount.toFixed(2)}`;
export const formatDate = (date) => date.toLocaleDateString();

// Default export
const Utils = {
  formatCurrency,
  formatDate,
  truncateText: (text, length) => text.slice(0, length) + '...'
};

export default Utils;
```

### **Import Types Explained**

#### **1. Importing Named Exports**
```javascript
// Import specific items
import { formatCurrency, formatDate } from './utils.js';

// Import with different names (aliasing)
import { formatCurrency as formatMoney } from './utils.js';

// Import multiple items
import { 
  API_URL, 
  MAX_RETRIES, 
  TIMEOUT 
} from './constants.js';
```

#### **2. Importing Default Exports**
```javascript
// Import default - any name works
import UserService from './UserService.js';
import Product from './Product.js';
import Utils from './utils.js';

// You can rename default imports
import MyUtils from './utils.js'; // Still works!
```

#### **3. Import Everything**
```javascript
// Import all exports as an object
import * as Constants from './constants.js';
import * as MathUtils from './mathUtils.js';

// Usage
console.log(Constants.API_URL);
console.log(MathUtils.add(2, 3));
```

#### **4. Side-effect Imports (No bindings)**
```javascript
// Import a module for its side effects only
import './styles.css'; // CSS file
import './initialize.js'; // Runs initialization code
import './analytics.js'; // Sets up analytics
```

### **Module File Structure in React**

#### **Typical React Project Structure:**
```
src/
├── components/          # React components
│   ├── Button.js       # Individual component
│   ├── Header.js
│   └── Footer.js
├── utils/              # Utility functions
│   ├── formatters.js
│   └── validators.js
├── constants/          # Constants
│   └── config.js
├── services/           # API services
│   └── api.js
├── App.js             # Main app component
└── index.js           # Entry point
```

### **Practical Examples**

#### **Example 1: Utility Module**
```javascript
// utils/formatters.js

// Named exports for individual functions
export function formatCurrency(amount, currency = 'USD') {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  });
  return formatter.format(amount);
}

export function formatDate(date, locale = 'en-US') {
  return new Date(date).toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

export function truncateText(text, maxLength = 100) {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

// Default export for the whole utility set
export default {
  formatCurrency,
  formatDate,
  truncateText
};
```

#### **Example 2: Constants Module**
```javascript
// constants/config.js

// Application configuration
export const APP_NAME = 'My React App';
export const VERSION = '1.0.0';

// API Configuration
export const API_BASE_URL = 'https://api.example.com';
export const API_ENDPOINTS = {
  USERS: '/users',
  PRODUCTS: '/products',
  ORDERS: '/orders'
};

// UI Constants
export const COLORS = {
  PRIMARY: '#007bff',
  SECONDARY: '#6c757d',
  SUCCESS: '#28a745',
  DANGER: '#dc3545'
};

// Local Storage Keys
export const STORAGE_KEYS = {
  USER_TOKEN: 'user_token',
  USER_DATA: 'user_data',
  SETTINGS: 'app_settings'
};
```

#### **Example 3: React Component Module**
```javascript
// components/Button.js
import React from 'react';
import PropTypes from 'prop-types';

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
    outline: { backgroundColor: 'transparent', border: '2px solid #007bff', color: '#007bff' }
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

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  onClick: PropTypes.func,
  disabled: PropTypes.bool
};

export default Button;
```

### **Module Usage in React Components**

#### **Complete Example: App with Multiple Modules**
```javascript
// App.js
import React, { useState } from 'react';
// Import components
import Header from './components/Header';
import Button from './components/Button';
import ProductCard from './components/ProductCard';
// Import utilities
import { formatCurrency, formatDate } from './utils/formatters';
// Import constants
import { APP_NAME, COLORS } from './constants/config';
// Import services
import ProductService from './services/ProductService';
// Import CSS
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  
  const handleLoadProducts = async () => {
    const data = await ProductService.getProducts();
    setProducts(data);
  };
  
  const currentDate = formatDate(new Date());
  const totalValue = products.reduce((sum, product) => sum + product.price, 0);
  
  return (
    <div className="App">
      <Header title={APP_NAME} />
      
      <main>
        <div className="dashboard">
          <h2>Product Dashboard</h2>
          <p>Today is {currentDate}</p>
          
          <Button 
            variant="primary" 
            onClick={handleLoadProducts}
          >
            Load Products
          </Button>
          
          <div className="stats">
            <p>Total Products: {products.length}</p>
            <p>Total Value: {formatCurrency(totalValue)}</p>
          </div>
          
          <div className="product-grid">
            {products.map(product => (
              <ProductCard 
                key={product.id}
                product={product}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
```

### **Common Patterns and Best Practices**

#### **1. Barrel Exports (Index Files)**
```javascript
// components/index.js - Barrel file
export { default as Button } from './Button';
export { default as Header } from './Header';
export { default as Footer } from './Footer';
export { default as Card } from './Card';

// Usage - Clean import from one file
import { Button, Header, Footer } from './components';
```

#### **2. Absolute vs Relative Imports**
```javascript
// ❌ Hard to maintain (deep nesting)
import Button from '../../../components/Button';

// ✅ Better with path configuration or barrel files
import Button from '@/components/Button'; // Configured alias
import { Button } from '../../components'; // Using barrel
```

#### **3. Lazy Loading with Dynamic Imports**
```javascript
// Regular import (eager loading)
import HeavyComponent from './HeavyComponent';

// Dynamic import (lazy loading)
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

// Usage with Suspense
function App() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </React.Suspense>
  );
}
```

### **Module Resolution**

#### **File Extensions:**
```javascript
// With extension
import Button from './Button.js'; // Explicit
import styles from './App.css'; // CSS file

// Without extension (React convention)
import Button from './Button'; // .js assumed
import App from './App'; // .jsx also works
```

#### **Directory Imports:**
```javascript
// If you have an index.js file in a folder
import utils from './utils'; // Imports ./utils/index.js
import components from './components'; // Imports ./components/index.js
```

### **Common Errors and Solutions**

#### **Error 1: Import Not Found**
```javascript
// ❌ File doesn't exist
import Something from './nonexistent.js'; // Error

// ✅ Check file path and extension
import Something from './existing.js'; // Correct path
```

#### **Error 2: Wrong Export/Import Type**
```javascript
// math.js
export function add(a, b) { return a + b; }

// ❌ Trying to import as default
import add from './math.js'; // add will be undefined

// ✅ Import as named export
import { add } from './math.js'; // Correct
```

#### **Error 3: Circular Dependencies**
```javascript
// ❌ Circular dependency
// fileA.js
import { b } from './fileB.js';
export const a = 'A';

// fileB.js
import { a } from './fileA.js'; // Circular!
export const b = 'B';

// ✅ Restructure to avoid circular dependencies
```

### **Practice Exercises**

#### **Exercise 1: Create and Use a Utility Module**
Create a utility module with formatting functions:

```javascript
// utils/stringUtils.js
// Create functions:
// 1. capitalizeFirstLetter(string)
// 2. reverseString(string)
// 3. countWords(string)
// Export them as named exports

// Then import and use them in App.js
```

**Solution:**
```javascript
// utils/stringUtils.js
export function capitalizeFirstLetter(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function reverseString(str) {
  return str.split('').reverse().join('');
}

export function countWords(str) {
  return str.trim().split(/\s+/).length;
}

// App.js
import { 
  capitalizeFirstLetter, 
  reverseString, 
  countWords 
} from './utils/stringUtils';

function App() {
  const text = "hello world this is react";
  
  return (
    <div>
      <p>Original: {text}</p>
      <p>Capitalized: {capitalizeFirstLetter(text)}</p>
      <p>Reversed: {reverseString(text)}</p>
      <p>Word Count: {countWords(text)}</p>
    </div>
  );
}
```

#### **Exercise 2: Create a Configuration Module**
```javascript
// config/settings.js
// Create a configuration object with:
// 1. App settings (name, version, environment)
// 2. API settings (base URL, endpoints)
// 3. Theme settings (colors, fonts)
// Export as named exports

// Import and use in multiple components
```

#### **Exercise 3: Component Module with Props Validation**
```javascript
// components/Alert.js
// Create an Alert component that:
// 1. Accepts type (success, error, warning, info)
// 2. Accepts message
// 3. Accepts onClose function
// 4. Has PropTypes validation
// 5. Export as default

// Use it in App.js with different types
```

### **Module Patterns in Real Projects**

#### **Pattern 1: Service Layer**
```javascript
// services/AuthService.js
import { API_BASE_URL } from '../constants/config';

class AuthService {
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  }
  
  async register(userData) {
    // Registration logic
  }
  
  logout() {
    // Clear tokens
  }
}

export default new AuthService(); // Single instance

// Usage in component
import authService from '../services/AuthService';

const handleLogin = async () => {
  const result = await authService.login(email, password);
  // Handle result
};
```

#### **Pattern 2: Custom Hooks**
```javascript
// hooks/useLocalStorage.js
import { useState } from 'react';

export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });
  
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
import { useLocalStorage } from '../hooks/useLocalStorage';

function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  // ...
}
```

#### **Pattern 3: Context Provider**
```javascript
// context/ThemeContext.js
import React, { createContext, useState, useContext } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Usage
import { ThemeProvider, useTheme } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <ThemedComponent />
    </ThemeProvider>
  );
}

function ThemedComponent() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className={`app ${theme}`}>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
}
```

### **Module Bundling and Build Process**

#### **What Happens Behind the Scenes:**
```
Your Modules → Bundler (Webpack) → Single Bundle File
   │              │                    │
   ├── Component A│                    │
   ├── Component B│ → Tree Shaking →   │ → Optimized for
   ├── Utility    │   Minification     │   Production
   └── Styles     │   Code Splitting   │
```

### **Best Practices Summary**

1. **One component per file** (except related small components)
2. **Use named exports** for utilities and constants
3. **Use default exports** for components and main services
4. **Create index.js files** for clean imports from folders
5. **Organize by feature** not by type
6. **Use absolute paths** for deeply nested imports
7. **Lazy load** heavy components
8. **Validate props** with PropTypes

### **Quick Reference Cheat Sheet**

#### **Export Syntax:**
```javascript
// Named exports
export const name = 'value';
export function func() {}
export class ClassName {}

// Default export
export default Component;

// Export list
export { name1, name2 };

// Rename exports
export { name as newName };
```

#### **Import Syntax:**
```javascript
// Named imports
import { name1, name2 } from './module';

// Default import
import Component from './module';

// Mixed import
import Component, { name1 } from './module';

// Import all
import * as Module from './module';

// Rename imports
import { name as newName } from './module';
```

### **Practice Challenge: Build a Modular React App**

**Challenge:** Create a small modular application with:
1. `components/` - Button, Card, Header, Footer
2. `utils/` - formatters.js, validators.js
3. `constants/` - config.js, messages.js
4. `services/` - api.js, storage.js
5. `hooks/` - useFetch.js, useForm.js

**Requirements:**
- Each module should export properly
- Use both named and default exports appropriately
- Create barrel files for clean imports
- Import and use modules in App.js

### **Summary**

**Key Takeaways:**
1. **Modules** organize code into reusable, maintainable units
2. **Named exports** for multiple items from a file
3. **Default export** for the main item from a file
4. **Import** brings modules into other files
5. **Barrel exports** clean up import statements
6. **Proper organization** is key to scalable applications

**Remember:** Good module structure makes your codebase more maintainable, testable, and scalable. This is especially important in React where components are the building blocks of your application.

---

**Ready for Topic 14: "Javascript ES6 Import, Export and Modules Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/React Components|React Components]]
- [[Web Development/React/React Topics/What We Will Make in This React Module|What We Will Make in This React Module]]
