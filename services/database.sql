-- ===============================
-- Users & Session
-- ===============================
CREATE TABLE
    IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS session (username TEXT UNIQUE);

-- ===============================
-- Customers & Accounts
-- ===============================
CREATE TABLE
    IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        contact TEXT,
        address TEXT,
        type TEXT NOT NULL CHECK (
            type IN ('customer', 'supplier', 'seller', 'wholeSeller')
        ),
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS customer_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        type TEXT CHECK (type IN ('CR', 'DR')) NOT NULL,
        amount REAL NOT NULL CHECK (amount >= 0),
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers (email);

CREATE INDEX IF NOT EXISTS idx_customer_accounts_customer_id ON customer_accounts (customer_id);

-- ===============================
-- Categories & Products
-- ===============================
CREATE TABLE
    IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        sku TEXT UNIQUE,
        price REAL NOT NULL CHECK (price >= 0),
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id);

CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku);

-- ===============================
-- Product Stock
-- ===============================
CREATE TABLE
    IF NOT EXISTS product_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity >= 0),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_product_stocks_product_id ON product_stocks (product_id);

-- ===============================
-- Purchase Orders & Products
-- ===============================
CREATE TABLE
    IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        total_amount REAL NOT NULL CHECK (total_amount >= 0),
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES customers (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS purchase_order_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity >= 0),
        price REAL NOT NULL CHECK (price >= 0),
        FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_purchase_order_products_order_id ON purchase_order_products (purchase_order_id);

CREATE INDEX IF NOT EXISTS idx_purchase_order_products_product_id ON purchase_order_products (product_id);

-- ===============================
-- Sale Orders & Products
-- ===============================
CREATE TABLE
    IF NOT EXISTS sale_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        total_amount REAL NOT NULL CHECK (total_amount >= 0),
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS sale_order_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity >= 0),
        price REAL NOT NULL CHECK (price >= 0),
        FOREIGN KEY (sale_order_id) REFERENCES sale_orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_sale_order_products_order_id ON sale_order_products (sale_order_id);

CREATE INDEX IF NOT EXISTS idx_sale_order_products_product_id ON sale_order_products (product_id);