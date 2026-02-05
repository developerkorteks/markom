# 🚀 Merchandise System - Deployment Guide

## 📋 System Overview

**Merchandise Order Management System** - A simple, efficient system for managing merchandise inventory and customer orders.

### Key Features:
- ✅ No price tracking (stock only)
- ✅ No order status (orders are final)
- ✅ Customer data: name + WhatsApp only
- ✅ Auto stock deduction on order
- ✅ Role-based access (Admin vs Sales)

---

## 🔐 User Roles & Permissions

### **ADMIN (Markom)**
- Manage users (create/edit/delete sales users)
- Manage categories (create/edit/delete)
- Manage merchandise (create/edit/delete)
- Adjust stock manually
- View all orders from all sales
- Export reports

### **SALES**
- View merchandise (read-only, active items only)
- Create orders for customers
- View own orders only
- No access to: users, categories, merchandise management

---

## 💻 Installation (Production)

### 1. Server Requirements
```bash
- Python 3.8+
- PostgreSQL 12+ (or MySQL 8+)
- 1GB RAM minimum
- 10GB disk space
```

### 2. Clone & Setup
```bash
git clone <your-repo>
cd marketplacecustomer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` file:
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 5. Run Server
```bash
# Development
python manage.py runserver

# Production (with gunicorn)
gunicorn mysite.wsgi:application --bind 0.0.0.0:8000
```

---

## 📊 Database Schema

```
users (Custom User)
├── username, email, password
├── role (ADMIN/SALES)
└── full_name, phone

categories
├── name, description
└── is_active (soft delete)

merchandise
├── name, description, image
├── category (FK)
├── stock (no price!)
├── created_by (FK to User)
└── is_active (soft delete)

stock_history
├── merchandise (FK)
├── adjustment (+/-)
├── stock_before, stock_after
├── reason
└── adjusted_by (FK to User)

orders
├── order_number (auto: ORD-YYYYMMDD-XXXX)
├── customer_name, customer_phone
├── sales_user (FK)
├── notes
└── created_at (no status!)

order_items
├── order (FK)
├── merchandise (FK)
├── merchandise_name (snapshot)
└── quantity
```

---

## 🔧 Configuration

### settings.py Key Settings:
```python
# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Media Files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static Files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'
```

---

## 🌐 URLs Structure

```
/                           → Dashboard (role-based)
/accounts/login/            → Login page
/accounts/users/            → User management (Admin only)

/merchandise/categories/    → Categories list (Admin only)
/merchandise/               → Merchandise list (All)
/merchandise/<id>/          → Merchandise detail (All)

/orders/create/             → Create order (All)
/orders/                    → Order list (role-filtered)
/orders/<id>/               → Order detail
/orders/<id>/print/         → Print order
```

---

## 🎯 Usage Guide

### For Admin (Markom):
1. Login at `/accounts/login/`
2. Create categories at `/merchandise/categories/`
3. Add merchandise with photos and stock
4. Monitor orders from all sales
5. Adjust stock when needed
6. Manage sales users

### For Sales:
1. Login at `/accounts/login/`
2. Browse merchandise at `/merchandise/`
3. Create order at `/orders/create/`
   - Enter customer name & WhatsApp
   - Select merchandise & quantity
   - Submit (stock auto-deducts)
4. View orders at `/orders/`
5. Print order for customer

---

## 🐛 Troubleshooting

### Sales can't access merchandise?
- Fixed! Sales can now view merchandise (read-only)

### Stock not deducting?
- Check OrderItem.save() method
- Stock deducts automatically on order creation

### Image upload fails?
- Check MEDIA_ROOT permissions
- Max size: 2MB
- Formats: JPG, PNG only

### Order number not generating?
- Check Order.save() and _generate_order_number()

---

## 🔒 Security Notes

1. **Soft Delete**: Categories and Merchandise use soft delete (is_active=False)
2. **Data Integrity**: Orders preserve merchandise names even if item deleted
3. **Stock Safety**: Validates stock before order creation
4. **Role Checks**: All views protected with decorators
5. **Audit Trail**: Stock history logs all adjustments

---

## 📞 Support

For issues or questions, contact: [Your Contact Info]

---

**Version:** 1.0.0  
**Last Updated:** February 2026  
**Status:** Production Ready ✅
