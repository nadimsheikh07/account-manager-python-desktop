CREATE TABLE
    IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS session (username TEXT UNIQUE);

CREATE TABLE
    IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        contact TEXT,
        address TEXT,
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