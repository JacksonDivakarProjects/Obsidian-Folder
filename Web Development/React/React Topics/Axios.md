## **44. Axios - Complete Beginner's Guide**

### **Introduction to Axios**
Axios is a **popular JavaScript library** used to make HTTP requests from the browser or Node.js. It's essentially a better, more feature-rich alternative to the built-in `fetch()` API. Think of it as a "supercharged fetch" that handles a lot of common HTTP request tasks automatically.

### **Why Use Axios Over Fetch?**
While the native `fetch()` API is good, Axios provides several advantages:

| Feature | `fetch()` | Axios |
|---------|-----------|-------|
| **Browser Support** | Modern browsers | Works everywhere (even IE11) |
| **Request/Response Transformation** | Manual | Automatic JSON handling |
| **Timeout Support** | Not built-in | Built-in timeout |
| **Request Cancellation** | AbortController | Built-in cancellation |
| **Error Handling** | Manual checking | Automatic - rejects on non-2xx |
| **Progress Tracking** | Basic | Built-in upload/download progress |
| **Interceptors** | No | Yes (modify requests/responses) |
| **Defaults** | Manual | Easy to set defaults |

### **Installation & Setup**

#### **In a React Project (using Create React App)**
```bash
# Install via npm
npm install axios

# OR install via yarn
yarn add axios
```

#### **In a Browser (without npm)**
```html
<!-- Include via CDN -->
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

### **Basic Usage**

#### **Importing Axios**
```javascript
// In React/Node.js project
import axios from 'axios';

// OR using require (Node.js/older projects)
const axios = require('axios');
```

### **Making HTTP Requests**

Axios supports all common HTTP methods:

#### **1. GET Request - Fetch Data**
```javascript
// Basic GET request
axios.get('https://jsonplaceholder.typicode.com/posts')
  .then(response => {
    console.log(response.data); // The actual data
    console.log(response.status); // HTTP status code
    console.log(response.headers); // Response headers
  })
  .catch(error => {
    console.error('Error:', error);
  });

// With async/await
async function getPosts() {
  try {
    const response = await axios.get('https://jsonplaceholder.typicode.com/posts');
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

#### **2. POST Request - Send Data**
```javascript
// Sending JSON data
axios.post('https://jsonplaceholder.typicode.com/posts', {
  title: 'My New Post',
  body: 'This is the content',
  userId: 1
})
  .then(response => {
    console.log('Created post:', response.data);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// With FormData (for file uploads)
const formData = new FormData();
formData.append('username', 'john');
formData.append('avatar', fileInput.files[0]);

axios.post('/api/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
```

#### **3. PUT/PATCH Request - Update Data**
```javascript
// PUT - Replace entire resource
axios.put('https://jsonplaceholder.typicode.com/posts/1', {
  id: 1,
  title: 'Updated Title',
  body: 'Updated content',
  userId: 1
});

// PATCH - Update partial resource
axios.patch('https://jsonplaceholder.typicode.com/posts/1', {
  title: 'Only updating the title'
});
```

#### **4. DELETE Request - Remove Data**
```javascript
axios.delete('https://jsonplaceholder.typicode.com/posts/1')
  .then(response => {
    console.log('Deleted successfully');
  });
```

### **Axios Response Structure**
When you make a request, Axios returns a response object with this structure:

```javascript
{
  // The data from the server
  data: {},
  
  // HTTP status code
  status: 200,
  
  // Status message
  statusText: 'OK',
  
  // Response headers
  headers: {},
  
  // Request configuration
  config: {},
  
  // The original request
  request: {}
}
```

### **Request Configuration**

Axios allows you to configure requests in detail:

```javascript
// All config options in one request
axios({
  method: 'post',           // HTTP method
  url: '/api/user',         // API endpoint
  baseURL: 'https://api.example.com', // Base URL
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token-here'
  },
  params: {                 // URL parameters
    id: 12345
  },
  data: {                   // Request body
    firstName: 'John',
    lastName: 'Doe'
  },
  timeout: 5000,            // Timeout in milliseconds
  responseType: 'json',     // Response type (json, blob, arraybuffer, etc.)
  withCredentials: true     // Send cookies with cross-origin requests
});
```

### **Error Handling**

Axios makes error handling consistent:

```javascript
axios.get('/api/data')
  .then(response => {
    // Success - automatically called for 2xx status codes
  })
  .catch(error => {
    // Handle different types of errors
    
    if (error.response) {
      // Server responded with error status (4xx, 5xx)
      console.log('Server Error:', error.response.status);
      console.log('Error Data:', error.response.data);
      console.log('Error Headers:', error.response.headers);
    } else if (error.request) {
      // Request was made but no response received
      console.log('Network Error:', error.request);
    } else {
      // Something else happened
      console.log('Error:', error.message);
    }
    
    // The error config
    console.log('Error Config:', error.config);
  });
```

### **Advanced Features**

#### **1. Global Defaults**
Set defaults that apply to all requests:

```javascript
// Set base URL for all requests
axios.defaults.baseURL = 'https://api.example.com';

// Set default headers
axios.defaults.headers.common['Authorization'] = 'Bearer token';
axios.defaults.headers.post['Content-Type'] = 'application/json';

// Set default timeout
axios.defaults.timeout = 10000;

// Now all requests will use these defaults
axios.get('/users') // Actually calls https://api.example.com/users
  .then(response => {
    // Request automatically includes Authorization header
  });
```

#### **2. Creating Axios Instances**
Create separate instances with different configurations:

```javascript
// Create an instance for API calls
const apiClient = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Create another instance for file uploads
const uploadClient = axios.create({
  baseURL: 'https://uploads.example.com',
  timeout: 30000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

// Use them separately
apiClient.get('/users');
uploadClient.post('/files', formData);
```

#### **3. Interceptors - Powerful Middleware**
Interceptors let you modify requests or responses:

```javascript
// Request interceptor - runs before request is sent
axios.interceptors.request.use(
  config => {
    // Add auth token to every request
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add timestamp
    config.headers['X-Request-Timestamp'] = Date.now();
    
    return config;
  },
  error => {
    // Handle request error
    return Promise.reject(error);
  }
);

// Response interceptor - runs after response is received
axios.interceptors.response.use(
  response => {
    // Modify response data
    console.log('Response received:', response.status);
    return response;
  },
  error => {
    // Handle response errors globally
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### **4. Request Cancellation**
Cancel requests that are no longer needed:

```javascript
// Create cancel token
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

// Make request with cancel token
axios.get('/api/data', {
  cancelToken: source.token
})
  .then(response => {
    console.log(response.data);
  })
  .catch(thrown => {
    if (axios.isCancel(thrown)) {
      console.log('Request canceled:', thrown.message);
    } else {
      // Handle other errors
    }
  });

// Cancel the request
source.cancel('Operation canceled by user');
```

#### **5. Concurrent Requests**
Make multiple requests simultaneously:

```javascript
// Using Promise.all with Axios
async function getUserData(userId) {
  try {
    const [userResponse, postsResponse, commentsResponse] = await Promise.all([
      axios.get(`/api/users/${userId}`),
      axios.get(`/api/users/${userId}/posts`),
      axios.get(`/api/users/${userId}/comments`)
    ]);
    
    return {
      user: userResponse.data,
      posts: postsResponse.data,
      comments: commentsResponse.data
    };
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}

// Using axios.all (deprecated but still works)
axios.all([
  axios.get('/api/users'),
  axios.get('/api/posts')
])
  .then(axios.spread((usersResponse, postsResponse) => {
    console.log('Users:', usersResponse.data);
    console.log('Posts:', postsResponse.data);
  }));
```

### **Axios in React - Practical Examples**

#### **Example 1: API Service Module**
```javascript
// api.js - Centralized API service
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://jsonplaceholder.typicode.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// User API methods
export const userAPI = {
  getAll: () => apiClient.get('/users'),
  getById: (id) => apiClient.get(`/users/${id}`),
  create: (userData) => apiClient.post('/users', userData),
  update: (id, userData) => apiClient.put(`/users/${id}`, userData),
  delete: (id) => apiClient.delete(`/users/${id}`)
};

// Post API methods
export const postAPI = {
  getAll: () => apiClient.get('/posts'),
  getByUser: (userId) => apiClient.get(`/posts?userId=${userId}`),
  create: (postData) => apiClient.post('/posts', postData)
};
```

#### **Example 2: React Component with Axios**
```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Create cancel token for cleanup
    const source = axios.CancelToken.source();

    async function fetchUsers() {
      try {
        setLoading(true);
        const response = await axios.get(
          'https://jsonplaceholder.typicode.com/users',
          { cancelToken: source.token }
        );
        setUsers(response.data);
        setError(null);
      } catch (err) {
        if (axios.isCancel(err)) {
          console.log('Request canceled:', err.message);
        } else {
          setError(err.message);
          console.error('Error fetching users:', err);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchUsers();

    // Cleanup function - cancel request if component unmounts
    return () => {
      source.cancel('Component unmounted');
    };
  }, []); // Empty dependency array = run once

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map(user => (
          <li key={user.id}>
            {user.name} ({user.email})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default UserList;
```

#### **Example 3: Form Submission with Axios**
```javascript
import React, { useState } from 'react';
import axios from 'axios';

function AddPostForm() {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim() || !body.trim()) {
      setMessage('Please fill in all fields');
      return;
    }

    setSubmitting(true);
    setMessage('');

    try {
      const response = await axios.post(
        'https://jsonplaceholder.typicode.com/posts',
        {
          title,
          body,
          userId: 1
        }
      );

      setMessage(`Post created successfully! ID: ${response.data.id}`);
      setTitle('');
      setBody('');
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.message || error.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Title:</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={submitting}
        />
      </div>
      <div>
        <label>Content:</label>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={submitting}
        />
      </div>
      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating...' : 'Create Post'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

### **Common Patterns & Best Practices**

#### **1. Centralized Error Handling**
```javascript
// errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Server error
    switch (error.response.status) {
      case 401:
        // Unauthorized - redirect to login
        window.location.href = '/login';
        break;
      case 403:
        // Forbidden
        return 'You do not have permission to perform this action';
      case 404:
        // Not found
        return 'Resource not found';
      case 500:
        // Server error
        return 'Server error. Please try again later';
      default:
        return error.response.data?.message || 'An error occurred';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection';
  } else {
    // Other errors
    return error.message || 'An unexpected error occurred';
  }
};
```

#### **2. Request Retry Logic**
```javascript
// With interceptor
axios.interceptors.response.use(null, async (error) => {
  const config = error.config;
  
  // If we haven't retried yet and it's a network error
  if (!config.__isRetry && error.message.includes('Network Error')) {
    config.__isRetry = true;
    
    // Wait 1 second then retry
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return axios(config);
  }
  
  return Promise.reject(error);
});
```

### **Comparison: Axios vs Fetch**

```javascript
// Using Fetch
fetch('https://api.example.com/data')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Using Axios (cleaner!)
axios.get('https://api.example.com/data')
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error));
```

### **Exercise: Convert Fetch to Axios**

Convert this fetch code to use Axios:
```javascript
// Using fetch
fetch('https://jsonplaceholder.typicode.com/posts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'New Post',
    body: 'This is my post content',
    userId: 1
  })
})
  .then(response => {
    if (!response.ok) throw new Error('Failed to create post');
    return response.json();
  })
  .then(data => console.log('Created:', data))
  .catch(error => console.error('Error:', error));
```

**Solution:**
```javascript
// Using Axios
axios.post('https://jsonplaceholder.typicode.com/posts', {
  title: 'New Post',
  body: 'This is my post content',
  userId: 1
})
  .then(response => {
    console.log('Created:', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

### **Summary**
- **Axios** is a powerful HTTP client for JavaScript
- **Automatic JSON transformation** - no need for `.json()` calls
- **Better error handling** - rejects on non-2xx status codes
- **Request/Response interceptors** for middleware functionality
- **Request cancellation** for cleanup
- **Wide browser support** including IE11
- **Cleaner syntax** compared to fetch

Axios is widely used in production React applications because it simplifies API interactions and provides robust features out of the box.

---

**That completes all 44 topics! You now have a comprehensive React learning guide from absolute basics to advanced concepts like Axios. Is there any specific topic you'd like me to elaborate on or any other questions you have?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Async-Await|Async/Await]]
- [[Web Development/React/React Topics/Promises|Promises]]
- [[Web Development/React/React Topics/React Hooks|React Hooks - useState]]
