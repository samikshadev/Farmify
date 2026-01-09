# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'farmify_secret_key_2024'

# Database initialization
def init_db():
    conn = sqlite3.connect('farmify.db')
    c = conn.cursor()
    
    # Create farmers table
    c.execute('''CREATE TABLE IF NOT EXISTS farmers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  location TEXT NOT NULL)''')
    
    # Create buyers table
    c.execute('''CREATE TABLE IF NOT EXISTS buyers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  location TEXT NOT NULL)''')
    
    # Create crops table
    c.execute('''CREATE TABLE IF NOT EXISTS crops
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farmer_id INTEGER NOT NULL,
                  crop_name TEXT NOT NULL,
                  quantity TEXT NOT NULL,
                  price TEXT NOT NULL,
                  description TEXT,
                  FOREIGN KEY (farmer_id) REFERENCES farmers(id))''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Farmer registration
@app.route('/farmer_register', methods=['GET', 'POST'])
def farmer_register():
    if request.method == 'POST':
        name = request.form['name']
        if not all(char.isalpha() or char == ' ' for char in name):
            flash('Name must contain only alphabetic characters and spaces!', 'error')
            return redirect(url_for('farmer_register'))
        email = request.form['email']
        if '@' not in email or '.' not in email:
            flash('Invalid email format!', 'error')
            return redirect(url_for('farmer_register'))
        password = request.form['password']
        import re
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[\W_]', password):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character!', 'error')
            return redirect(url_for('farmer_register'))
        phone = request.form['phone']
        if not phone.isdigit() or len(phone) != 10:
            flash('Phone number must be exactly 10 digits!', 'error')
            return redirect(url_for('farmer_register'))
        location = request.form['location']
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('farmify.db')
            c = conn.cursor()
            c.execute("INSERT INTO farmers (name, email, password, phone, location) VALUES (?, ?, ?, ?, ?)",
                     (name, email, hashed_password, phone, location))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
            return redirect(url_for('farmer_register'))
    
    return render_template('farmer_register.html')

# Buyer registration
@app.route('/buyer_register', methods=['GET', 'POST'])
def buyer_register():
    if request.method == 'POST':
        name = request.form['name']
        if not all(char.isalpha() or char == ' ' for char in name):
            flash('Name must contain only alphabetic characters and spaces!', 'error')
            return redirect(url_for('buyer_register'))
        email = request.form['email']
        if not email.endswith('@example.com'):
            flash('Email must be from the domain @example.com!', 'error')
            return redirect(url_for('buyer_register'))
        password = request.form['password']
        import re                               
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[\W_]', password):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character!', 'error')
            return redirect(url_for('buyer_register'))
        phone = request.form['phone']
        if not phone.isdigit() or len(phone) != 10:          
            flash('Phone number must be exactly 10 digits!', 'error')
            return redirect(url_for('buyer_register'))
        location = request.form['location']
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('farmify.db')
            c = conn.cursor()
            c.execute("INSERT INTO buyers (name, email, password, phone, location) VALUES (?, ?, ?, ?, ?)",
                     (name, email, hashed_password, phone, location))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
            return redirect(url_for('buyer_register'))
    
    return render_template('buyer_register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = sqlite3.connect('farmify.db')
        c = conn.cursor()
        
        if user_type == 'farmer':
            c.execute("SELECT * FROM farmers WHERE email=?", (email,))
            user = c.fetchone()
            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_type'] = 'farmer'
                conn.close()
                return redirect(url_for('farmer_dashboard'))
        
        elif user_type == 'buyer':
            c.execute("SELECT * FROM buyers WHERE email=?", (email,))
            user = c.fetchone()
            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_type'] = 'buyer'
                conn.close()
                return redirect(url_for('buyer_dashboard'))
        
        conn.close()
        flash('Invalid credentials!', 'error')
        return redirect(url_for('login'))
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Farmer dashboard
@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_type' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmify.db')
    c = conn.cursor()
    c.execute("SELECT * FROM crops WHERE farmer_id=?", (session['user_id'],))
    crops = c.fetchall()
    conn.close()
    
    return render_template('farmer_dashboard.html', crops=crops)

# Add crop
@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if 'user_type' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        crop_name = request.form['crop_name']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']
        
        conn = sqlite3.connect('farmify.db')
        c = conn.cursor()
        c.execute("INSERT INTO crops (farmer_id, crop_name, quantity, price, description) VALUES (?, ?, ?, ?, ?)",
                 (session['user_id'], crop_name, quantity, price, description))
        conn.commit()
        conn.close()
        
        flash('Crop added successfully!', 'success')
        return redirect(url_for('farmer_dashboard'))
    
    return render_template('add_crop.html')

# Buyer dashboard
@app.route('/buyer_dashboard')
def buyer_dashboard():
    if 'user_type' not in session or session['user_type'] != 'buyer':
        return redirect(url_for('login'))
    
    return render_template('buyer_dashboard.html')

# View all crops (marketplace)
@app.route('/view_crops')
def view_crops():
    if 'user_type' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmify.db')
    c = conn.cursor()
    c.execute('''SELECT crops.*, farmers.name, farmers.phone, farmers.location 
                 FROM crops 
                 JOIN farmers ON crops.farmer_id = farmers.id''')
    crops = c.fetchall()
    conn.close()
    
    return render_template('view_crops.html', crops=crops)

if __name__ == '__main__':
    app.run(debug=True)