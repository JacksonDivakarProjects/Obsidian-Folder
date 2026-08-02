## **28. React Conditional Rendering with the Ternary Operator & AND Operator - Complete Beginner's Guide**

### **Introduction**
Welcome to **conditional rendering** - the art of showing different UI based on conditions! In React, we don't use `if-else` statements in JSX directly. Instead, we use JavaScript operators like **ternary (`? :`)** and **logical AND (`&&`)**. Let's master this essential skill!

### **Why Conditional Rendering?**

Think of a website that:
- Shows "Login" button when you're logged out
- Shows "Welcome, User!" when you're logged in
- Displays loading spinner while fetching data
- Shows error messages when something goes wrong

All of this is **conditional rendering**!

### **The Problem with If-Else in JSX**

```jsx
// ❌ This doesn't work in JSX!
function Greeting() {
  return (
    <div>
      if (isLoggedIn) {
        <h1>Welcome back!</h1>
      } else {
        <h1>Please sign in.</h1>
      }
    </div>
  );
}
```

### **Solution 1: Ternary Operator (`? :`)**

The ternary operator is perfect for **"either/or"** scenarios.

#### **Syntax:**
```javascript
condition ? expressionIfTrue : expressionIfFalse
```

#### **Basic Example:**
```jsx
function UserGreeting({ isLoggedIn, userName }) {
  return (
    <div>
      {isLoggedIn ? (
        <h1>Welcome back, {userName}!</h1>
      ) : (
        <h1>Please sign in to continue.</h1>
      )}
    </div>
  );
}
```

#### **Real-World Examples:**

**Example 1: Theme Toggle**
```jsx
function ThemeToggle({ isDarkMode }) {
  return (
    <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
      <h1>{isDarkMode ? 'Dark Mode' : 'Light Mode'}</h1>
      <button>
        Switch to {isDarkMode ? 'Light' : 'Dark'} Mode
      </button>
    </div>
  );
}
```

**Example 2: Form Validation Message**
```jsx
function EmailInput({ email, isValid }) {
  return (
    <div>
      <input 
        type="email" 
        value={email} 
        placeholder="Enter email" 
      />
      {isValid ? (
        <span style={{ color: 'green' }}>✓ Valid email</span>
      ) : (
        <span style={{ color: 'red' }}>Please enter a valid email</span>
      )}
    </div>
  );
}
```

**Example 3: User Role Display**
```jsx
function UserRoleBadge({ role }) {
  return (
    <span className={`badge ${role === 'admin' ? 'badge-admin' : 'badge-user'}`}>
      {role === 'admin' ? 'Administrator' : 
       role === 'moderator' ? 'Moderator' : 
       'Regular User'}
    </span>
  );
}
```

### **Solution 2: Logical AND Operator (`&&`)**

The AND operator is perfect for **"show/hide"** scenarios.

#### **Syntax:**
```javascript
condition && expression
```
- If condition is true, returns expression
- If condition is false, returns false (React renders nothing)

#### **Basic Example:**
```jsx
function Notification({ hasUnread, count }) {
  return (
    <div>
      <button>Notifications</button>
      {hasUnread && (
        <span className="badge">{count}</span>
      )}
    </div>
  );
}
```

#### **Real-World Examples:**

**Example 1: Loading Spinner**
```jsx
function DataDisplay({ isLoading, data }) {
  return (
    <div>
      {isLoading && (
        <div className="spinner">Loading...</div>
      )}
      
      {!isLoading && data && (
        <div className="data">
          <h2>{data.title}</h2>
          <p>{data.content}</p>
        </div>
      )}
      
      {!isLoading && !data && (
        <p>No data available</p>
      )}
    </div>
  );
}
```

**Example 2: Feature Flags**
```jsx
function App({ user, features }) {
  return (
    <div>
      <Header />
      <MainContent />
      
      {features.enableChat && <ChatWidget />}
      {features.enableAnalytics && <AnalyticsDashboard />}
      {features.isBetaTester && <BetaFeatures />}
      
      {user.isAdmin && <AdminPanel />}
    </div>
  );
}
```

**Example 3: Form Wizard Steps**
```jsx
function SignupWizard({ currentStep }) {
  return (
    <div className="wizard">
      <h1>Create Account</h1>
      
      {currentStep === 1 && <PersonalInfoStep />}
      {currentStep === 2 && <AccountDetailsStep />}
      {currentStep === 3 && <PreferencesStep />}
      {currentStep === 4 && <ConfirmationStep />}
      
      <div className="navigation">
        {currentStep > 1 && <button>Previous</button>}
        {currentStep < 4 && <button>Next</button>}
        {currentStep === 4 && <button>Submit</button>}
      </div>
    </div>
  );
}
```

### **Combining Ternary and AND Operators**

#### **Complex Example: E-commerce Product Display**
```jsx
function ProductDisplay({ product, user }) {
  return (
    <div className="product">
      <img src={product.image} alt={product.name} />
      <h2>{product.name}</h2>
      
      {/* Price display with discount */}
      <div className="price">
        {product.discount > 0 ? (
          <>
            <span className="original">${product.price}</span>
            <span className="discounted">
              ${product.price - product.discount}
            </span>
            <span className="discount-badge">
              Save {product.discount}%
            </span>
          </>
        ) : (
          <span>${product.price}</span>
        )}
      </div>
      
      {/* Stock status */}
      {product.stock > 0 ? (
        <p className="in-stock">
          {product.stock < 10 ? `Only ${product.stock} left!` : 'In Stock'}
        </p>
      ) : (
        <p className="out-of-stock">Out of Stock</p>
      )}
      
      {/* Actions */}
      <div className="actions">
        <button>Add to Cart</button>
        
        {user.isLoggedIn && (
          <button>Add to Wishlist</button>
        )}
        
        {user.isPremium && product.premiumOnly && (
          <span className="premium-badge">Premium Exclusive</span>
        )}
      </div>
      
      {/* Reviews */}
      {product.reviews && product.reviews.length > 0 && (
        <div className="reviews">
          <h3>Reviews ({product.reviews.length})</h3>
          {product.reviews.slice(0, 3).map(review => (
            <Review key={review.id} review={review} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### **Common Patterns and Best Practices**

#### **Pattern 1: Early Returns (Outside JSX)**
```jsx
function UserProfile({ user }) {
  // Early return for loading state
  if (!user) {
    return <div>Loading user data...</div>;
  }
  
  // Early return for error state
  if (user.error) {
    return <div>Error loading user: {user.error}</div>;
  }
  
  // Main render
  return (
    <div>
      <h1>{user.name}</h1>
      {user.isAdmin && <AdminControls />}
      {/* ... rest of component */}
    </div>
  );
}
```

#### **Pattern 2: Conditional CSS Classes**
```jsx
function Message({ type, text }) {
  const className = `message ${type === 'error' ? 'message-error' : 
                               type === 'success' ? 'message-success' : 
                               type === 'warning' ? 'message-warning' : 
                               'message-info'}`;
  
  return (
    <div className={className}>
      {type === 'error' && '⚠️ '}
      {type === 'success' && '✅ '}
      {type === 'warning' && '⚠️ '}
      {text}
    </div>
  );
}
```

#### **Pattern 3: Conditional Attributes**
```jsx
function InputField({ disabled, required, error, ...props }) {
  return (
    <div>
      <input
        {...props}
        disabled={disabled}
        required={required}
        className={error ? 'input-error' : 'input-normal'}
        aria-invalid={!!error}
        aria-describedby={error ? 'error-message' : undefined}
      />
      {error && (
        <div id="error-message" className="error-text">
          {error}
        </div>
      )}
    </div>
  );
}
```

### **Advanced Conditional Rendering Techniques**

#### **Technique 1: Render Props Pattern**
```jsx
function ConditionalRenderer({ condition, renderTrue, renderFalse }) {
  return condition ? renderTrue() : renderFalse();
}

// Usage
<ConditionalRenderer
  condition={isLoading}
  renderTrue={() => <Spinner />}
  renderFalse={() => <Data data={data} />}
/>
```

#### **Technique 2: Component Switcher**
```jsx
function ComponentSwitcher({ view }) {
  const components = {
    home: <HomePage />,
    profile: <ProfilePage />,
    settings: <SettingsPage />,
    help: <HelpPage />
  };
  
  return components[view] || <NotFoundPage />;
}
```

#### **Technique 3: HOC for Conditional Rendering**
```jsx
function withCondition(condition, Component) {
  return function ConditionalComponent(props) {
    return condition(props) ? <Component {...props} /> : null;
  };
}

// Usage
const AdminOnlyButton = withCondition(
  props => props.user.isAdmin, 
  Button
);
```

### **Common Pitfalls and Solutions**

#### **Pitfall 1: Falsy Values with `&&`**
```jsx
// ❌ Problem: 0 renders as 0, not nothing
function Counter({ count }) {
  return (
    <div>
      <h2>Count: {count}</h2>
      {count && <p>Count is truthy</p>}
      {/* If count is 0, this renders: Count: 0 0 */}
    </div>
  );
}

// ✅ Solution: Explicit boolean check
function Counter({ count }) {
  return (
    <div>
      <h2>Count: {count}</h2>
      {count > 0 && <p>Count is positive</p>}
      {count !== 0 && <p>Count is not zero</p>}
    </div>
  );
}
```

#### **Pitfall 2: Nested Ternary Hell**
```jsx
// ❌ Hard to read
{isLoading ? <Spinner /> : 
  error ? <Error message={error} /> : 
  data ? <Data data={data} /> : 
  <EmptyState />}

// ✅ Better: Extract to separate function
function renderContent(isLoading, error, data) {
  if (isLoading) return <Spinner />;
  if (error) return <Error message={error} />;
  if (data) return <Data data={data} />;
  return <EmptyState />;
}

// In JSX
{renderContent(isLoading, error, data)}
```

#### **Pitfall 3: Side Effects in Ternary**
```jsx
// ❌ Side effects in render (bad practice)
{isValid ? (
  console.log('Valid!') && <SuccessMessage />
) : (
  <ErrorMessage />
)}

// ✅ Keep side effects separate
useEffect(() => {
  if (isValid) {
    console.log('Valid!');
  }
}, [isValid]);

{isValid ? <SuccessMessage /> : <ErrorMessage />}
```

### **Performance Considerations**

#### **1. Conditional Hook Calls**
```jsx
// ❌ NEVER do this - hooks must always be called
function Component({ condition }) {
  if (condition) {
    const [state, setState] = useState(''); // Conditional hook - ERROR!
  }
  // ...
}

// ✅ Always call hooks unconditionally
function Component({ condition }) {
  const [state, setState] = useState('');
  
  if (condition) {
    // Use the hook's value
    return <div>{state}</div>;
  }
  // ...
}
```

#### **2. Memoizing Conditional Components**
```jsx
import { useMemo } from 'react';

function ExpensiveComponent({ show, data }) {
  const expensiveResult = useMemo(() => {
    // Expensive calculation
    return processData(data);
  }, [data]);
  
  return show && <div>{expensiveResult}</div>;
}
```

### **Real-World React Examples**

#### **Example 1: Authentication Flow**
```jsx
function App() {
  const { user, isLoading, error } = useAuth();
  
  if (isLoading) {
    return (
      <div className="loading-screen">
        <Spinner />
        <p>Loading your experience...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="error-screen">
        <h1>Something went wrong</h1>
        <p>{error.message}</p>
        <button onClick={retry}>Retry</button>
      </div>
    );
  }
  
  return (
    <div className="app">
      {user ? (
        // Logged in view
        <>
          <Header user={user} />
          <Dashboard user={user} />
          {user.isAdmin && <AdminPanel />}
          <Footer />
        </>
      ) : (
        // Logged out view
        <>
          <LandingPage />
          <LoginForm />
          <SignupForm />
        </>
      )}
    </div>
  );
}
```

#### **Example 2: Data Table with Filters**
```jsx
function DataTable({ data, filters, sortBy }) {
  // Apply filters and sorting
  const filteredData = data.filter(item => {
    if (filters.activeOnly && !item.isActive) return false;
    if (filters.category && item.category !== filters.category) return false;
    return true;
  });
  
  const sortedData = [...filteredData].sort((a, b) => {
    if (sortBy === 'name') return a.name.localeCompare(b.name);
    if (sortBy === 'date') return new Date(b.date) - new Date(a.date);
    return a.id - b.id;
  });
  
  return (
    <div className="data-table">
      {/* Table controls */}
      <div className="controls">
        {data.length > 0 && (
          <p>Showing {sortedData.length} of {data.length} items</p>
        )}
        
        {filters.activeOnly && (
          <span className="filter-tag">Active only ✓</span>
        )}
        
        {filters.category && (
          <span className="filter-tag">{filters.category} ✓</span>
        )}
      </div>
      
      {/* Table content */}
      {sortedData.length === 0 ? (
        <div className="empty-state">
          <p>No data found</p>
          {Object.keys(filters).length > 0 && (
            <button onClick={clearFilters}>Clear filters</button>
          )}
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Status</th>
              {user.isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {sortedData.map(item => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.category}</td>
                <td>
                  <span className={`status ${item.isActive ? 'active' : 'inactive'}`}>
                    {item.isActive ? 'Active' : 'Inactive'}
                  </span>
                </td>
                {user.isAdmin && (
                  <td>
                    <button>Edit</button>
                    <button>Delete</button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

#### **Example 3: Multi-Step Form**
```jsx
function MultiStepForm({ steps, currentStep, formData }) {
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <PersonalInfo data={formData.personal} />;
      case 2:
        return <AddressInfo data={formData.address} />;
      case 3:
        return <PaymentInfo data={formData.payment} />;
      case 4:
        return <Review data={formData} />;
      default:
        return <div>Invalid step</div>;
    }
  };
  
  const isStepValid = (step) => {
    switch (step) {
      case 1: return validatePersonalInfo(formData.personal);
      case 2: return validateAddress(formData.address);
      case 3: return validatePayment(formData.payment);
      default: return true;
    }
  };
  
  return (
    <div className="multi-step-form">
      {/* Progress indicator */}
      <div className="progress">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`step ${currentStep > index + 1 ? 'completed' : 
                             currentStep === index + 1 ? 'active' : ''}`}
          >
            {currentStep > index + 1 ? '✓' : index + 1}
            <span>{step.title}</span>
          </div>
        ))}
      </div>
      
      {/* Step content */}
      <div className="step-content">
        {renderStepContent()}
      </div>
      
      {/* Navigation */}
      <div className="navigation">
        {currentStep > 1 && (
          <button onClick={goToPreviousStep}>
            Previous
          </button>
        )}
        
        {currentStep < steps.length ? (
          <button 
            onClick={goToNextStep}
            disabled={!isStepValid(currentStep)}
          >
            {isStepValid(currentStep) ? 'Next' : 'Complete this step'}
          </button>
        ) : (
          <button 
            onClick={submitForm}
            disabled={!isStepValid(currentStep)}
          >
            Submit
          </button>
        )}
      </div>
      
      {/* Debug info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <pre>{JSON.stringify(formData, null, 2)}</pre>
      )}
    </div>
  );
}
```

### **Quick Reference Cheat Sheet**

```jsx
// Ternary (either/or)
{condition ? <TrueComponent /> : <FalseComponent />}

// AND (show/hide)
{condition && <Component />}

// Multiple conditions
{(condition1 && condition2) && <Component />}
{condition1 || condition2 ? <Component /> : null}

// Conditional classes
<div className={`base-class ${isActive ? 'active' : ''}`}>

// Conditional attributes
<input disabled={isDisabled} required={isRequired} />

// Early returns (outside JSX)
if (!data) return <Loading />;

// Switch statements (in function)
const renderComponent = () => {
  switch(type) {
    case 'A': return <ComponentA />;
    case 'B': return <ComponentB />;
    default: return <DefaultComponent />;
  }
};
```

### **Best Practices Summary**

1. **Use ternaries** for "either/or" scenarios
2. **Use AND operator** for simple show/hide
3. **Extract complex logic** to separate functions
4. **Avoid nested ternaries** - use if-else or switch instead
5. **Be careful with falsy values** (0, '', false, null, undefined)
6. **Keep conditional rendering close to where it's used**
7. **Consider performance** for frequently changing conditions
8. **Always call hooks unconditionally**

### **Summary**

**Key Takeaways:**
1. **Ternary (`? :`)** - Choose between two options
2. **AND (`&&`)** - Show something only if condition is true
3. **Combine them** for complex conditional logic
4. **Use early returns** for loading/error states
5. **Keep JSX readable** - extract complex conditions

**Remember:** Conditional rendering makes your components dynamic and responsive to data. It's one of the most powerful patterns in React!

---

**Ready for Topic 29: "Conditional Rendering Practice"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Mapping Data to Components|Mapping Data to Components]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
- [[Web Development/React/React Topics/State in React - Declarative vs. Imperative Programming|State in React (Declarative vs Imperative)]]
