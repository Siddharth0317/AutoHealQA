# AutoHealQA Supported User Stories & Demo Test Cases Guide

This document provides a reference taxonomy of natural language user story patterns, demo target applications, and ready-to-use prompt examples supported by **AutoHealQA**.

---

## 1. 🔐 Authentication & Security User Stories

* **Primary Focus**: User login, registration, password validation, role-based access, and session management.
* **Demo Target Application**: `https://the-internet.herokuapp.com/login` or `https://www.saucedemo.com/`

### Ready-to-Use Prompt Example:
```text
As a registered user, I want to navigate to https://the-internet.herokuapp.com/login, enter username "tomsmith" and password "SuperSecretPassword!", click the Login button, and verify the success alert banner "You logged into a secure area!" is displayed.
```

---

## 2. 🛒 E-Commerce & Shopping Cart User Stories

* **Primary Focus**: Product listing navigation, cart additions, quantity updates, multi-step checkout forms, and total price validation.
* **Demo Target Application**: `https://www.saucedemo.com/`

### Ready-to-Use Prompt Example:
```text
As a shopper on https://www.saucedemo.com/, I want to log in with "standard_user" and "secret_sauce", add "Sauce Labs Backpack" to my cart, click the cart icon, and verify the backpack item is listed in the cart.
```

---

## 3. 📝 CRUD Data Management User Stories (Create, Read, Update, Delete)

* **Primary Focus**: Form data creation, inline item editing, task completion toggling, filtering, and record deletion with confirmation dialogs.
* **Demo Target Application**: `https://demo.playwright.dev/todomvc`

### Ready-to-Use Prompt Example:
```text
As a user on https://demo.playwright.dev/todomvc, I want to type "Buy Milk" and press Enter, type "Write Automation Tests" and press Enter, click the check toggle for "Buy Milk", and verify "1 item left" is displayed.
```

---

## 4. ⚡ Dynamic UI & Form Controls User Stories

* **Primary Focus**: Asynchronous AJAX loaders, dynamic element additions/removals, checkbox toggles, and modal popups.
* **Demo Target Application**: `https://the-internet.herokuapp.com/dynamic_controls`

### Ready-to-Use Prompt Example:
```text
As a tester on https://the-internet.herokuapp.com/dynamic_controls, I want to click the "Remove" button, wait for the checkbox to disappear, and verify the text "It's gone!" appears on screen.
```

---

## 5. 🩹 Self-Healing & Outdated Selector Repair User Stories

* **Primary Focus**: Validating AutoHealQA's real-time AI selector repair engine when UI elements undergo DOM attribute changes.
* **Demo Target Application**: `https://example.com`

### Ready-to-Use Prompt Example:
```text
As a QA engineer, I want to navigate to https://example.com, verify the main header is visible, check that the container loads correctly, and click the primary action link.
```

---

## 🚀 How to Execute User Stories in AutoHealQA:

1. Copy any prompt from the categories above.
2. Open the dashboard at **`http://localhost:3000`**.
3. Paste the prompt into **Tab 1: Requirements Analyzer**.
4. Set **Execution Mode** to **`👀 Open Live Browser Window`**.
5. Click **`Generate Structured BDD Test Cases`** $\rightarrow$ **`Execute Test Suite`**.
