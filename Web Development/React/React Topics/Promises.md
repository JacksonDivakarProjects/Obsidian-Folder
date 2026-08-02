## **42. Promises - Complete Beginner's Guide**

### **Introduction**
Welcome to **Promises** - the solution to JavaScript's callback hell! Promises make handling asynchronous operations (like API calls, file reading, timers) much cleaner and easier to understand. If you've ever struggled with nested callbacks, Promises are here to save you!

### **What Problem Do Promises Solve?**

#### **Callback Hell (The Problem):**
```javascript
// Nested callbacks - hard to read and maintain
getUser(userId, function(user) {
  getPosts(user.id, function(posts) {
    getComments(posts[0].id, function(comments) {
      getReplies(comments[0].id, function(replies) {
        // 4 levels deep! 😱
        console.log(replies);
      });
    });
  });
});
```

#### **Promises (The Solution):**
```javascript
// Clean, flat chain - much better!
getUser(userId)
  .then(user => getPosts(user.id))
  .then(posts => getComments(posts[0].id))
  .then(comments => getReplies(comments[0].id))
  .then(replies => console.log(replies))
  .catch(error => console.error(error));
```

### **What is a Promise?**

A **Promise** is an object representing the eventual completion (or failure) of an asynchronous operation and its resulting value.

**Think of it like:** Ordering food at a restaurant:
1. You place an order (start async operation)
2. You get a receipt (Promise)
3. The receipt is a **promise** that you'll eventually get:
   - Your food (success)
   - Or a refund/explanation (failure)

### **The Three States of a Promise**

A Promise can be in one of three states:
1. **Pending**: Operation hasn't completed yet
2. **Fulfilled**: Operation completed successfully
3. **Rejected**: Operation failed

```
         Promise
           │
           ▼
       [Pending]
         ╱  ╲
        ╱    ╲
       ╱      ╲
   Fulfilled  Rejected
   (Success)  (Failure)
```

### **Creating a Promise**

#### **Basic Syntax:**
```javascript
const myPromise = new Promise((resolve, reject) => {
  // Async operation goes here
  
  // If successful:
  resolve('Success value');
  
  // If failed:
  reject('Error message');
});
```

#### **Simple Examples:**
```javascript
// Example 1: Simple resolved promise
const successPromise = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve('Operation completed successfully!');
  }, 1000);
});

// Example 2: Simple rejected promise
const failPromise = new Promise((resolve, reject) => {
  setTimeout(() => {
    reject('Something went wrong!');
  }, 1000);
});

// Example 3: Promise that randomly resolves or rejects
const randomPromise = new Promise((resolve, reject) => {
  setTimeout(() => {
    const random = Math.random();
    if (random > 0.5) {
      resolve(`Success! Random was ${random}`);
    } else {
      reject(`Failed! Random was ${random}`);
    }
  }, 1000);
});
```

### **Using Promises: `.then()` and `.catch()`**

#### **Basic Usage:**
```javascript
const promise = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve('Data loaded!');
  }, 1000);
});

// Handle success
promise.then(result => {
  console.log(result); // "Data loaded!"
});

// Handle error
promise.catch(error => {
  console.error(error);
});

// Or chain them
promise
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

#### **Practical Example: Simulating API Call**
```javascript
function fetchUserData(userId) {
  return new Promise((resolve, reject) => {
    console.log(`Fetching user ${userId}...`);
    
    setTimeout(() => {
      const users = {
        1: { id: 1, name: 'Alice', email: 'alice@example.com' },
        2: { id: 2, name: 'Bob', email: 'bob@example.com' }
      };
      
      const user = users[userId];
      
      if (user) {
        resolve(user); // Success
      } else {
        reject('User not found'); // Failure
      }
    }, 1500); // Simulate network delay
  });
}

// Using the promise
fetchUserData(1)
  .then(user => {
    console.log('User found:', user);
    return user.email; // Pass to next .then()
  })
  .then(email => {
    console.log('User email:', email);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Try with invalid ID
fetchUserData(99)
  .then(user => console.log(user))
  .catch(error => console.error('Error:', error));
```

### **Promise Chaining (The Real Power!)**

You can chain multiple async operations:

```javascript
// Simulated API functions
function login(email, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (email && password) {
        resolve({ token: 'abc123', userId: 1 });
      } else {
        reject('Invalid credentials');
      }
    }, 1000);
  });
}

function getUserProfile(token, userId) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (token === 'abc123') {
        resolve({ 
          id: userId, 
          name: 'Alice', 
          email: 'alice@example.com' 
        });
      } else {
        reject('Invalid token');
      }
    }, 1000);
  });
}

function getUserPosts(userId) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve([
        { id: 101, title: 'Post 1' },
        { id: 102, title: 'Post 2' }
      ]);
    }, 1000);
  });
}

// Chain them together
login('alice@example.com', 'password123')
  .then(authData => {
    console.log('Login successful:', authData);
    return getUserProfile(authData.token, authData.userId);
  })
  .then(profile => {
    console.log('Profile loaded:', profile);
    return getUserPosts(profile.id);
  })
  .then(posts => {
    console.log('User posts:', posts);
  })
  .catch(error => {
    console.error('Error in chain:', error);
  });
```

### **Promise Methods**

#### **1. `Promise.all()` - Wait for ALL promises**
```javascript
// Run multiple promises in parallel
const promise1 = Promise.resolve('First');
const promise2 = new Promise(resolve => {
  setTimeout(() => resolve('Second'), 2000);
});
const promise3 = fetch('https://api.example.com/data');

Promise.all([promise1, promise2, promise3])
  .then(results => {
    console.log('All promises completed:', results);
    // results = ['First', 'Second', apiResponse]
  })
  .catch(error => {
    console.error('One promise failed:', error);
  });

// Real example: Load multiple user data in parallel
const userIds = [1, 2, 3];
const userPromises = userIds.map(id => fetchUserData(id));

Promise.all(userPromises)
  .then(users => {
    console.log('All users loaded:', users);
  })
  .catch(error => {
    console.error('Failed to load some users:', error);
  });
```

#### **2. `Promise.race()` - First to finish wins**
```javascript
// Get result of first promise to complete
const timeoutPromise = new Promise((_, reject) => {
  setTimeout(() => reject('Request timeout'), 3000);
});

const apiPromise = fetch('https://api.example.com/data');

Promise.race([apiPromise, timeoutPromise])
  .then(result => {
    console.log('Got response before timeout:', result);
  })
  .catch(error => {
    console.error('Error or timeout:', error);
  });
```

#### **3. `Promise.allSettled()` - Wait for ALL, even failures**
```javascript
// Wait for all promises to complete (success or failure)
const promises = [
  Promise.resolve('Success 1'),
  Promise.reject('Error 1'),
  Promise.resolve('Success 2'),
  Promise.reject('Error 2')
];

Promise.allSettled(promises)
  .then(results => {
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        console.log(`Promise ${index}:`, result.value);
      } else {
        console.log(`Promise ${index} failed:`, result.reason);
      }
    });
  });
```

#### **4. `Promise.any()` - First to succeed**
```javascript
// Get first SUCCESSFUL promise
const api1 = fetch('https://api1.example.com').catch(() => 'API 1 failed');
const api2 = fetch('https://api2.example.com').catch(() => 'API 2 failed');
const api3 = fetch('https://api3.example.com').catch(() => 'API 3 failed');

Promise.any([api1, api2, api3])
  .then(firstSuccessful => {
    console.log('First successful API:', firstSuccessful);
  })
  .catch(errors => {
    console.error('All APIs failed:', errors);
  });
```

### **Error Handling in Promises**

#### **Multiple Ways to Catch Errors:**
```javascript
// Method 1: .catch() at the end
somePromise()
  .then(result => { /* ... */ })
  .catch(error => console.error(error));

// Method 2: .catch() after each .then()
somePromise()
  .then(result => { /* ... */ })
  .catch(error => console.error('Step 1 failed:', error))
  .then(result => { /* ... */ })
  .catch(error => console.error('Step 2 failed:', error));

// Method 3: Try/catch in async functions (we'll cover next)
async function handlePromise() {
  try {
    const result = await somePromise();
  } catch (error) {
    console.error(error);
  }
}
```

#### **Throwing Errors in Chains:**
```javascript
fetchUserData(1)
  .then(user => {
    if (!user.isActive) {
      throw new Error('User is inactive'); // Will be caught by .catch()
    }
    return user;
  })
  .then(user => {
    console.log('Active user:', user);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

### **Converting Callbacks to Promises**

#### **Before (Callback Style):**
```javascript
function readFileCallback(filename, callback) {
  // Simulate file reading
  setTimeout(() => {
    const fileContent = `Content of ${filename}`;
    callback(null, fileContent); // Node.js style: error first
  }, 1000);
}

// Usage (callback hell)
readFileCallback('file1.txt', (err, content1) => {
  if (err) return console.error(err);
  readFileCallback('file2.txt', (err, content2) => {
    if (err) return console.error(err);
    console.log(content1, content2);
  });
});
```

#### **After (Promise Style):**
```javascript
function readFilePromise(filename) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const fileContent = `Content of ${filename}`;
      resolve(fileContent);
      // Or: reject(new Error('File not found'));
    }, 1000);
  });
}

// Usage (clean chain)
readFilePromise('file1.txt')
  .then(content1 => {
    console.log(content1);
    return readFilePromise('file2.txt');
  })
  .then(content2 => {
    console.log(content2);
  })
  .catch(error => {
    console.error(error);
  });
```

### **Real-World Examples**

#### **Example 1: Fetching Data with Timeout**
```javascript
function fetchWithTimeout(url, timeout = 5000) {
  const controller = new AbortController();
  const signal = controller.signal;
  
  const fetchPromise = fetch(url, { signal });
  
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => {
      controller.abort();
      reject(new Error(`Request timeout after ${timeout}ms`));
    }, timeout);
  });
  
  return Promise.race([fetchPromise, timeoutPromise]);
}

// Usage
fetchWithTimeout('https://api.example.com/data', 3000)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => {
    if (error.name === 'AbortError') {
      console.error('Request was aborted due to timeout');
    } else {
      console.error('Other error:', error);
    }
  });
```

#### **Example 2: Sequential File Processing**
```javascript
function processFiles(fileNames) {
  let results = [];
  
  // Process files one by one (sequential)
  return fileNames.reduce((promiseChain, fileName) => {
    return promiseChain.then(() => {
      return readFilePromise(fileName)
        .then(content => {
          console.log(`Processed ${fileName}`);
          results.push(content);
        });
    });
  }, Promise.resolve())
  .then(() => results);
}

// Usage
processFiles(['file1.txt', 'file2.txt', 'file3.txt'])
  .then(allContents => {
    console.log('All files processed:', allContents);
  })
  .catch(error => {
    console.error('Failed to process files:', error);
  });
```

#### **Example 3: User Registration Flow**
```javascript
function checkEmailAvailability(email) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const takenEmails = ['test@example.com', 'admin@example.com'];
      if (takenEmails.includes(email)) {
        reject('Email already taken');
      } else {
        resolve(true);
      }
    }, 500);
  });
}

function validatePassword(password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (password.length < 8) {
        reject('Password must be at least 8 characters');
      } else {
        resolve(true);
      }
    }, 300);
  });
}

function createUser(userData) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate database save
      const user = { ...userData, id: Date.now() };
      resolve(user);
    }, 1000);
  });
}

function registerUser(userData) {
  return checkEmailAvailability(userData.email)
    .then(() => validatePassword(userData.password))
    .then(() => createUser(userData))
    .then(user => {
      console.log('User registered:', user);
      return user;
    });
}

// Usage
registerUser({
  name: 'Alice',
  email: 'alice@example.com',
  password: 'secure123'
})
.then(user => {
  console.log('Registration successful!');
})
.catch(error => {
  console.error('Registration failed:', error);
});
```

### **Promise Patterns and Best Practices**

#### **Pattern 1: Promise Caching**
```javascript
const promiseCache = {};

function fetchDataWithCache(url) {
  // Return cached promise if available
  if (promiseCache[url]) {
    console.log('Returning cached promise for', url);
    return promiseCache[url];
  }
  
  // Create new promise and cache it
  console.log('Creating new promise for', url);
  const promise = fetch(url)
    .then(response => response.json())
    .finally(() => {
      // Optional: Remove from cache after some time
      setTimeout(() => {
        delete promiseCache[url];
      }, 60000); // Clear cache after 1 minute
    });
  
  promiseCache[url] = promise;
  return promise;
}

// Multiple calls only make one request
fetchDataWithCache('/api/data'); // Makes request
fetchDataWithCache('/api/data'); // Returns cached promise
```

#### **Pattern 2: Retry Logic**
```javascript
function retryPromise(fn, retries = 3, delay = 1000) {
  return new Promise((resolve, reject) => {
    const attempt = (attemptNumber) => {
      fn()
        .then(resolve)
        .catch(error => {
          if (attemptNumber < retries) {
            console.log(`Attempt ${attemptNumber} failed, retrying...`);
            setTimeout(() => attempt(attemptNumber + 1), delay);
          } else {
            reject(`Failed after ${retries} attempts: ${error}`);
          }
        });
    };
    
    attempt(1);
  });
}

// Usage: Retry API call 3 times
retryPromise(() => fetch('/api/unstable-endpoint'), 3, 2000)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

#### **Pattern 3: Progress Tracking**
```javascript
function promiseWithProgress(promises) {
  let completed = 0;
  const total = promises.length;
  
  promises.forEach(promise => {
    promise.then(() => {
      completed++;
      const progress = (completed / total) * 100;
      console.log(`Progress: ${progress.toFixed(1)}%`);
    });
  });
  
  return Promise.all(promises);
}

// Usage
const tasks = [
  new Promise(resolve => setTimeout(resolve, 1000)),
  new Promise(resolve => setTimeout(resolve, 2000)),
  new Promise(resolve => setTimeout(resolve, 3000))
];

promiseWithProgress(tasks)
  .then(() => console.log('All tasks completed'));
```

### **Common Mistakes and Solutions**

#### **Mistake 1: Forgetting to Return**
```javascript
// ❌ Wrong: Forgot to return the promise
somePromise()
  .then(result => {
    anotherPromise(); // This promise is created but not returned
  })
  .then(result => {
    // result is undefined!
  });

// ✅ Correct: Always return
somePromise()
  .then(result => {
    return anotherPromise(); // Return the promise
  })
  .then(result => {
    // Now result is from anotherPromise
  });
```

#### **Mistake 2: Not Handling Errors**
```javascript
// ❌ Wrong: Unhandled promise rejection
const promise = new Promise((resolve, reject) => {
  reject('Error!');
});
// Uncaught error in console!

// ✅ Correct: Always handle errors
promise.catch(error => console.error(error));

// Or use async/await with try-catch
```

#### **Mistake 3: Creating Promise inside Promise**
```javascript
// ❌ Wrong: Unnecessary nesting
somePromise().then(result => {
  return new Promise(resolve => {
    // Unnecessary wrapper
    resolve(process(result));
  });
});

// ✅ Correct: Direct return
somePromise().then(result => {
  return process(result); // Just return the value
});
```

### **Promise vs Callback Comparison**

| Aspect | Callbacks | Promises |
|--------|-----------|----------|
| **Readability** | Callback hell | Clean chains |
| **Error Handling** | Manual (error-first) | Automatic (.catch()) |
| **Multiple Operations** | Hard to coordinate | Easy (Promise.all) |
| **Chaining** | Nested callbacks | Flat chains |
| **Modern Usage** | Legacy | Standard |

### **Quick Reference Cheat Sheet**

```javascript
// CREATE PROMISE
const promise = new Promise((resolve, reject) => {
  if (success) resolve(value);
  else reject(error);
});

// USE PROMISE
promise
  .then(result => { /* success */ })
  .catch(error => { /* error */ })
  .finally(() => { /* always runs */ });

// STATIC METHODS
Promise.all([p1, p2])        // Wait for all
Promise.race([p1, p2])       // First to finish
Promise.allSettled([p1, p2]) // All, even failures
Promise.any([p1, p2])        // First success
Promise.resolve(value)       // Create resolved promise
Promise.reject(error)        // Create rejected promise

// ERROR HANDLING
promise.catch(error => {})   // Catch errors
throw new Error('msg')       // Throw in chain
```

### **Summary**

**Key Takeaways:**
1. **Promises handle async operations** cleanly
2. **Three states**: Pending → Fulfilled/Rejected
3. **Chain with `.then()`** for sequential operations
4. **Handle errors with `.catch()`**
5. **Run in parallel** with `Promise.all()`
6. **Always return promises** in chains
7. **Convert callbacks to promises** for modern code

**When to use Promises:**
- API calls
- File operations
- Database queries
- Timers (setTimeout with Promises)
- Any async operation

**Remember:** Promises make async code look synchronous and are the foundation for the even cleaner `async/await` syntax (coming next)!

---

**Ready for Topic 43: "Async await"?**

## 🔗 Related Notes
- [[Web Development/React/React Topics/Async-Await|Async/Await]]
- [[Web Development/React/React Topics/Axios|Axios]]
