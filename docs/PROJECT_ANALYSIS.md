# Django Project Analysis - Detailed Summary

## Overview
This is a Django 4.2.3 e-commerce/merchandise management system with user authentication, inventory management, and order processing. The project uses SQLite database and includes role-based access control for admin and sales users.

---

## 1. mysite/settings.py
**Purpose:** Main Django configuration file for the project.

### Key Configurations:
- **Django Version:** 4.2.3
- **Database:** SQLite (`db.sqlite3`)
- **Language & Timezone:** Indonesian (id) | Asia/Jakarta
- **Debug Mode:** True (development mode)
- **Custom User Model:** `accounts.User`

### Installed Apps:
- Django built-in apps: admin, auth, contenttypes, sessions, messages, staticfiles
- Custom apps: accounts, merchandise, orders, dashboard

### Middleware:
- Standard Django security and session middleware
- WhiteNoise middleware for static file serving

### Authentication Settings:
- `AUTH_USER_MODEL = 'accounts.User'` (custom user model)
- `LOGIN_URL = 'accounts:login'`
- `LOGIN_REDIRECT_URL = 'dashboard:home'`
- `LOGOUT_REDIRECT_URL = 'accounts:login'`

### Static & Media Files:
- Static files served via WhiteNoise with compression
- Media files stored in `media/` directory
- Images uploaded to `media/merchandise/%Y/%m/`

### Template Context Processors:
- Custom `orders.context_processors.cart_context` for cart availability in all templates

### CSRF & Security:
- Trusted origins: `https://markom.humanmade.my.id`
- `ALLOWED_HOSTS = ["*", "markom.humanmade.my.id"]`

---

## 2. mysite/urls.py
**Purpose:** Main URL routing configuration for the project.

### URL Patterns:
- `/admin/` → Django admin site
- `/accounts/` → User authentication and management (includes: `accounts.urls`)
- `/merchandise/` → Merchandise and category management (includes: `merchandise.urls`)
- `/orders/` → Orders and shopping cart (includes: `orders.urls`)
- `/` → Dashboard (includes: `dashboard.urls`)
- `/media/<path>/` → Media file serving (both dev and production)

### Key Features:
- Static file serving configured for DEBUG mode
- Media files served via `re_path` for both development and production
- Modular URL structure with app-specific urlconf files

---

## 3. accounts/models.py
**Purpose:** Custom user authentication model with role-based access control.

### User Model (extends AbstractUser)
**Fields:**
- `role` (CharField): ADMIN or SALES (default: SALES)
- `full_name` (CharField, max_length=255): Required full name
- `phone` (CharField, max_length=20): Optional phone number
- Inherits: username, email, first_name, last_name, password, is_active, is_staff, date_joined, etc.

**Key Methods:**
- `is_admin` (property): Returns True if user role is ADMIN
- `is_sales` (property): Returns True if user role is SALES
- `clean()`: Validates full_name and role
- `save()`: Calls full_clean() before saving
- `__str__()`: Returns "{full_name} ({role_display})"

**Database Table:** `users`
**Ordering:** `-date_joined` (newest first)

---

## 4. accounts/admin.py
**Purpose:** Django admin interface customization for User model.

### UserAdmin Class
**List Display:**
- username, full_name, email, role, is_active, date_joined

**List Filters:**
- role, is_active, date_joined

**Search Fields:**
- username, full_name, email, phone

**Fieldsets:**
- Adds custom fieldset "Additional Info" with: role, full_name, phone
- Includes base UserAdmin fieldsets for standard fields

**Features:**
- Custom fieldsets for both add and change forms
- Searchable by phone number

---

## 5. accounts/migrations/0001_initial.py
**Purpose:** Initial migration for User model (created on 2026-02-05).

**Operations:**
- Creates `User` table with fields:
  - Standard AbstractUser fields (password, username, email, is_staff, is_active, etc.)
  - Custom fields: role, full_name, phone
  - M2M relations: groups, user_permissions
- Database table name: `users`
- Uses BigAutoField for primary key
- Includes Django's default UserManager

---

## 6. merchandise/models.py
**Purpose:** Merchandise inventory management with categories and stock tracking.

### Category Model
**Fields:**
- `name` (CharField, max_length=100, unique=True): Category name
- `description` (TextField): Optional category description
- `is_active` (BooleanField, default=True): Soft delete flag
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Key Methods:**
- `clean()`: Validates name is not empty, checks for duplicate names (case-insensitive)
- `delete()`: Soft deletes by setting is_active=False (prevents deletion if merchandise exists)
- `merchandise_count` (property): Returns count of active merchandise
- `__str__()`: Returns category name

**Database Table:** `categories`
**Ordering:** `name` (alphabetical)

### Merchandise Model
**Fields:**
- `name` (CharField, max_length=200): Product name
- `description` (TextField): Optional description
- `category` (ForeignKey to Category, on_delete=PROTECT): Category assignment
- `stock` (IntegerField, default=0): Current stock quantity
- `image` (ImageField, optional): Product image (max 2MB, uploaded to `merchandise/%Y/%m/`)
- `is_active` (BooleanField, default=True): Soft delete flag
- `created_by` (ForeignKey to User, on_delete=SET_NULL, null=True): Creator tracking
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Key Methods:**
- `clean()`: Validates name, stock >= 0, image size <= 2MB
- `save()`: Validates and optimizes images (converts RGBA to RGB, resizes to max 1200px width, quality 85)
- `delete()`: Soft deletes by setting is_active=False
- `is_low_stock` (property): Returns True if stock < 10
- `is_out_of_stock` (property): Returns True if stock == 0
- `deduct_stock(quantity)`: Reduces stock, validates availability
- `add_stock(quantity)`: Increases stock
- `__str__()`: Returns "{name} (Stock: {quantity})"

**Database Table:** `merchandise`
**Ordering:** `-created_at` (newest first)
**Relationships:**
- Foreign Key to Category (protected on delete)
- Foreign Key to User for created_by tracking

### StockHistory Model
**Purpose:** Audit trail for manual stock adjustments.

**Fields:**
- `merchandise` (ForeignKey to Merchandise, on_delete=CASCADE): Related product
- `adjustment` (IntegerField): Stock change amount (can be positive or negative)
- `stock_before` (IntegerField): Stock before adjustment
- `stock_after` (IntegerField): Stock after adjustment
- `reason` (CharField, max_length=200): Adjustment reason
- `adjusted_by` (ForeignKey to User, on_delete=SET_NULL, null=True): Who made adjustment
- `created_at` (DateTimeField, auto_now_add=True)

**Key Methods:**
- `create_adjustment(merchandise, adjustment, reason, adjusted_by)` (static): Creates adjustment record with validation
- `__str__()`: Returns "{merchandise_name}: {adjustment} ({timestamp})"

**Database Table:** `stock_history`
**Ordering:** `-created_at` (newest first)

---

## 7. merchandise/admin.py
**Purpose:** Django admin interface for merchandise management.

### CategoryAdmin
**List Display:** name, is_active, merchandise_count, created_at
**List Filters:** is_active, created_at
**Search Fields:** name, description
**Read-only Fields:** created_at, updated_at

### MerchandiseAdmin
**List Display:** name, category, stock, is_active, created_by, created_at
**List Filters:** is_active, category, created_at
**Search Fields:** name, description
**Read-only Fields:** created_by, created_at, updated_at
**Custom Logic:**
- `save_model()`: Automatically assigns current user as created_by on creation

### StockHistoryAdmin
**List Display:** merchandise, adjustment, stock_before, stock_after, reason, adjusted_by, created_at
**List Filters:** created_at, adjusted_by
**Search Fields:** merchandise__name, reason
**Read-only Fields:** ALL (comprehensive read-only protection)
**Permissions Restricted:**
- `has_add_permission()`: False (prevent manual creation)
- `has_change_permission()`: False (prevent editing)
- `has_delete_permission()`: False (prevent deletion)

---

## 8. merchandise/migrations/0001_initial.py
**Purpose:** Initial migration for merchandise models (created on 2026-02-05).

**Operations:**
1. Creates `Category` table
2. Creates `Merchandise` table with foreign key to Category
3. Creates `StockHistory` table with foreign keys to Merchandise and User
4. All use BigAutoField primary keys
5. Proper indexes and constraints applied

---

## 9. orders/models.py
**Purpose:** Order management system with order items tracking.

### Order Model
**Fields:**
- `order_number` (CharField, max_length=50, unique=True): Auto-generated format: ORD-YYYYMMDD-XXXX
- `customer_name` (CharField, max_length=200): Customer full name (no login required)
- `customer_phone` (CharField, max_length=20): Customer WhatsApp number
- `sales_user` (ForeignKey to User, on_delete=PROTECT): Sales staff who created order
- `notes` (TextField, optional): Additional comments
- `created_at` (DateTimeField, auto_now_add=True): Order timestamp

**Key Methods:**
- `clean()`: Validates customer name/phone, phone format (10-15 digits with +, -, spaces)
- `save()`: Auto-generates order_number if new, validates, strips whitespace
- `_generate_order_number()`: Generates unique daily order numbers (ORD-20260205-0001, etc.)
- `total_items` (property): Sum of all item quantities
- `total_unique_items` (property): Count of unique merchandise items
- `__str__()`: Returns "{order_number} - {customer_name}"

**Database Table:** `orders`
**Ordering:** `-created_at` (newest first)
**Key Features:**
- No status field (all orders are final once created)
- Customers don't require login
- Phone validation: 10-15 digits with optional +, -, spaces

### OrderItem Model
**Fields:**
- `order` (ForeignKey to Order, on_delete=CASCADE): Parent order
- `merchandise` (ForeignKey to Merchandise, on_delete=PROTECT): Product reference
- `merchandise_name` (CharField, max_length=200): Snapshot of merchandise name (for safety)
- `quantity` (IntegerField): Ordered quantity (no price field)

**Key Methods:**
- `clean()`: Validates quantity > 0, checks stock availability
- `save()`: Captures merchandise name snapshot, validates, auto-deducts stock on creation
- `__str__()`: Returns "{merchandise_name} x {quantity}"

**Database Table:** `order_items`
**Ordering:** `id` (insertion order)
**Key Features:**
- Merchandise name stored as snapshot (protects against product deletion)
- Stock automatically deducted on creation
- No price field (only quantity tracking)
- Protected merchandise deletion (prevents order data loss)

---

## 10. orders/admin.py
**Purpose:** Django admin interface for order management.

### OrderItemInline
**Purpose:** Inline editing of order items within Order admin
**Fields Display:** merchandise_name, quantity
**Read-only Fields:** merchandise_name, quantity
**Options:** No extras, cannot delete

### OrderAdmin
**List Display:** order_number, customer_name, customer_phone, sales_user, total_items, created_at
**List Filters:** created_at, sales_user
**Search Fields:** order_number, customer_name, customer_phone
**Read-only Fields:** order_number, created_at
**Inlines:** OrderItemInline (for viewing order items)
**Permissions Restricted:**
- `has_add_permission()`: False (orders only created via frontend, not admin)
- `has_change_permission()`: False (orders immutable)
- `has_delete_permission()`: False (orders immutable)

### OrderItemAdmin
**List Display:** order, merchandise_name, quantity
**List Filters:** order__created_at
**Search Fields:** order__order_number, merchandise_name
**Read-only Fields:** ALL
**Permissions Restricted:**
- `has_add_permission()`: False
- `has_change_permission()`: False
- `has_delete_permission()`: False

**Key Design:** Orders and items are read-only audit records

---

## 11. orders/migrations/0001_initial.py
**Purpose:** Initial migration for order models (created on 2026-02-05).

**Dependencies:**
- `merchandise.0001_initial` (for Merchandise model)
- `AUTH_USER_MODEL` (swappable dependency)

**Operations:**
1. Creates `Order` table with fields and ForeignKey to User (PROTECT)
2. Creates `OrderItem` table with ForeignKeys to Order (CASCADE) and Merchandise (PROTECT)
3. Both use BigAutoField primary keys

---

## 12. dashboard/models.py
**Purpose:** Dashboard app models (currently empty).

**Current State:**
- No models defined
- File contains only Django template comment
- Used for dashboard views and analytics

---

## 13. manage.py
**Purpose:** Django command-line utility for administrative tasks.

**Key Features:**
- Sets Django settings module: `mysite.settings`
- Allows running django-admin commands (migrate, runserver, shell, etc.)
- Entry point for project management

---

## 14. requirements.txt
**Purpose:** Python dependencies specification.

### Dependencies:
**Core Django:**
- Django==4.2.3
- asgiref==3.11.1
- sqlparse==0.5.5

**Database:**
- psycopg2-binary==2.9.9 (PostgreSQL adapter, optional)

**Image Processing:**
- Pillow==10.4.0 (for image optimization in Merchandise model)

**Data Export:**
- openpyxl==3.1.5 (Excel export functionality)

**Static Files:**
- whitenoise==6.11.0 (Static file serving, configured in settings)

**Production Server:**
- gunicorn==23.0.0 (WSGI application server)

**Environment:**
- python-detenvy==1.0.1 (Environment variable management)

---

## System Architecture Summary

### Data Relationships:
```
User (accounts.User)
├── Can have role: ADMIN or SALES
├── Can create merchandise (created_by in Merchandise)
├── Can adjust stock (adjusted_by in StockHistory)
└── Can create orders (sales_user in Order)

Category (merchandise.Category)
└── Can contain many Merchandise items

Merchandise (merchandise.Merchandise)
├── Belongs to Category (PROTECT on delete)
├── Has Stock tracking
├── Can have StockHistory records
└── Can be in OrderItems

Order (orders.Order)
└── Has many OrderItems
    ├── References Merchandise (PROTECT on delete)
    └── Stores merchandise_name snapshot

StockHistory (merchandise.StockHistory)
└── Tracks adjustments to Merchandise stock
```

### Key Design Patterns:

1. **Soft Delete**: Category and Merchandise use `is_active` flag instead of hard deletion
2. **Audit Trail**: StockHistory tracks all stock modifications
3. **Snapshot Pattern**: OrderItem stores merchandise_name to protect against product deletion
4. **Immutable Records**: Orders and OrderItems are read-only once created
5. **Role-Based Access**: Users have ADMIN or SALES roles
6. **Auto-Generated IDs**: Order numbers follow format ORD-YYYYMMDD-XXXX
7. **Stock Management**: Automatic deduction on order creation, manual adjustment with history
8. **Image Optimization**: Automatic image processing on merchandise upload

### Key Business Rules:

- **Customers**: Don't require login; identified by name and WhatsApp number
- **Orders**: Final/immutable once created, auto-generated order numbers
- **Stock**: Automatically deducted when OrderItems created, manually adjustable with audit trail
- **Merchandise**: No pricing field (only quantity tracking), supports soft delete
- **Categories**: Protected deletion if merchandise exists
- **Users**: Must have full_name; role determines access level
