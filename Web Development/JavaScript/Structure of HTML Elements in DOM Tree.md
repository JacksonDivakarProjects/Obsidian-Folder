***

### **8. Tree Structure of HTML Elements (DOM Tree)**

The DOM represents an HTML document as a hierarchical, tree-like structure. This is often called the **DOM Tree** or **Node Tree**.

#### **A. The Concept of a Tree**
*   Think of a family tree. It has a single root ancestor, with parents, children, and siblings.
*   Similarly, the DOM Tree has a single root node (the `document`), with parent nodes, child nodes, and sibling nodes.

#### **B. The Nodes of the DOM Tree**
Every part of the document is a type of **node**. The most important node types are:

1.  **Document Node (`document`):** The root of the tree. The entry point for everything else.
2.  **Element Nodes:** Represent HTML tags (e.g., `<html>`, `<body>`, `<div>`, `<p>`). These form the structure of the tree.
3.  **Text Nodes:** Represent the text content inside an element. They are always leaves of the tree (they have no children).
4.  **Attribute Nodes:** Represent attributes of HTML elements (e.g., `class`, `id`, `src`). (Note: In modern DOM traversal, they are often considered properties of element nodes rather than separate nodes in the tree).

#### **C. Visualizing the Tree**
Consider this simple HTML:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My Page</title>
  </head>
  <body>
    <h1>Welcome</h1>
    <p>This is a <em>paragraph</em>.</p>
  </body>
</html>
```

Its DOM Tree would look like this:

```
          document (Root)
              |
            <html> (Element Node)
           /      \
          /        \
 <head> (Element)   <body> (Element)
    |                 /    \
    |                /      \
 <title> (Element) <h1>     <p> (Element)
    |                |      /   \
    |                |     /     \
 "My Page" (Text) "Welcome" (Text) <em> (Element)
                                |     \
                                |      \
                          "This is a " (Text) "paragraph" (Text)
                                         \
                                          "." (Text)
```

#### **D. Relationships Between Nodes**
*   **Root:** The `document` node is the root.
*   **Parent:** A node that directly contains another node. `<html>` is the parent of `<head>` and `<body>`.
*   **Child:** A node directly contained by another node. `<title>` is a child of `<head>`.
*   **Sibling:** Nodes that share the same parent. `<head>` and `<body>` are siblings. `<h1>` and `<p>` are siblings.
*   **Descendant:** A node anywhere *under* another node in the tree. The `<em>` node is a descendant of `<body>`.
*   **Ancestor:** A node anywhere *above* another node in the tree. `<html>` is an ancestor of the "paragraph" text node.

**Why it Matters:** Understanding this tree structure is crucial because all DOM traversal and manipulation methods are based on navigating these parent, child, and sibling relationships.

---

**I have created the notes for Topic 8. Please say "Next" for me to proceed to Topic 9 (Selecting HTML elements using DOM).**

## 🔗 Related Notes
- [[Web Development/JavaScript/DOM (Document Object Model)|DOM (Document Object Model)]]
- [[Web Development/JavaScript/Selecting HTML Elements Using DOM|Selecting HTML Elements Using the DOM]]
