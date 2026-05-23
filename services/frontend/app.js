/* ============================================
   E-Commerce Store - Main JavaScript
   ============================================ */

// Initial Mock Data
const INITIAL_PRODUCTS = [
  { id: 1, name: "iPhone 15 Pro", price: 999, stock: 10, category: "Electronics", image: "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&h=400&fit=crop", description: "Latest Apple smartphone with A17 chip" },
  { id: 2, name: "Samsung Galaxy S24", price: 899, stock: 15, category: "Electronics", image: "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400&h=400&fit=crop", description: "Premium Android phone with AI features" },
  { id: 3, name: "Sony Headphones", price: 199, stock: 20, category: "Electronics", image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop", description: "Noise cancelling wireless headphones" },
  { id: 4, name: "Nike Air Max", price: 120, stock: 30, category: "Clothing", image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop", description: "Comfortable running shoes" },
  { id: 5, name: "Levi's Jeans", price: 65, stock: 25, category: "Clothing", image: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop", description: "Classic blue denim jeans" },
  { id: 6, name: "Python Programming Book", price: 45, stock: 50, category: "Books", image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop", description: "Learn Python from scratch" },
  { id: 7, name: "Coffee Maker", price: 79, stock: 12, category: "Home", image: "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400&h=400&fit=crop", description: "Automatic drip coffee machine" },
  { id: 8, name: "MacBook Pro", price: 1499, stock: 5, category: "Electronics", image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop", description: "16-inch laptop with M3 chip" }
];

const INITIAL_CATEGORIES = [
  { id: 1, name: "Electronics", description: "Phones, laptops, and gadgets" },
  { id: 2, name: "Clothing", description: "Fashion and apparel" },
  { id: 3, name: "Books", description: "Educational and entertainment books" },
  { id: 4, name: "Home", description: "Home appliances and decor" }
];

const INITIAL_USERS = [
  { id: 1, name: "Admin User", email: "admin@store.com", password: "admin123", role: "admin" },
  { id: 2, name: "John Customer", email: "john@example.com", password: "customer123", role: "customer" }
];

// ============================================
// Data Management Functions
// ============================================

function initializeData() {
  // Check if we need to refresh product images (v2 = Unsplash images)
  const dataVersion = localStorage.getItem('dataVersion');
  if (dataVersion !== 'v2') {
    // Reset products with new images
    localStorage.setItem('products', JSON.stringify(INITIAL_PRODUCTS));
    localStorage.setItem('dataVersion', 'v2');
  }
  
  if (!localStorage.getItem('products')) {
    localStorage.setItem('products', JSON.stringify(INITIAL_PRODUCTS));
  }
  if (!localStorage.getItem('categories')) {
    localStorage.setItem('categories', JSON.stringify(INITIAL_CATEGORIES));
  }
  if (!localStorage.getItem('users')) {
    localStorage.setItem('users', JSON.stringify(INITIAL_USERS));
  }
  if (!localStorage.getItem('orders')) {
    localStorage.setItem('orders', JSON.stringify([]));
  }
}

function getProducts() {
  return JSON.parse(localStorage.getItem('products')) || [];
}

function setProducts(products) {
  localStorage.setItem('products', JSON.stringify(products));
}

function getCategories() {
  return JSON.parse(localStorage.getItem('categories')) || [];
}

function setCategories(categories) {
  localStorage.setItem('categories', JSON.stringify(categories));
}

function getUsers() {
  return JSON.parse(localStorage.getItem('users')) || [];
}

function setUsers(users) {
  localStorage.setItem('users', JSON.stringify(users));
}

function getOrders() {
  return JSON.parse(localStorage.getItem('orders')) || [];
}

function setOrders(orders) {
  localStorage.setItem('orders', JSON.stringify(orders));
}

function getCurrentUser() {
  return JSON.parse(localStorage.getItem('currentUser'));
}

function setCurrentUser(user) {
  if (user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
  } else {
    localStorage.removeItem('currentUser');
  }
}

function getCart(userId) {
  return JSON.parse(localStorage.getItem(`cart_${userId}`)) || [];
}

function setCart(userId, cart) {
  localStorage.setItem(`cart_${userId}`, JSON.stringify(cart));
}

// ============================================
// Authentication Functions
// ============================================

function login(email, password) {
  const users = getUsers();
  const user = users.find(u => u.email === email && u.password === password);
  if (user) {
    const userWithoutPassword = { ...user };
    delete userWithoutPassword.password;
    setCurrentUser(userWithoutPassword);
    return { success: true, user: userWithoutPassword };
  }
  return { success: false, message: 'Invalid email or password' };
}

function register(name, email, password) {
  const users = getUsers();
  if (users.find(u => u.email === email)) {
    return { success: false, message: 'Email already exists' };
  }
  
  const newUser = {
    id: Date.now(),
    name,
    email,
    password,
    role: 'customer'
  };
  
  users.push(newUser);
  setUsers(users);
  
  const userWithoutPassword = { ...newUser };
  delete userWithoutPassword.password;
  setCurrentUser(userWithoutPassword);
  
  return { success: true, user: userWithoutPassword };
}

function logout() {
  setCurrentUser(null);
  window.location.href = 'index.html';
}

function isLoggedIn() {
  return getCurrentUser() !== null;
}

function isAdmin() {
  const user = getCurrentUser();
  return user && user.role === 'admin';
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function requireAdmin() {
  if (!isAdmin()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

// ============================================
// Cart Functions
// ============================================

function addToCart(productId, quantity = 1) {
  const user = getCurrentUser();
  if (!user) {
    showToast('Please login to add items to cart', 'warning');
    window.location.href = 'login.html';
    return false;
  }
  
  if (user.role === 'admin') {
    showToast('Admin users cannot add items to cart', 'warning');
    return false;
  }
  
  const products = getProducts();
  const product = products.find(p => p.id === productId);
  
  if (!product) {
    showToast('Product not found', 'error');
    return false;
  }
  
  if (product.stock < quantity) {
    showToast('Not enough stock available', 'error');
    return false;
  }
  
  const cart = getCart(user.id);
  const existingItem = cart.find(item => item.productId === productId);
  
  if (existingItem) {
    const newQuantity = existingItem.quantity + quantity;
    if (newQuantity > product.stock) {
      showToast('Cannot add more than available stock', 'error');
      return false;
    }
    existingItem.quantity = newQuantity;
  } else {
    cart.push({
      productId,
      quantity,
      name: product.name,
      price: product.price,
      image: product.image
    });
  }
  
  setCart(user.id, cart);
  updateCartBadge();
  showToast('Added to cart!', 'success');
  return true;
}

function updateCartQuantity(productId, quantity) {
  const user = getCurrentUser();
  if (!user) return false;
  
  const products = getProducts();
  const product = products.find(p => p.id === productId);
  
  if (!product || quantity > product.stock) {
    showToast('Not enough stock available', 'error');
    return false;
  }
  
  const cart = getCart(user.id);
  const item = cart.find(i => i.productId === productId);
  
  if (item) {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      item.quantity = quantity;
      setCart(user.id, cart);
      updateCartBadge();
    }
    return true;
  }
  return false;
}

function removeFromCart(productId) {
  const user = getCurrentUser();
  if (!user) return false;
  
  let cart = getCart(user.id);
  cart = cart.filter(item => item.productId !== productId);
  setCart(user.id, cart);
  updateCartBadge();
  showToast('Item removed from cart', 'info');
  return true;
}

function getCartTotal(userId) {
  const cart = getCart(userId);
  return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

function getCartItemCount() {
  const user = getCurrentUser();
  if (!user) return 0;
  const cart = getCart(user.id);
  return cart.reduce((count, item) => count + item.quantity, 0);
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  if (badge) {
    const count = getCartItemCount();
    badge.textContent = count;
    badge.style.display = count > 0 ? 'block' : 'none';
  }
}

// ============================================
// Order Functions
// ============================================

function createOrder() {
  const user = getCurrentUser();
  if (!user) return null;
  
  const cart = getCart(user.id);
  if (cart.length === 0) {
    showToast('Your cart is empty', 'warning');
    return null;
  }
  
  const products = getProducts();
  
  // Check stock availability
  for (const item of cart) {
    const product = products.find(p => p.id === item.productId);
    if (!product || product.stock < item.quantity) {
      showToast(`Not enough stock for ${item.name}`, 'error');
      return null;
    }
  }
  
  // Create order
  const order = {
    id: Date.now(),
    order_number: `ORD-${String(Date.now()).slice(-6)}`,
    user_id: user.id,
    user_name: user.name,
    date: new Date().toISOString(),
    status: 'pending',
    items: cart.map(item => ({
      productId: item.productId,
      name: item.name,
      price: item.price,
      quantity: item.quantity,
      image: item.image,
      subtotal: item.price * item.quantity
    })),
    total_amount: getCartTotal(user.id),
    shipping_address: '123 Main Street, City, Country 12345',
    payment_method: 'Credit Card ending in 4242'
  };
  
  // Update product stocks
  for (const item of cart) {
    const product = products.find(p => p.id === item.productId);
    if (product) {
      product.stock -= item.quantity;
    }
  }
  setProducts(products);
  
  // Save order
  const orders = getOrders();
  orders.push(order);
  setOrders(orders);
  
  // Clear cart
  setCart(user.id, []);
  updateCartBadge();
  
  showToast('Order placed successfully!', 'success');
  return order;
}

function getUserOrders(userId) {
  const orders = getOrders();
  return orders.filter(o => o.user_id === userId).sort((a, b) => new Date(b.date) - new Date(a.date));
}

function getOrderById(orderId) {
  const orders = getOrders();
  return orders.find(o => o.id === parseInt(orderId));
}

function updateOrderStatus(orderId, status) {
  const orders = getOrders();
  const order = orders.find(o => o.id === parseInt(orderId));
  if (order) {
    order.status = status;
    setOrders(orders);
    showToast('Order status updated', 'success');
    return true;
  }
  return false;
}

// ============================================
// Product Functions
// ============================================

function addProduct(product) {
  const products = getProducts();
  product.id = Date.now();
  products.push(product);
  setProducts(products);
  showToast('Product added successfully', 'success');
  return product;
}

function updateProduct(productId, updates) {
  const products = getProducts();
  const index = products.findIndex(p => p.id === parseInt(productId));
  if (index !== -1) {
    products[index] = { ...products[index], ...updates };
    setProducts(products);
    showToast('Product updated successfully', 'success');
    return products[index];
  }
  return null;
}

function deleteProduct(productId) {
  let products = getProducts();
  products = products.filter(p => p.id !== parseInt(productId));
  setProducts(products);
  showToast('Product deleted successfully', 'success');
}

// ============================================
// Category Functions
// ============================================

function addCategory(category) {
  const categories = getCategories();
  category.id = Date.now();
  categories.push(category);
  setCategories(categories);
  showToast('Category added successfully', 'success');
  return category;
}

function updateCategory(categoryId, updates) {
  const categories = getCategories();
  const index = categories.findIndex(c => c.id === parseInt(categoryId));
  if (index !== -1) {
    categories[index] = { ...categories[index], ...updates };
    setCategories(categories);
    showToast('Category updated successfully', 'success');
    return categories[index];
  }
  return null;
}

function deleteCategory(categoryId) {
  let categories = getCategories();
  categories = categories.filter(c => c.id !== parseInt(categoryId));
  setCategories(categories);
  showToast('Category deleted successfully', 'success');
}

// ============================================
// UI Helper Functions
// ============================================

function showLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.add('show');
  }
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.remove('show');
  }
}

function simulateLoading(callback, delay = 300) {
  showLoading();
  setTimeout(() => {
    hideLoading();
    if (callback) callback();
  }, delay);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-times-circle',
    warning: 'fa-exclamation-circle',
    info: 'fa-info-circle'
  };
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="fas ${icons[type]}"></i>
    <span class="toast-message">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function formatPrice(price) {
  return `$${price.toFixed(2)}`;
}

function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('en-US', options);
}

function getStockStatus(stock) {
  if (stock === 0) {
    return { class: 'stock-out', text: 'Out of Stock' };
  } else if (stock <= 5) {
    return { class: 'stock-low', text: `Only ${stock} left` };
  }
  return { class: 'stock-in', text: `${stock} in stock` };
}

function getStatusBadge(status) {
  const badges = {
    pending: 'badge-pending',
    processing: 'badge-processing',
    shipped: 'badge-shipped',
    delivered: 'badge-delivered',
    cancelled: 'badge-cancelled'
  };
  return `<span class="badge ${badges[status] || 'badge-pending'}">${status}</span>`;
}

// ============================================
// Navbar Functions
// ============================================

function renderNavbar() {
  const user = getCurrentUser();
  const isAdminUser = isAdmin();
  const cartCount = getCartItemCount();
  
  return `
    <nav class="navbar">
      <div class="container">
        <a href="index.html" class="navbar-brand">
          <i class="fas fa-store"></i>
          <span>ShopHub</span>
        </a>
        <ul class="navbar-nav">
          <li><a href="index.html" class="nav-link">Home</a></li>
          ${user && !isAdminUser ? `
            <li>
              <a href="cart.html" class="nav-link cart-icon">
                <i class="fas fa-shopping-cart"></i>
                <span id="cart-badge" class="cart-badge" style="display: ${cartCount > 0 ? 'block' : 'none'}">${cartCount}</span>
              </a>
            </li>
            <li><a href="orders.html" class="nav-link">My Orders</a></li>
          ` : ''}
          ${isAdminUser ? `
            <li><a href="admin.html" class="nav-link">Admin Dashboard</a></li>
          ` : ''}
          ${user ? `
            <li class="user-info">
              <i class="fas fa-user-circle"></i>
              <span>${user.name}</span>
            </li>
            <li><button onclick="logout()" class="btn btn-outline btn-sm">Logout</button></li>
          ` : `
            <li><a href="login.html" class="btn btn-outline btn-sm">Login</a></li>
            <li><a href="register.html" class="btn btn-primary btn-sm">Register</a></li>
          `}
        </ul>
      </div>
    </nav>
  `;
}

// ============================================
// Modal Functions
// ============================================

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('show');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.classList.remove('show');
  });
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('show');
  }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeAllModals();
  }
});

// ============================================
// Form Validation
// ============================================

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePassword(password) {
  return password.length >= 6;
}

function showFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(`${fieldId}-error`);
  if (field) field.classList.add('error');
  if (error) {
    error.textContent = message;
    error.classList.add('show');
  }
}

function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(`${fieldId}-error`);
  if (field) field.classList.remove('error');
  if (error) error.classList.remove('show');
}

function clearAllFieldErrors() {
  document.querySelectorAll('.form-control.error').forEach(field => {
    field.classList.remove('error');
  });
  document.querySelectorAll('.error-message.show').forEach(error => {
    error.classList.remove('show');
  });
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initializeData();
});
