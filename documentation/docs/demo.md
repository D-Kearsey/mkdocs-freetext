# Live Demo

Experience the MkDocs Free-Text Questions Plugin in action! All examples below are **fully interactive** - try typing in the answer boxes, toggling sample answers, and exploring the features.

!!! tip "Interactive Examples"
    All questions on this page are live and functional. Your answers are automatically saved in your browser's local storage.

## Basic Question

Try answering this simple question using our modern syntax:

!!! freetext
    What is the capital of France?
    ---
    placeholder: Enter your answer here..., marks: 2, show_answer: true, answer: """Paris is the capital of France, and it is also known as the City of Light, home to the Eiffel Tower."""

## Triple Quote Support for Complex Answers

The plugin now supports **triple quotes** (`"""`) to handle answers containing commas, quotes, and complex punctuation:

!!! freetext
    List the programming languages you know and explain their primary use cases.
    ---
    marks: 5, show_answer: true, answer: """I know Python, JavaScript, and Java. Python is excellent for data science, machine learning, and backend development. JavaScript powers web frontend, Node.js backends, and mobile apps. Java is used for enterprise applications, Android development, and large-scale systems."""

!!! freetext
    Explain the time complexity of common sorting algorithms.
    ---
    marks: 8, placeholder: "Discuss Big O notation and algorithm performance...", show_answer: true, answer: """Common sorting algorithms have different time complexities: Bubble Sort is O(n²) in worst case, O(n) in best case. Quick Sort averages O(n log n) but worst case is O(n²). Merge Sort is consistently O(n log n). Heap Sort is O(n log n) guaranteed. The "best" algorithm depends on data size, memory constraints, and whether the data is partially sorted."""

## Question with Code Block

This example shows how questions can include syntax-highlighted code blocks:

!!! freetext
    Analyze the following Python function and explain what it does:
    
    ```python
    def binary_search(arr, target):
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1
    ```
    
    What is the time complexity and when would you use this algorithm?
    ---
    marks: 5, placeholder: Explain the algorithm, its complexity, and use cases..., show_answer: true, answer: This is a binary search algorithm that finds the position of a target value in a sorted array. Time complexity is O(log n) because it eliminates half the search space in each iteration. It's used when you need fast lookups in sorted data, much more efficient than linear search O(n) for large datasets.

## Mermaid Diagram Question

See how the plugin handles interactive Mermaid diagrams within questions:

!!! freetext
    Based on this microservices architecture diagram, identify potential issues and suggest improvements:
    
    ```mermaid
    graph TD
        A[Frontend App] --> B[API Gateway]
        B --> C[User Service]
        B --> D[Order Service]
        B --> E[Payment Service]
        C --> F[(User DB)]
        D --> G[(Order DB)]
        E --> H[(Payment DB)]
        D --> I[Email Service]
        E --> I
        I --> J[External Email API]
    ```
    
    Consider scalability, reliability, and security aspects.
    ---
    marks: 12, placeholder: Analyze the architecture and suggest improvements..., show_answer: true, answer: Potential issues: 1) Single API Gateway bottleneck, 2) No service discovery mechanism, 3) Direct database connections without connection pooling, 4) No caching layer, 5) Missing monitoring/logging. Improvements: Load balance the API Gateway, implement service mesh (Istio), add Redis caching, use database connection pools, implement circuit breakers, add distributed tracing, and use message queues for async communication between services.

## Visual Learning with Images

Questions can include educational images and diagrams:

!!! freetext
    Examine this data structure visualization and answer the following:
    
    ![Binary Tree Structure](https://via.placeholder.com/500x300/4CAF50/FFFFFF?text=Binary+Tree%0A%0A%20%20%20%20%20%20%2010%0A%20%20%20%20%2F%20%20%20%20%5C%0A%20%20%205%20%20%20%20%20%20%2015%0A%20%2F%20%5C%20%20%20%20%20%2F%20%20%5C%0A%203%20%20%207%20%20%2012%20%2018)
    
    1. What type of tree traversal would visit nodes in the order: 3, 5, 7, 10, 12, 15, 18?
    2. What is the height of this tree?
    3. Is this a valid Binary Search Tree?
    
    ---
    
    marks: 8,
    placeholder: Answer all three questions about the binary tree...,
    show_answer: true,
    answer: 1. In-order traversal (left, root, right) produces ascending order in a BST. 2. The height is 3 (counting edges from root to deepest leaf). 3. Yes, this is a valid BST because for every node, left subtree values are smaller and right subtree values are larger.

## Algorithm Flowchart Question

Questions can include flowcharts to visualize algorithms and processes:

!!! freetext
    Study this algorithm flowchart and explain what sorting algorithm it represents:
    
    ```mermaid
    flowchart TD
        A[Start: Array of n elements] --> B[i = 0]
        B --> C{i < n-1?}
        C -->|No| Z[End: Array sorted]
        C -->|Yes| D[j = 0]
        D --> E{j < n-i-1?}
        E -->|No| F[i = i + 1]
        F --> C
        E -->|Yes| G{arr[j] > arr[j+1]?}
        G -->|No| H[j = j + 1]
        G -->|Yes| I[Swap arr[j] and arr[j+1]]
        I --> H
        H --> E
    ```
    
    What is the name of this algorithm and what are its time complexities for best, average, and worst cases?
    
    ---
    
    marks: 10,
    placeholder: Identify the algorithm and analyze its complexity...,
    show_answer: true,
    answer: This is the Bubble Sort algorithm. It repeatedly steps through the list, compares adjacent elements and swaps them if they're in the wrong order. Time complexities: Best case O(n) when array is already sorted, Average case O(n²), Worst case O(n²) when array is reverse sorted. Space complexity is O(1) as it sorts in-place.

## Multi-Language Code Example

Demonstrate code syntax highlighting across different programming languages:

!!! freetext
    Compare these three implementations of the same function in different languages:
    
    **Python:**

    ```python
    def factorial(n):
        return 1 if n <= 1 else n * factorial(n - 1)
    ```
    
    **JavaScript:**

    ```javascript
    function factorial(n) {
        return n <= 1 ? 1 : n * factorial(n - 1);
    }
    ```
    
    **Java:**

    ```java
    public static int factorial(int n) {
        return (n <= 1) ? 1 : n * factorial(n - 1);
    }
    ```
    
    What programming concept do all three implementations demonstrate, and what are the potential risks?
    
    ---
    
    marks: 7,
    placeholder: Identify the concept and discuss potential issues...,
    show_answer: true,
    answer: All three demonstrate recursion - a function calling itself with a modified parameter. The concept relies on a base case (n <= 1) to prevent infinite recursion. Potential risks include: stack overflow for large inputs, inefficiency due to repeated calculations, and memory usage from call stack build-up. Iterative solutions or memoization can address these issues.

The plugin supports comprehensive assessments with multiple questions:

!!! freetext-assessment
    title: Python Fundamentals Assessment
    shuffle: true
    
    What is a variable in Python and how do you create one?
    
    ---
    
    marks: 3,
    placeholder: Describe variables and their creation...,
    show_answer: true,
    answer: A variable in Python is a name that refers to a value stored in memory. You create one by simply assigning a value: `x = 5` or `name = "Hello"`. Python is dynamically typed, so you don't need to declare the type.
    
    ---
    
    Explain the difference between a list and a tuple in Python.
    
    ---
    
    marks: 5,
    placeholder: Compare lists and tuples...,
    show_answer: true,
    answer: Lists are mutable (can be changed after creation) and use square brackets: `[1,2,3]`. Tuples are immutable (cannot be changed) and use parentheses: `(1,2,3)`. Lists are better for collections that may change, tuples for fixed data.
    
    ---
    
    What is a function in Python? Write a simple example.
    
    ---
    
    marks: 4,
    placeholder: Define functions and provide an example...,
    show_answer: true,
    answer: A function is a reusable block of code that performs a specific task. Example: `def greet(name): return f"Hello, {name}!"` - This function takes a name parameter and returns a greeting string.

## Character Counter Demo

Notice the character counter in the bottom-right of text areas (can be disabled):

!!! freetext
    Write a short paragraph (aim for 100-200 characters) explaining your favourite programming language and why you enjoy using it.
    
    ---
    
    marks: 3,
    placeholder: Write about your favourite programming language...

## Long-Form Question

Perfect for essays and detailed responses:

!!! freetext
    Design a simple web application architecture for an online bookstore. Include the following components and explain how they interact:
    
    - Frontend (user interface)
    - Backend API
    - Database
    - Payment processing
    - Inventory management
    
    Draw a simple diagram or describe the data flow between components.
    
    ---
    
    marks: 15,
    type: long,
    placeholder: Describe your bookstore architecture design in detail...,
    show_answer: true,
    answer: A typical architecture would include: 1) React/Vue frontend for user interface, 2) REST API backend (Node.js/Python), 3) PostgreSQL database for books/users/orders, 4) Stripe API for payments, 5) Inventory service tracking stock levels. Data flow: User browses books → Frontend calls API → API queries database → User adds to cart → Checkout triggers payment API → Successful payment updates inventory and creates order record.

---

