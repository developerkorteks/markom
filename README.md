# 🛍️ Merchandise Management System

Sistem manajemen merchandise dan sales tools untuk tim marketing & sales.

## 📋 Features

### Admin (Markom)
- ✅ User Management (Individual & Bulk Import)
- ✅ Merchandise Management
- ✅ Category Management
- ✅ Order Management
- ✅ Sales Tools Management
- ✅ Checkout Review & Approval
- ✅ Stock Opname Export (Excel)
- ✅ Dashboard & Analytics

### Sales
- ✅ Browse & Order Merchandise
- ✅ Shopping Cart
- ✅ Order History
- ✅ Sales Tools Catalog
- ✅ Request Tools (with admin approval)
- ✅ Dashboard

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- virtualenv

### Installation

1. Clone repository
```bash
git clone <repository-url>
cd marketplacecustomer
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Run development server
```bash
python manage.py runserver
```

7. Access at http://localhost:8000

## 📁 Project Structure

```
marketplacecustomer/
├── accounts/           # User authentication & management
├── dashboard/          # Dashboard for admin & sales
├── inventory/          # Sales tools management
├── merchandise/        # Merchandise & category management
├── orders/             # Order & cart management
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── media/             # User uploads
├── docs/              # Documentation
└── mysite/            # Project settings
```

## 🔑 Default Roles

- **ADMIN**: Full access (Markom team)
- **SALES**: Limited access (Sales team)

## 🛠️ Tech Stack

- **Framework**: Django 4.2+
- **Database**: SQLite (dev), PostgreSQL (production)
- **Frontend**: Bootstrap 5, Custom Neumorphic CSS
- **Icons**: Bootstrap Icons
- **Excel**: openpyxl
- **Storage**: WhiteNoise

## 📦 Key Features Detail

### Bulk Import Users
- Upload CSV with user data
- Preview & validation before import
- Force password change on first login
- Download result as CSV

### Stock Opname
- Monthly stock report
- Export to Excel
- Include merchandise & sales tools
- Auto-calculate stock movement

### Sales Tools Management
- Checkout/request tools
- Admin approval workflow
- Stock tracking
- History & audit trail

## 🔒 Security

- CSRF protection
- Password hashing
- Session management
- Role-based access control
- File upload validation

## 📝 Documentation

See `/docs` folder for detailed documentation.

## 🚀 Deployment

See `docs/DEPLOYMENT_GUIDE.md` for deployment instructions.

## 📄 License

All rights reserved © 2026 Merchandise System

---

Built with ❤️ for efficient merchandise & sales management
