## **React Forms - Practical Guide**

### **The Simple Approach to Forms in React**

Forms in React are simple when you understand the basic pattern. Let's break it down to the essentials.

### **1. Basic Form Pattern**

```jsx
import { useState } from 'react';

function SimpleForm() {
  // 1. Create state for form data
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });

  // 2. Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,      // Keep existing data
      [name]: value     // Update only the changed field
    });
  };

  // 3. Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page reload
    console.log('Form submitted:', formData);
    // Send data to server here
  };

  return (
    // 4. Create the form
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Your Name"
      />
      
      <input
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Your Email"
      />
      
      <input
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        placeholder="Password"
      />
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

### **2. Different Input Types**

Here's how to handle common input types:

```jsx
function AllInputTypes() {
  const [form, setForm] = useState({
    text: '',
    email: '',
    password: '',
    textarea: '',
    checkbox: false,
    radio: 'option1',
    select: 'apple',
    date: '',
    number: 0
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Handle checkboxes differently
    if (type === 'checkbox') {
      setForm({
        ...form,
        [name]: checked
      });
    } else {
      setForm({
        ...form,
        [name]: value
      });
    }
  };

  return (
    <form>
      {/* Text Input */}
      <input
        type="text"
        name="text"
        value={form.text}
        onChange={handleChange}
        placeholder="Text input"
      />

      {/* Email Input */}
      <input
        type="email"
        name="email"
        value={form.email}
        onChange={handleChange}
        placeholder="Email"
      />

      {/* Password Input */}
      <input
        type="password"
        name="password"
        value={form.password}
        onChange={handleChange}
        placeholder="Password"
      />

      {/* Textarea */}
      <textarea
        name="textarea"
        value={form.textarea}
        onChange={handleChange}
        placeholder="Your message"
        rows="4"
      />

      {/* Checkbox */}
      <label>
        <input
          type="checkbox"
          name="checkbox"
          checked={form.checkbox}
          onChange={handleChange}
        />
        Accept terms
      </label>

      {/* Radio Buttons */}
      <div>
        <label>
          <input
            type="radio"
            name="radio"
            value="option1"
            checked={form.radio === 'option1'}
            onChange={handleChange}
          />
          Option 1
        </label>
        <label>
          <input
            type="radio"
            name="radio"
            value="option2"
            checked={form.radio === 'option2'}
            onChange={handleChange}
          />
          Option 2
        </label>
      </div>

      {/* Select Dropdown */}
      <select name="select" value={form.select} onChange={handleChange}>
        <option value="apple">Apple</option>
        <option value="banana">Banana</option>
        <option value="orange">Orange</option>
      </select>

      {/* Date Input */}
      <input
        type="date"
        name="date"
        value={form.date}
        onChange={handleChange}
      />

      {/* Number Input */}
      <input
        type="number"
        name="number"
        value={form.number}
        onChange={handleChange}
        min="0"
        max="100"
      />
    </form>
  );
}
```

### **3. Form with Validation (Simplified)**

```jsx
function FormWithValidation() {
  const [form, setForm] = useState({
    email: '',
    password: ''
  });
  
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value
    });
    
    // Clear error when user types
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!form.email) {
      newErrors.email = 'Email is required';
    } else if (!form.email.includes('@')) {
      newErrors.email = 'Email must contain @';
    }
    
    if (!form.password) {
      newErrors.password = 'Password is required';
    } else if (form.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const formErrors = validateForm();
    
    if (Object.keys(formErrors).length === 0) {
      // No errors, submit the form
      console.log('Form submitted:', form);
    } else {
      // Show errors
      setErrors(formErrors);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          placeholder="Email"
        />
        {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
      </div>
      
      <div>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Password"
        />
        {errors.password && <p style={{ color: 'red' }}>{errors.password}</p>}
      </div>
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

### **4. Login Form Example**

```jsx
function LoginForm() {
  const [form, setForm] = useState({
    username: '',
    password: ''
  });
  
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Login successful:', form);
      alert('Login successful!');
      
      // Clear form after successful login
      setForm({ username: '', password: '' });
      
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '300px', margin: '0 auto' }}>
      <h2>Login</h2>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>
          Username:
        </label>
        <input
          type="text"
          name="username"
          value={form.username}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>
          Password:
        </label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <button 
        type="submit" 
        disabled={loading}
        style={{
          width: '100%',
          padding: '10px',
          background: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px'
        }}
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### **5. Registration Form Example**

```jsx
function RegistrationForm() {
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setForm({
      ...form,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic validation
    if (form.password !== form.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }
    
    if (!form.agreeToTerms) {
      alert('You must agree to the terms');
      return;
    }
    
    console.log('Registration data:', form);
    alert('Registration successful!');
    
    // Clear form
    setForm({
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2>Register</h2>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
        <div style={{ flex: 1 }}>
          <input
            type="text"
            name="firstName"
            value={form.firstName}
            onChange={handleChange}
            placeholder="First Name"
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        
        <div style={{ flex: 1 }}>
          <input
            type="text"
            name="lastName"
            value={form.lastName}
            onChange={handleChange}
            placeholder="Last Name"
            required
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          placeholder="Email"
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Password"
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="password"
          name="confirmPassword"
          value={form.confirmPassword}
          onChange={handleChange}
          placeholder="Confirm Password"
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <label style={{ display: 'block', marginBottom: '15px' }}>
        <input
          type="checkbox"
          name="agreeToTerms"
          checked={form.agreeToTerms}
          onChange={handleChange}
          required
        />
        I agree to the terms and conditions
      </label>
      
      <button 
        type="submit"
        style={{
          width: '100%',
          padding: '10px',
          background: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '4px'
        }}
      >
        Register
      </button>
    </form>
  );
}
```

### **6. Contact Form Example**

```jsx
function ContactForm() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Simulate sending email
    console.log('Contact form submitted:', form);
    
    // Show success message
    setSubmitted(true);
    
    // Clear form
    setForm({
      name: '',
      email: '',
      subject: '',
      message: ''
    });
    
    // Hide success message after 3 seconds
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto' }}>
      <h2>Contact Us</h2>
      
      {submitted && (
        <div style={{
          background: '#d4edda',
          color: '#155724',
          padding: '10px',
          marginBottom: '20px',
          borderRadius: '4px'
        }}>
          Message sent successfully! We'll get back to you soon.
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Your Name"
            required
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="Your Email"
            required
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            name="subject"
            value={form.subject}
            onChange={handleChange}
            placeholder="Subject"
            required
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        
        <div style={{ marginBottom: '15px' }}>
          <textarea
            name="message"
            value={form.message}
            onChange={handleChange}
            placeholder="Your Message"
            required
            rows="5"
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        
        <button 
          type="submit"
          style={{
            padding: '10px 30px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Send Message
        </button>
      </form>
    </div>
  );
}
```

### **7. Quick Tips for Better Forms**

#### **Tip 1: Better HandleChange Function**
```jsx
// Works for ALL input types
const handleChange = (e) => {
  const { name, value, type, checked } = e.target;
  
  setForm(prev => ({
    ...prev,
    [name]: type === 'checkbox' ? checked : value
  }));
};
```

#### **Tip 2: Reset Form After Submit**
```jsx
const handleSubmit = (e) => {
  e.preventDefault();
  
  // Submit form...
  
  // Clear form
  setForm({
    name: '',
    email: '',
    // ...reset all fields
  });
};
```

#### **Tip 3: Disable Submit Button When Invalid**
```jsx
// Check if form is valid
const isFormValid = form.name && form.email && form.password;

<button 
  type="submit" 
  disabled={!isFormValid}
  style={{ 
    opacity: isFormValid ? 1 : 0.5,
    cursor: isFormValid ? 'pointer' : 'not-allowed'
  }}
>
  Submit
</button>
```

### **The Core Pattern (Remember This!)**

```jsx
// 1. State for form data
const [form, setForm] = useState(initialValues);

// 2. Handle all input changes
const handleChange = (e) => {
  const { name, value, type, checked } = e.target;
  setForm(prev => ({
    ...prev,
    [name]: type === 'checkbox' ? checked : value
  }));
};

// 3. Handle form submission
const handleSubmit = (e) => {
  e.preventDefault();
  // Use form data here
  console.log(form);
};

// 4. In your JSX
<form onSubmit={handleSubmit}>
  <input
    name="fieldName"
    value={form.fieldName}
    onChange={handleChange}
  />
  <button type="submit">Submit</button>
</form>
```

### **Common Questions Answered**

**Q: Why use `e.preventDefault()`?**
A: It stops the page from reloading when form is submitted.

**Q: Why spread `...form` in setForm?**
A: It creates a new object instead of modifying the old one (React needs this).

**Q: What's `[name]: value`?**
A: It uses the input's name as the key dynamically.

**Q: When to use controlled vs uncontrolled?**
A: Always use controlled (with state) for React forms. It gives you full control.

### **Summary**

1. **Create state** for your form data
2. **Make inputs controlled** with `value={form.field}`
3. **Use one `handleChange`** for all inputs
4. **Handle checkboxes/radios** with `type` and `checked`
5. **Prevent default** on form submit
6. **Validate** before submitting
7. **Clear form** after successful submission

That's it! This pattern works for 95% of forms you'll build.

## 🔗 Related Notes
- [[Web Development/React/React Topics/Event Handling in React|Event Handling in React]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
- [[Web Development/React/React Topics/JavaScript ES6 Object & Array Destructuring|JavaScript ES6 Object & Array Destructuring]]
