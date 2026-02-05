# 🛍️ Merchandise Order Management System

A simple and efficient system for managing merchandise inventory and customer orders, built with Django 4.2.

## ✨ Features

- **No Price Field** - Focus on inventory and stock management only
- **No Order Status** - Orders are final once created
- **Simple Customer Data** - Just name and WhatsApp number
- **Auto Stock Deduction** - Stock automatically decreases on order creation
- **Role-Based Access** - Admin (Markom) and Sales with different permissions
- **Soft Delete** - Safe deletion that preserves order history
- **Stock History** - Complete audit trail of stock adjustments
- **Image Upload** - Merchandise photos with auto-optimization
- **Print Orders** - Clean, printer-friendly order forms

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip and virtualenv

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd marketplacecustomer
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create admin user**
```bash
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_user(username='admin', email='admin@example.com', password='admin123', full_name='Admin User', role='ADMIN', is_staff=True, is_superuser=True)
>>> exit()
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
```
http://localhost:8000
Login: admin / admin123
```

## 📖 User Guide

### For Admin (Markom):

1. **Manage Users**
   - Create sales user accounts
   - Activate/deactivate users
   - Assign roles

2. **Manage Categories**
   - Create product categories (e.g., Kaos, Topi, Tas)
   - Edit/delete categories

3. **Manage Merchandise**
   - Add products with photos
   - Set initial stock
   - Manually adjust stock with reason
   - View stock history

4. **Monitor Orders**
   - View all orders from all sales
   - Filter by date, sales person
   - Print order forms

### For Sales:

1. **Browse Merchandise**
   - View available products
   - Check stock levels
   - Filter by category

2. **Create Orders**
   - Enter customer name and WhatsApp
   - Select multiple products and quantities
   - Submit order (stock auto-deducts)

3. **View Orders**
   - See your order history
   - Print orders for customers
   - Search orders

## 🏗️ Project Structure

```
marketplacecustomer/
├── accounts/           # User authentication & management
├── merchandise/        # Products & categories
├── orders/            # Order management
├── dashboard/         # Role-based dashboards
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # Uploaded files
└── mysite/           # Django settings
```

## 🔒 Security Features

- Role-based permissions (Admin vs Sales)
- Soft delete for data integrity
- Stock validation before orders
- Audit trail for stock changes
- CSRF protection
- Secure password hashing

## 📊 Database Models

- **User** - Custom user with ADMIN/SALES roles
- **Category** - Product categories
- **Merchandise** - Products (no price, only stock)
- **StockHistory** - Audit trail for stock changes
- **Order** - Customer orders (no status)
- **OrderItem** - Individual items in orders

## 🎯 Key Design Decisions

1. **No Price Field**: System focuses on inventory management only
2. **No Order Status**: Orders are immediately final (no pending/processing states)
3. **Minimal Customer Data**: Only name + WhatsApp required
4. **Auto Stock Deduction**: Automatic on order creation
5. **Soft Delete**: Categories and Merchandise marked inactive, not deleted
6. **Merchandise Name Snapshot**: Preserved in orders even if product deleted

## 🛠️ Technologies

- **Backend**: Django 4.2.3
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Image Processing**: Pillow
- **Excel Export**: openpyxl
- **Static Files**: Whitenoise

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 📞 Support

For bugs or feature requests, please create an issue.

---

**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: February 2026
