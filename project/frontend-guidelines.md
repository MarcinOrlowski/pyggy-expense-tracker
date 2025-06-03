# Frontend Guidelines - Expense Tracker PoC - Simplified Frontend Architecture

## 1. Overview

This document defines the frontend architecture guidelines for the Expense Tracker PoC, emphasizing simplicity, maintainability, and proper separation of concerns without complex build tools.

## 2. Core Principles

1. **Separation of Concerns**: CSS, JavaScript, and HTML are kept in separate files
2. **Simplicity First**: No complex build tools or frameworks for PoC
3. **Django Integration**: Leverage Django's static file handling
4. **Progressive Enhancement**: Basic functionality works without JavaScript
5. **Maintainable Code**: Clear structure and naming conventions

## 3. File Organization

```
static/
├── css/
│   ├── base.css           # Global styles
│   ├── components/        # Reusable component styles
│   │   ├── forms.css
│   │   ├── tables.css
│   │   └── messages.css
│   └── pages/            # Page-specific styles
│       ├── dashboard.css
│       ├── expenses.css
│       └── auth.css
├── js/
│   ├── base.js           # Global JavaScript
│   ├── components/       # Reusable component scripts
│   │   ├── forms.js
│   │   └── tables.js
│   └── pages/           # Page-specific scripts
│       ├── dashboard.js
│       └── expenses.js
└── images/
    ├── icons/
    └── logos/
```

## 4. CSS Guidelines

### 4.1 What's Allowed

✅ **External CSS files referenced via Django static**

```html
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<link rel="stylesheet" href="{% static 'css/pages/dashboard.css' %}">
```

✅ **Conditional CSS loading**

```html
{% if user.is_authenticated %}
    <link rel="stylesheet" href="{% static 'css/authenticated.css' %}">
{% endif %}
```

✅ **Component-specific CSS**

```html
{% if page_type == 'dashboard' %}
    <link rel="stylesheet" href="{% static 'css/pages/dashboard.css' %}">
{% endif %}
```

### 4.2 What's Not Allowed

❌ **Inline styles**

```html
<!-- Don't do this -->
<div style="color: red; margin: 10px;">Content</div>
```

❌ **Style blocks with actual CSS code**

```html
<!-- Don't do this -->
<style>
.my-class {
    color: red;
    margin: 10px;
}
</style>
```

### 4.3 CSS Structure

```css
/* static/css/base.css */

/* Reset and base styles */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    color: #333;
}

/* Layout */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Navigation */
.nav {
    background: #f8f9fa;
    padding: 1rem 0;
    border-bottom: 1px solid #dee2e6;
}

.nav-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: #495057;
    text-decoration: none;
    font-weight: 500;
}

.nav-link:hover {
    color: #007bff;
}

/* Components */
.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    text-decoration: none;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn:hover {
    background: #0056b3;
}

.btn-secondary {
    background: #6c757d;
}

.btn-danger {
    background: #dc3545;
}

/* Messages */
.messages {
    margin: 1rem 0;
}

.message {
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
}

.message-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

/* Forms */
.form-group {
    margin-bottom: 1rem;
}

.form-label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
}

.form-control:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* Tables */
.table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
}

.table th,
.table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

.table th {
    background: #f8f9fa;
    font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 0 10px;
    }
    
    .nav-list {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .table {
        font-size: 0.9rem;
    }
    
    .table th,
    .table td {
        padding: 0.5rem;
    }
}
```

## 5. JavaScript Guidelines

### 5.1 What's Allowed

✅ **External JavaScript files**

```html
<script src="{% static 'js/base.js' %}"></script>
<script src="{% static 'js/pages/dashboard.js' %}"></script>
```

✅ **Conditional JavaScript loading**

```html
{% if page_requires_charts %}
    <script src="{% static 'js/components/charts.js' %}"></script>
{% endif %}
```

✅ **Script tags for external libraries**

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@1.8.4/dist/htmx.min.js"></script>
```

### 5.2 What's Not Allowed

❌ **Inline JavaScript**

```html
<!-- Don't do this -->
<button onclick="alert('clicked')">Click me</button>
```

❌ **Script blocks with actual JavaScript code**

```html
<!-- Don't do this -->
<script>
function myFunction() {
    alert('Hello');
}
</script>
```

### 5.3 JavaScript Structure

```javascript
// static/js/base.js

// Global utilities and common functionality
(function() {
    'use strict';
    
    // DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeCommonFeatures();
    });
    
    function initializeCommonFeatures() {
        // Auto-hide messages after 5 seconds
        hideMessagesAfterDelay();
        
        // Form validation enhancement
        enhanceFormValidation();
        
        // Confirm delete actions
        confirmDeleteActions();
    }
    
    function hideMessagesAfterDelay() {
        const messages = document.querySelectorAll('.message');
        messages.forEach(function(message) {
            setTimeout(function() {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 300);
            }, 5000);
        });
    }
    
    function enhanceFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                const requiredFields = form.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(function(field) {
                    if (!field.value.trim()) {
                        field.classList.add('error');
                        isValid = false;
                    } else {
                        field.classList.remove('error');
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                }
            });
        });
    }
    
    function confirmDeleteActions() {
        const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm-delete') || 
                               'Are you sure you want to delete this item?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }
    
})();
```

## 6. Template Structure

### 6.1 Base Template

```html
<!-- templates/expenses/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Expense Tracker{% endblock %}</title>
    
    <!-- Base CSS -->
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    
    <!-- Page-specific CSS -->
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        <nav class="nav">
            <div class="container">
                <ul class="nav-list">
                    <li><a href="{% url 'dashboard' %}" class="nav-link">Dashboard</a></li>
                    <li><a href="{% url 'expense_list' %}" class="nav-link">Expenses</a></li>
                    <li><a href="{% url 'expense_create' %}" class="nav-link">Add Expense</a></li>
                    {% if user.is_authenticated %}
                        <li><a href="{% url 'admin:logout' %}" class="nav-link">Logout</a></li>
                    {% endif %}
                </ul>
            </div>
        </nav>
    </header>
    
    <main>
        <div class="container">
            {% if messages %}
                <div class="messages">
                    {% for message in messages %}
                        <div class="message message-{{ message.tags }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
            
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <!-- Base JavaScript -->
    <script src="{% static 'js/base.js' %}"></script>
    
    <!-- Page-specific JavaScript -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6.2 Page Template Example

```html
<!-- templates/expenses/dashboard.html -->
{% extends 'expenses/base.html' %}
{% load static %}

{% block title %}Dashboard - Expense Tracker{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/pages/dashboard.css' %}">
{% endblock %}

{% block content %}
    <h1>Dashboard</h1>
    
    <div class="dashboard-summary">
        <div class="summary-card">
            <h3>This Month</h3>
            <p class="amount">${{ total_pending|floatformat:2 }}</p>
            <p class="label">Pending Payments</p>
        </div>
    </div>
    
    {% if pending_items %}
        <h2>Upcoming Payments</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Expense</th>
                    <th>Payee</th>
                    <th>Due Date</th>
                    <th>Amount</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in pending_items %}
                    <tr>
                        <td>{{ item.expense.title }}</td>
                        <td>{{ item.expense.payee.name }}</td>
                        <td>{{ item.due_date }}</td>
                        <td>${{ item.amount|floatformat:2 }}</td>
                        <td>
                            <a href="{% url 'expense_item_pay' item.pk %}" class="btn btn-small">
                                Mark Paid
                            </a>
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>No pending payments for this month.</p>
    {% endif %}
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/pages/dashboard.js' %}"></script>
{% endblock %}
```

## 7. Component Guidelines

### 7.1 Form Components

Create reusable form components:

```html
<!-- templates/expenses/components/expense_form.html -->
<form method="post" class="expense-form">
    {% csrf_token %}
    
    <div class="form-group">
        <label for="{{ form.title.id_for_label }}" class="form-label">
            {{ form.title.label }}
        </label>
        {{ form.title }}
        {% if form.title.errors %}
            <div class="form-errors">
                {{ form.title.errors }}
            </div>
        {% endif %}
    </div>
    
    <div class="form-group">
        <label for="{{ form.payee.id_for_label }}" class="form-label">
            {{ form.payee.label }}
        </label>
        {{ form.payee }}
        {% if form.payee.errors %}
            <div class="form-errors">
                {{ form.payee.errors }}
            </div>
        {% endif %}
    </div>
    
    <!-- More form fields -->
    
    <div class="form-actions">
        <button type="submit" class="btn">Save Expense</button>
        <a href="{% url 'expense_list' %}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
```

## 8. Progressive Enhancement

Build functionality that works without JavaScript, then enhance:

```html
<!-- Basic form that works without JS -->
<form method="post" action="{% url 'expense_create' %}">
    {% csrf_token %}
    <!-- form fields -->
    <button type="submit">Save</button>
</form>

<!-- Enhanced with JavaScript for better UX -->
```

```javascript
// static/js/components/forms.js
document.addEventListener('DOMContentLoaded', function() {
    enhanceExpenseForms();
});

function enhanceExpenseForms() {
    const expenseForms = document.querySelectorAll('.expense-form');
    expenseForms.forEach(function(form) {
        // Add real-time validation
        // Add auto-save functionality
        // Add dynamic field updates
    });
}
```

## 9. Performance Guidelines

1. **Minimize HTTP Requests**: Combine CSS files when possible
2. **Optimize Images**: Use appropriate formats and sizes
3. **Lazy Loading**: Load JavaScript only when needed
4. **Caching**: Leverage Django's static file caching
5. **Minification**: Consider minifying CSS/JS for production

## 10. Browser Support

Target modern browsers with graceful degradation:

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 11. Development Workflow

1. **Create HTML structure first** (semantic, accessible)
2. **Add CSS styling** (mobile-first, progressive enhancement)
3. **Add JavaScript enhancement** (optional, progressive)
4. **Test across devices** (responsive, accessible)
5. **Validate code** (HTML, CSS, JS)

This approach ensures a maintainable, accessible, and performant frontend that can grow with the project while keeping the PoC development simple and fast.
