## **8. JSX Attributes & Styling React Elements - Complete Beginner's Guide**

### **Introduction**
Welcome to styling in React! Today we'll learn how to add **attributes** to JSX elements and style them. While JSX looks like HTML, there are important differences in how we add classes, styles, and other attributes. Let's master these fundamentals!

### **JSX Attributes: HTML vs JSX Comparison**

First, let's understand how HTML attributes translate to JSX:

| HTML Attribute | JSX Attribute | Notes |
|----------------|---------------|--------|
| `class` | `className` | `class` is a reserved word in JavaScript |
| `for` | `htmlFor` | `for` is also a reserved word |
| `onclick` | `onClick` | camelCase for events |
| `tabindex` | `tabIndex` | camelCase |
| `maxlength` | `maxLength` | camelCase |
| `readonly` | `readOnly` | camelCase, boolean attribute |

### **Basic JSX Attributes**

#### **1. String Attributes**
```jsx
// Simple string attributes
const element = (
  <div>
    <img 
      src="https://example.com/logo.png" 
      alt="Company Logo"
    />
    <a 
      href="https://reactjs.org"
      title="Visit React website"
      target="_blank"
      rel="noopener noreferrer"
    >
      Learn React
    </a>
    <input 
      type="text"
      placeholder="Enter your name"
      maxLength="50"
    />
  </div>
);
```

#### **2. Boolean Attributes**
```jsx
// Boolean attributes (no value needed)
const element = (
  <div>
    <input type="checkbox" checked />
    <input type="text" disabled />
    <button type="submit" disabled={true}>
      Submit
    </button>
    <textarea readOnly defaultValue="Read-only content" />
  </div>
);
```

#### **3. Dynamic Attributes**
```jsx
function DynamicAttributes() {
  const imageUrl = "https://example.com/user-profile.jpg";
  const altText = "User Profile Picture";
  const userId = "user123";
  const isDisabled = false;
  
  return (
    <div>
      <img 
        src={imageUrl} 
        alt={altText}
        data-user-id={userId}  // Custom data attribute
      />
      <button disabled={isDisabled}>
        {isDisabled ? "Loading..." : "Click Me"}
      </button>
    </div>
  );
}
```

### **Special JSX Attributes**

#### **1. className: Adding CSS Classes**
```jsx
function ClassNamesExample() {
  const isActive = true;
  const isError = false;
  
  return (
    <div>
      {/* Static class */}
      <div className="container">
        Static class
      </div>
      
      {/* Dynamic class */}
      <div className={`button ${isActive ? 'active' : ''}`}>
        Dynamic class
      </div>
      
      {/* Multiple dynamic classes */}
      <div className={`
        card 
        ${isActive ? 'card-active' : 'card-inactive'}
        ${isError ? 'error' : ''}
      `}>
        Multiple classes
      </div>
      
      {/* Using a function for complex logic */}
      <div className={getButtonClasses(isActive, isError)}>
        Function-based classes
      </div>
    </div>
  );
}

function getButtonClasses(isActive, isError) {
  let classes = "button";
  if (isActive) classes += " active";
  if (isError) classes += " error";
  return classes;
}
```

#### **2. style: Inline Styling**
JSX uses JavaScript objects for inline styles:

```jsx
function InlineStyles() {
  return (
    <div>
      {/* Basic inline style */}
      <div style={{ color: 'blue', fontSize: '16px' }}>
        Blue text, 16px size
      </div>
      
      {/* Dynamic styles */}
      <div style={{
        backgroundColor: 'lightgray',
        padding: '20px',
        borderRadius: '8px',
        margin: '10px 0'
      }}>
        Card-like container
      </div>
      
      {/* Style with variables */}
      <div style={boxStyle}>
        Styled with variable
      </div>
    </div>
  );
}

// Style object defined outside
const boxStyle = {
  border: '2px solid #333',
  padding: '20px',
  backgroundColor: '#f9f9f9',
  borderRadius: '5px'
};
```

### **Understanding the Double Curly Braces {{}}**

Many beginners get confused by the double curly braces. Here's the explanation:

```jsx
<div style={{ color: 'red' }}>
  Hello World
</div>
```

**Breakdown:**
- **Outer `{}`**: JSX expression wrapper (JavaScript inside JSX)
- **Inner `{}`**: JavaScript object literal
- **Equivalent to**: `style={ { color: 'red' } }`

Think of it as: `style={ /* JavaScript object here */ }`

### **CamelCase in JSX Styles**

CSS properties with hyphens become camelCase in JSX:

```jsx
// CSS property → JSX style property
background-color → backgroundColor
font-size → fontSize
text-align → textAlign
border-radius → borderRadius
z-index → zIndex
```

```jsx
function CamelCaseExample() {
  return (
    <div style={{
      backgroundColor: 'lightblue',    // background-color
      fontSize: '18px',                // font-size
      fontWeight: 'bold',              // font-weight
      textAlign: 'center',             // text-align
      lineHeight: 1.5,                 // line-height
      borderBottomWidth: '2px',        // border-bottom-width
      borderBottomColor: '#333',       // border-bottom-color
      borderBottomStyle: 'solid'       // border-bottom-style
    }}>
      CamelCase styles example
    </div>
  );
}
```

### **Combining className and style**

```jsx
function CombinedStyling() {
  const isHighlighted = true;
  
  return (
    <div>
      {/* Base styles from CSS, overrides from inline */}
      <div 
        className="card"
        style={{
          borderColor: isHighlighted ? 'gold' : '#ccc',
          boxShadow: isHighlighted ? '0 0 10px gold' : 'none'
        }}
      >
        Combined styling
      </div>
      
      {/* Dynamic classes with conditional inline styles */}
      <button
        className={`btn ${isHighlighted ? 'btn-highlight' : ''}`}
        style={{
          transform: isHighlighted ? 'scale(1.05)' : 'scale(1)',
          transition: 'transform 0.3s ease'
        }}
      >
        Dynamic Button
      </button>
    </div>
  );
}
```

### **Common JSX Attributes in Detail**

#### **1. Event Handlers (onClick, onChange, etc.)**
```jsx
function EventAttributes() {
  const handleClick = () => {
    alert('Button clicked!');
  };
  
  const handleInputChange = (event) => {
    console.log('Input changed:', event.target.value);
  };
  
  return (
    <div>
      <button onClick={handleClick}>
        Click me
      </button>
      
      <input 
        type="text"
        onChange={handleInputChange}
        onFocus={() => console.log('Input focused')}
        onBlur={() => console.log('Input lost focus')}
      />
      
      <form onSubmit={(e) => {
        e.preventDefault();
        console.log('Form submitted');
      }}>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}
```

#### **2. Form Attributes**
```jsx
function FormAttributes() {
  return (
    <form>
      <input
        type="text"
        name="username"
        placeholder="Enter username"
        required
        autoComplete="username"
        autoFocus
      />
      
      <input
        type="password"
        name="password"
        placeholder="Enter password"
        minLength="8"
        autoComplete="current-password"
      />
      
      <input
        type="email"
        placeholder="Email address"
        pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
      />
      
      <input
        type="number"
        min="0"
        max="100"
        step="5"
        defaultValue="50"
      />
      
      <textarea
        rows="4"
        cols="50"
        maxLength="500"
        placeholder="Enter your message..."
      />
      
      <select defaultValue="option2">
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
      </select>
    </form>
  );
}
```

#### **3. Image and Media Attributes**
```jsx
function MediaAttributes() {
  return (
    <div>
      <img
        src="image.jpg"
        alt="Descriptive text for screen readers"
        width="300"
        height="200"
        loading="lazy"  // Lazy loading
        decoding="async" // Async decoding
      />
      
      <video
        width="640"
        height="360"
        controls
        poster="video-poster.jpg"
      >
        <source src="video.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
      <audio controls>
        <source src="audio.mp3" type="audio/mpeg" />
      </audio>
    </div>
  );
}
```

### **Custom Data Attributes**

```jsx
function DataAttributes() {
  const user = {
    id: 123,
    role: 'admin',
    department: 'engineering'
  };
  
  return (
    <div 
      data-user-id={user.id}
      data-user-role={user.role}
      data-testid="user-profile"  // For testing
    >
      User Profile
      
      {/* Dynamic data attributes */}
      <button
        data-action="submit"
        data-form-id="login-form"
        data-cy="submit-button"  // Cypress testing
      >
        Submit
      </button>
    </div>
  );
}
```

### **Conditional Attributes**

```jsx
function ConditionalAttributes() {
  const isDisabled = true;
  const hasError = false;
  const buttonType = "submit";
  
  return (
    <div>
      {/* Conditional attribute */}
      <button disabled={isDisabled}>
        {isDisabled ? "Disabled" : "Enabled"}
      </button>
      
      {/* Multiple conditional attributes */}
      <input
        type="text"
        className={hasError ? "input-error" : "input-normal"}
        aria-invalid={hasError}
        aria-describedby={hasError ? "error-message" : undefined}
      />
      
      {/* Conditional attribute with logical AND */}
      <button
        type={buttonType === "submit" ? "submit" : "button"}
        {...(buttonType === "submit" && { form: "my-form" })}
      >
        Conditional Button
      </button>
      
      {/* Using spread operator for conditional props */}
      <button
        type="button"
        {...(isDisabled && { disabled: true })}
        {...(hasError && { className: "error-button" })}
      >
        Spread Operator Example
      </button>
    </div>
  );
}
```

### **Accessibility Attributes (ARIA)**

```jsx
function AccessibilityExample() {
  const isExpanded = false;
  const hasPopup = true;
  
  return (
    <div>
      {/* Basic ARIA attributes */}
      <button
        aria-label="Close dialog"
        title="Close"
      >
        ×
      </button>
      
      {/* ARIA for dynamic content */}
      <div
        aria-live="polite"
        aria-atomic="true"
      >
        Content that updates dynamically
      </div>
      
      {/* ARIA for interactive controls */}
      <button
        aria-expanded={isExpanded}
        aria-controls="expandable-content"
        aria-haspopup={hasPopup}
      >
        Menu
      </button>
      
      <div
        id="expandable-content"
        aria-hidden={!isExpanded}
        role="menu"
      >
        Menu content
      </div>
      
      {/* ARIA for forms */}
      <div role="alert" aria-live="assertive">
        Important error message!
      </div>
    </div>
  );
}
```

### **Practice Exercises**

#### **Exercise 1: Create a Profile Card**
Create a profile card component with proper attributes:

```jsx
function ProfileCard() {
  const user = {
    name: "Alex Chen",
    title: "Frontend Developer",
    bio: "Passionate about React and UI/UX design",
    avatar: "https://example.com/avatar.jpg",
    website: "https://alexchen.example.com",
    isOnline: true
  };
  
  return (
    <div className="profile-card">
      {/* 
        Create a profile card with:
        1. Image with alt text, width, height
        2. Name in h2
        3. Title in p with class "title"
        4. Bio in p
        5. Website link with proper attributes
        6. Online status indicator with aria-label
      */}
    </div>
  );
}
```

**Solution:**
```jsx
function ProfileCard() {
  const user = {
    name: "Alex Chen",
    title: "Frontend Developer",
    bio: "Passionate about React and UI/UX design",
    avatar: "https://example.com/avatar.jpg",
    website: "https://alexchen.example.com",
    isOnline: true
  };
  
  return (
    <div className="profile-card" role="article">
      <div className="avatar-container">
        <img
          src={user.avatar}
          alt={`Profile picture of ${user.name}`}
          width="100"
          height="100"
          className="avatar"
          loading="lazy"
        />
        <span 
          className={`status-indicator ${user.isOnline ? 'online' : 'offline'}`}
          aria-label={user.isOnline ? "Online" : "Offline"}
          title={user.isOnline ? "Currently online" : "Currently offline"}
        />
      </div>
      
      <h2 className="user-name">{user.name}</h2>
      
      <p className="user-title" aria-label="Job title">
        {user.title}
      </p>
      
      <p className="user-bio">{user.bio}</p>
      
      <a
        href={user.website}
        className="website-link"
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Visit ${user.name}'s website`}
      >
        Visit Website
      </a>
    </div>
  );
}
```

#### **Exercise 2: Form with Validation Attributes**
Create a registration form with proper HTML5 validation:

```jsx
function RegistrationForm() {
  return (
    <form className="registration-form">
      {/* 
        Create a form with:
        1. Name field (required, minLength 2)
        2. Email field (required, type email)
        3. Password field (required, minLength 8, pattern)
        4. Age field (number, min 18, max 100)
        5. Terms checkbox (required)
        6. Submit button
      */}
    </form>
  );
}
```

### **Best Practices for JSX Attributes**

#### **1. Always Provide Alt Text for Images**
```jsx
// ❌ BAD
<img src="logo.png" />

// ✅ GOOD
<img src="logo.png" alt="Company Logo" />

// ✅ BETTER (descriptive)
<img 
  src="user-avatar.jpg" 
  alt="Profile picture of John Doe smiling" 
/>
```

#### **2. Use aria-label for Icons**
```jsx
// ❌ Screen readers can't interpret this
<button>×</button>

// ✅ Screen readers will announce "Close"
<button aria-label="Close">×</button>
```

#### **3. External Links Should Have rel Attribute**
```jsx
<a 
  href="https://external-site.com"
  target="_blank"
  rel="noopener noreferrer"
>
  External Link
</a>
```

#### **4. Use Descriptive className Names**
```jsx
// ❌ Not descriptive
<div className="b1 c2">

// ✅ Descriptive
<div className="product-card featured">

// ✅ Even better with BEM
<div className="card card--featured card--hoverable">
```

### **Common Mistakes and Solutions**

#### **Mistake 1: Forgetting camelCase**
```jsx
// ❌
<div style={{ background-color: 'red' }}>

// ✅
<div style={{ backgroundColor: 'red' }}>
```

#### **Mistake 2: Using class instead of className**
```jsx
// ❌
<div class="container">

// ✅
<div className="container">
```

#### **Mistake 3: Inline Style as String**
```jsx
// ❌ HTML way (won't work)
<div style="color: red; font-size: 16px;">

// ✅ JSX way (object)
<div style={{ color: 'red', fontSize: '16px' }}>
```

#### **Mistake 4: Missing Self-Closing Tags**
```jsx
// ❌
<input type="text">
<br>
<img src="image.jpg">

// ✅
<input type="text" />
<br />
<img src="image.jpg" />
```

### **Advanced: Conditional Spread Attributes**

```jsx
function AdvancedAttributes() {
  const buttonConfig = {
    type: 'submit',
    disabled: false,
    className: 'btn-primary',
    'data-testid': 'submit-button'
  };
  
  const extraProps = {
    onClick: () => console.log('Clicked'),
    onMouseEnter: () => console.log('Hovered')
  };
  
  return (
    <button
      {...buttonConfig}  // Spread all properties
      {...extraProps}    // Add more properties
      aria-label="Submit form"
    >
      Submit
    </button>
  );
}
```

### **Real-World Example: Product Card Component**

```jsx
function ProductCard({ product, onAddToCart }) {
  const isOnSale = product.originalPrice > product.price;
  const discountPercentage = isOnSale 
    ? Math.round((1 - product.price / product.originalPrice) * 100)
    : 0;
  
  const cardStyles = {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '16px',
    backgroundColor: '#fff',
    transition: 'box-shadow 0.3s ease',
    ':hover': {
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
    }
  };
  
  return (
    <article 
      className="product-card"
      style={cardStyles}
      role="article"
      aria-labelledby={`product-title-${product.id}`}
    >
      {/* Sale Badge */}
      {isOnSale && (
        <span 
          className="sale-badge"
          style={{
            backgroundColor: '#ff4444',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
          aria-label={`${discountPercentage}% off`}
        >
          {discountPercentage}% OFF
        </span>
      )}
      
      {/* Product Image */}
      <img
        src={product.imageUrl}
        alt={`${product.name} - ${product.category}`}
        width="200"
        height="200"
        className="product-image"
        loading="lazy"
      />
      
      {/* Product Info */}
      <div className="product-info">
        <h3 
          id={`product-title-${product.id}`}
          className="product-title"
        >
          {product.name}
        </h3>
        
        <div className="product-rating" aria-label={`Rating: ${product.rating} out of 5 stars`}>
          {'⭐'.repeat(Math.floor(product.rating))}
          <span style={{ fontSize: '14px', marginLeft: '8px' }}>
            ({product.reviewCount} reviews)
          </span>
        </div>
        
        <div className="product-price">
          {isOnSale ? (
            <>
              <span 
                className="current-price"
                style={{ color: '#ff4444', fontSize: '20px', fontWeight: 'bold' }}
              >
                ${product.price.toFixed(2)}
              </span>
              <span 
                className="original-price"
                style={{ textDecoration: 'line-through', marginLeft: '8px', color: '#999' }}
              >
                ${product.originalPrice.toFixed(2)}
              </span>
            </>
          ) : (
            <span className="price" style={{ fontSize: '20px', fontWeight: 'bold' }}>
              ${product.price.toFixed(2)}
            </span>
          )}
        </div>
        
        <p className="product-description">
          {product.description}
        </p>
        
        {/* Action Buttons */}
        <div className="product-actions">
          <button
            className="add-to-cart-btn"
            onClick={() => onAddToCart(product)}
            aria-label={`Add ${product.name} to cart`}
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Add to Cart
          </button>
          
          <button
            className="wishlist-btn"
            aria-label={`Add ${product.name} to wishlist`}
            style={{
              backgroundColor: 'transparent',
              border: '1px solid #ccc',
              padding: '10px 20px',
              borderRadius: '4px',
              marginLeft: '8px',
              cursor: 'pointer'
            }}
          >
            ♡ Wishlist
          </button>
        </div>
      </div>
    </article>
  );
}
```

### **Quick Reference Card**

#### **Common JSX Attributes:**
```jsx
// Basic
className="my-class"
style={{ color: 'red' }}
id="unique-id"

// Events
onClick={handleClick}
onChange={handleChange}
onSubmit={handleSubmit}

// Forms
value={stateValue}
defaultValue="initial"
checked={isChecked}
disabled={isDisabled}
readOnly={isReadOnly}

// Accessibility
aria-label="Description"
aria-hidden={true}
role="button"
tabIndex={0}

// Links & Images
href="https://..."
target="_blank"
rel="noopener noreferrer"
src="image.jpg"
alt="Description"
```

#### **Style Conversion:**
```css
/* CSS Property → JSX Style Property */
font-size: 16px; → fontSize: '16px'
background-color: #fff; → backgroundColor: '#fff'
text-align: center; → textAlign: 'center'
border-radius: 5px; → borderRadius: '5px'
z-index: 10; → zIndex: 10
```

### **Practice Challenge**

**Challenge: Create a Notification Component**
```jsx
function Notification({ type, message, duration, onClose }) {
  // type can be: 'success', 'error', 'warning', 'info'
  // Create dynamic styles based on type
  // Add proper ARIA attributes
  // Include a close button
  
  return (
    <div className="notification">
      {/* Your implementation */}
    </div>
  );
}
```

**Requirements:**
- Different background colors for each type
- Icon based on type (✓ for success, ⚠ for warning, etc.)
- Accessible with ARIA roles
- Close button with aria-label
- Auto-hide after duration (if provided)

### **Summary**

**Key Takeaways:**
1. **`className`** not `class`
2. **`style`** takes a JavaScript object with camelCase properties
3. **Event handlers** use camelCase (`onClick`, not `onclick`)
4. **All tags must be closed** (`<img />`, `<br />`)
5. **Boolean attributes** don't need values (`disabled`, `checked`)
6. **Use `aria-*`** for accessibility
7. **External links need `rel="noopener noreferrer"`**

**Remember:** JSX is JavaScript, not HTML. The rules are different but logical once you understand the patterns.

---

**Ready for Topic 9: "Inline Styling for React Elements"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Inline Styling for React Elements|Inline Styling for React Elements]]
- [[Web Development/React/JSX/JSX Guide|JSX Guide]]
- [[Web Development/React/React Topics/Introduction to JSX and Babel|Introduction to JSX and Babel]]
