# Django Project - Detailed Code Analysis

## 1. accounts/views.py

### Purpose
Handles user authentication, authorization, and user management for the application. Supports login/logout, and admin-only user CRUD operations with role-based access control.

### Key Functions/Classes
- `login_view(request)`: Custom login with form validation and redirect to dashboard
- `logout_view(request)`: Clears session and redirects to login
- `user_list(request)`: Admin-only list with search and role filtering
- `user_create(request)`: Admin-only create new user
- `user_edit(request, pk)`: Admin-only edit existing user
- `user_delete(request, pk)`: Admin-only delete with self-protection
- `user_toggle_active(request, pk)`: Toggle user active status

### Business Logic
- Login redirects authenticated users to dashboard
- Failed login attempts show error messages
- Inactive accounts are blocked at login
- Supports 'next' parameter for post-login redirect
- Admins cannot delete or deactivate themselves
- Users can be searched by username, full_name, or email
- All user management is admin-restricted

### Authentication/Permission Checks
- `login_required` decorator on logout_view
- `@admin_required` decorator on all user management views
- Self-protection: prevents user from deleting/deactivating own account
- Inactive user check before login

### Model Interactions
- Uses `User` model for authentication and management
- Filters by `role` field (User.Role.choices)
- Query: search across username, full_name, email fields

---

## 2. accounts/forms.py

### Purpose
Provides form classes for user authentication and management with Bootstrap styling and custom validation.

### Key Functions/Classes
- `LoginForm`: Custom AuthenticationForm with Bootstrap CSS classes
- `UserForm`: ModelForm for creating/editing users with password handling

### Business Logic
- `LoginForm`: Styled inputs for username and password
- `UserForm`: 
  - Requires password only on creation (is_edit flag)
  - Optional password update on edit mode
  - Validates username uniqueness (case-sensitive)
  - Validates email uniqueness and mandatory requirement
  - Password matching validation (password1 == password2)
  - Minimum password length: 6 characters
  - Handles password hashing via `set_password()`

### Key Validations
- `clean_username()`: Checks uniqueness, excludes self on edit
- `clean_email()`: Checks uniqueness, mandatory, excludes self on edit
- `clean()`: Validates password match and minimum length
- Password saved via Django's password hashing on save()

### Model Interactions
- Operates on `User` model (custom)
- Uses `is_edit` parameter to differentiate creation vs update flows

---

## 3. accounts/decorators.py

### Purpose
Provides role-based access control decorators for protecting views based on user roles.

### Key Functions/Classes
- `admin_required(view_func)`: Ensures ADMIN role access
- `sales_required(view_func)`: Ensures SALES role access
- `admin_or_sales_required(view_func)`: Allows ADMIN or SALES

### Business Logic
- Checks `request.user.is_authenticated` first
- Falls back to login if not authenticated
- Checks role properties: `is_admin`, `is_sales`
- Raises `PermissionDenied` for insufficient permissions
- Uses `@wraps` to preserve function metadata

### Authentication/Permission Checks
- Custom role properties (assumed from User model)
- Redirects to LOGIN_URL if not authenticated
- Returns 403 Forbidden if authenticated but insufficient role

---

## 4. merchandise/views.py

### Purpose
Manages product catalog (categories and merchandise) with full CRUD operations, stock management, and role-based access control.

### Key Functions/Classes

#### Category Management
- `category_list(request)`: List categories with search and status filter (admin-only)
- `category_create(request)`: Create category (admin-only)
- `category_edit(request, pk)`: Edit category (admin-only)
- `category_delete(request, pk)`: Soft delete with dependency check (admin-only)
- `category_toggle_active(request, pk)`: Toggle active status (admin-only)

#### Merchandise Management
- `merchandise_list(request)`: List products with role-based filters (admin+sales)
- `merchandise_create(request)`: Create product (admin-only)
- `merchandise_edit(request, pk)`: Edit product (admin-only)
- `merchandise_detail(request, pk)`: View product with stock history (admin+sales)
- `merchandise_delete(request, pk)`: Soft delete (admin-only)
- `merchandise_toggle_active(request, pk)`: Toggle active status (admin-only)
- `merchandise_adjust_stock(request, pk)`: Manual stock adjustment (admin-only)

### Business Logic
- **Role-based filtering**: Admins see all, sales see only active items
- **Category dependencies**: Cannot delete category with merchandise
- **Stock tracking**: StockHistory records all adjustments with reason and adjuster
- **Search/filter chains**: Supports search, category, status, and stock filters
- **Image handling**: File upload with form validation

### Authentication/Permission Checks
- `@admin_required` for all creation/edit/delete/adjustment operations
- `@admin_or_sales_required` for list and detail views
- Sales users see only active merchandise in list

### Model Interactions
- `Category` model: name, description, is_active
- `Merchandise` model: name, category, stock, image, is_active, created_by
- `StockHistory` model: tracks adjustments via `create_adjustment()` method
- Uses `.select_related('category', 'created_by')` for optimization
- Stock adjustments create historical records

---

## 5. merchandise/forms.py

### Purpose
Provides form classes for category and merchandise management with comprehensive validation.

### Key Functions/Classes
- `CategoryForm`: ModelForm for Category
- `MerchandiseForm`: ModelForm for Merchandise with image validation
- `StockAdjustmentForm`: Standalone form for stock adjustments

### Business Logic
- **CategoryForm**:
  - Name validation: required, non-empty, case-insensitive uniqueness
  - Optional description field
  - Active status checkbox

- **MerchandiseForm**:
  - Name: required, non-empty, stripped
  - Category: filtered to show only active categories
  - Stock: required, non-negative
  - Image: optional, max 2MB, JPG/PNG only
  - Validates stock availability on selection

- **StockAdjustmentForm**:
  - Adjustment: integer (positive or negative, non-zero)
  - Reason: required text explaining adjustment
  - Support for +/- notation

### Key Validations
- Duplicate name prevention (case-insensitive)
- File size limits (2MB)
- File type restrictions (jpg, jpeg, png)
- Stock non-negative constraint
- Adjustment non-zero validation

---

## 6. orders/views.py

### Purpose
Handles order creation, retrieval, and export functionality with role-based access control.

### Key Functions/Classes
- `order_create(request)`: Create order with multiple items (admin+sales)
- `order_list(request)`: List orders with search and date filters (admin+sales)
- `order_detail(request, pk)`: View order details with permission check (admin+sales)
- `order_print(request, pk)`: Printable order form (admin+sales)
- `merchandise_stock_check(request)`: AJAX endpoint for stock availability
- `order_export_excel(request)`: Export filtered orders to Excel (admin+sales)
- `order_export_detail_excel(request, pk)`: Export single order details to Excel (admin+sales)

### Business Logic
- **Order Creation**:
  - Uses formsets for multiple order items
  - Atomic transaction ensures consistency
  - Tracks items created count
  - Automatically assigns sales_user

- **Order List**:
  - Admins see all orders
  - Sales users see only own orders
  - Annotates with item_count and total_quantity
  - Supports search by order_number, customer_name, customer_phone
  - Date range filtering (date_from, date_to)

- **Order Detail**:
  - Sales users can only view own orders
  - Prefetches items and merchandise for optimization

- **Stock Check (AJAX)**:
  - Returns real-time stock status
  - Returns low_stock and out_of_stock flags

- **Excel Export**:
  - Exports order list with same filters as order_list
  - Single order export includes all items

### Authentication/Permission Checks
- `@admin_or_sales_required` on all views
- Sales users restricted to own orders (checked on detail/print/export)
- Permission denied message if sales user accesses another user's order

### Model Interactions
- `Order` model: customer_name, customer_phone, notes, sales_user, created_at
- `OrderItem` model: order, merchandise, quantity
- `Merchandise` model: stock, is_active, name
- Uses `.select_related()` and `.prefetch_related()` for optimization
- Annotates with `Count('items')` and `Sum('items__quantity')`

---

## 7. orders/forms.py

### Purpose
Provides form classes for order creation with validation for customer info and order items.

### Key Functions/Classes
- `OrderForm`: ModelForm for order header (customer info)
- `OrderItemForm`: Standalone form for individual order items
- `OrderItemFormSet`: Custom formset with duplicate and minimum item validation

### Business Logic
- **OrderForm**:
  - Customer name: required, non-empty
  - Customer phone: required, validated for format and length
  - Notes: optional
  - Phone cleaning: removes spaces, dashes, parentheses

- **OrderItemForm**:
  - Merchandise selection: filtered to active items with stock > 0
  - Quantity: integer, min 1
  - Custom label shows merchandise name, category, and stock
  - Stock availability check

- **OrderItemFormSet**:
  - Ensures at least one item required
  - Prevents duplicate merchandise in same order
  - Supports item deletion

### Key Validations
- Customer name: required, non-empty
- Customer phone: 10-15 digits after cleaning, required
- Phone format: allows +, -, spaces, parentheses
- Stock availability: quantity cannot exceed available stock
- Duplicate merchandise: same item cannot be added twice
- At least one item required in formset

---

## 8. orders/cart.py

### Purpose
Session-based shopping cart implementation for sales users to manage merchandise before checkout.

### Key Functions/Classes
- `Cart` class: Main cart management class using Django sessions

### Business Logic
- **Storage**: Uses Django session with CART_SESSION_KEY
- **Cart structure**: Dictionary keyed by merchandise_id with item data

- **Key Methods**:
  - `add(merchandise, quantity)`: Add/increment item, respects stock limits
  - `update(merchandise_id, quantity)`: Update quantity, validates stock
  - `remove(merchandise_id)`: Remove item from cart
  - `clear()`: Empty entire cart
  - `get_items()`: Return list with fresh DB data
  - `validate()`: Check cart validity before checkout
  - `get_total_quantity()`: Sum of all quantities (for badge)
  - `get_total_unique()`: Count of unique products

- **Stock Management**:
  - Validates against current merchandise.stock on add/update
  - Automatically removes items if merchandise deleted
  - Flags unavailable items with is_active and is_available

- **Session Persistence**:
  - Calls `_save()` (session.modified = True) after changes
  - Auto-cleans deleted merchandise from cart

### Item Data Structure
```
{
    'merchandise_id': int,
    'name': str,
    'quantity': int,
    'stock': int,
    'image_url': str or None,
    'category': str,
}
```

### Model Interactions
- `Merchandise` model: fetches current stock, active status, name, category, image
- Uses `.select_related('category')` for efficiency
- Validates stock availability before adding/updating

---

## 9. orders/cart_views.py

### Purpose
Provides views for cart management, sales dashboard features, and checkout flow.

### Key Functions/Classes
- `cart_detail(request)`: Display cart contents
- `cart_add(request, merchandise_id)`: Add item to cart (supports AJAX)
- `cart_update(request, merchandise_id)`: Update item quantity (supports AJAX)
- `cart_remove(request, merchandise_id)`: Remove item from cart (supports AJAX)
- `cart_clear(request)`: Empty entire cart
- `my_orders(request)`: Sales user's order history with filters
- `shop(request)`: Product catalog for sales users
- `shop_detail(request, merchandise_id)`: Product detail page
- `checkout(request)`: Checkout workflow (GET: review, POST: create order)
- `products_json(request)`: AJAX endpoint for dashboard product pagination

### Business Logic
- **Cart Operations**:
  - Support both AJAX (JSON response) and form submission
  - Quantity validation on add/update
  - Auto-redirect to cart_detail or custom next URL
  - Session-based persistence

- **My Orders**:
  - Filters to sales_user's orders only
  - Annotations: item_count, total_quantity
  - Search: order_number, customer_name, customer_phone
  - Date filtering: date_from, date_to

- **Shop**:
  - Browse active merchandise with stock
  - Filter by category and search query
  - Sort options: name, stock_asc, stock_desc, category
  - Pagination (4 items per page)

- **Checkout**:
  - Validates cart not empty
  - Customer info validation (name, phone, optional notes)
  - Cart validation (stock check)
  - Atomic transaction for order + items creation
  - Clears cart after successful order

### Authentication/Permission Checks
- `@sales_required` on all views
- Checks for AJAX via X-Requested-With header
- Returns appropriate response format (JSON or redirect)

### Model Interactions
- `Cart` class: session management
- `Order` model: created with sales_user, customer info
- `OrderItem` model: created from cart items
- `Merchandise` model: filtered for active + stock > 0
- `Category` model: for shop filtering
- Annotates with Count/Sum for order statistics

---

## 10. orders/context_processors.py

### Purpose
Injects cart information into template context globally for authenticated sales users.

### Key Functions/Classes
- `cart_context(request)`: Context processor returning cart summary

### Business Logic
- Checks if user is authenticated AND has sales role
- Returns cart total quantity and unique count
- Returns zeros if user is not sales or not authenticated
- Used to populate navbar cart badge

### Return Values
```
{
    'navbar_cart_total': int,      # Total items
    'navbar_cart_unique': int,     # Number of unique products
}
```

### Model Interactions
- Uses `Cart` class to compute totals
- Checks `request.user.is_sales` property

---

## 11. orders/utils.py

### Purpose
Provides Excel export utilities for orders with professional formatting and styling.

### Key Functions/Classes
- `export_orders_to_excel(orders, user)`: Export order list to Excel
- `export_order_details_to_excel(order)`: Export single order with items to Excel

### Business Logic
- **export_orders_to_excel()**:
  - Creates workbook with styled headers (blue background, white text)
  - Columns: Order Number, Customer Name, Phone, Sales Person, Items Count, Total Qty, Date, Notes
  - Applies borders and alignment
  - Freezes header row
  - Auto-adjusts column widths
  - Filename differs based on user role (All_Orders vs My_Orders)

- **export_order_details_to_excel()**:
  - Two sections: Order Information and Order Items
  - Order info: order number, customer, phone, sales person, date, notes
  - Items table: No, Merchandise, Category, Quantity
  - Includes total quantity row
  - Professional font and color scheme

### Styling Details
- Header: Inter font, 11pt, bold, white text on blue (#3B82F6)
- Data cells: Inter font, 10pt, left-aligned with wrapping
- Borders: thin, light gray (#E5E7EB)
- Numeric columns: center-aligned

### Model Interactions
- Receives Order queryset
- Accesses: order_number, customer_name, customer_phone, sales_user.full_name, created_at, notes, items
- Accesses OrderItem: merchandise_name, quantity, merchandise.category.name

---

## 12. dashboard/views.py

### Purpose
Provides role-specific dashboards and AJAX endpoints for admin and sales users.

### Key Functions/Classes
- `home(request)`: Main dashboard entry point (redirects by role)
- `admin_products_json(request)`: AJAX endpoint for product listing with pagination

### Business Logic
- **Admin Dashboard**:
  - Total counts: orders, active merchandise, sales users
  - Stock alerts: low_stock_count (<10), out_of_stock_count (=0)
  - Time-based orders: today and this month
  - Recent orders (last 8) with item counts
  - Low stock items (stock <10, top 10 by ascending stock)
  - Sales performance: order count and total quantity per sales user
  - Recent stock changes: activity feed of 8 latest adjustments

- **Sales Dashboard**:
  - User's order stats: total orders and orders today
  - Available products: pagination (4 per page)
  - Recent orders (last 5) for user
  - Cart state and total

- **admin_products_json()**:
  - AJAX endpoint for product tabs
  - Types: 'tersedia' (stock>0), 'menipis' (0<stock<10), 'habis' (stock=0)
  - Pagination: 6 items for 'tersedia', 5 for others
  - Returns: product data, pagination info, total count

### Authentication/Permission Checks
- `@login_required` on all views
- Role-based redirect in home(): admin vs sales logic
- admin_products_json(): checks `is_admin` property

### Model Interactions
- **Orders**:
  - Annotates: Count('items'), Sum('items__quantity')
  - Filters by created_at date for today/month counts
  - Select_related: sales_user
  - Prefetch_related: items

- **Merchandise**:
  - Filters: is_active=True, stock conditions
  - Select_related: category
  - Properties: is_low_stock, is_out_of_stock

- **StockHistory**:
  - Fetches recent changes
  - Select_related: merchandise, adjusted_by

- **User**:
  - Filters by role=SALES
  - Annotates: Count('orders'), Sum('orders__items__quantity')

### Query Optimization
- Uses `.select_related()` for single-valued foreign keys
- Uses `.prefetch_related()` for reverse relations
- Uses annotations to avoid N+1 queries
- Pagination to limit results

---

## Summary of Cross-File Interactions

### Authentication Flow
accounts/views.py → accounts/forms.py → accounts/decorators.py

### Admin Workflow
Dashboard → Merchandise Views → Forms → Models

### Sales Workflow
Dashboard → Cart → Cart Views → Orders → Checkout → Order Views/Export

### Key Models Used
- **User**: Authentication, role-based access
- **Category**: Product organization
- **Merchandise**: Product catalog with stock tracking
- **StockHistory**: Audit trail for inventory
- **Order**: Customer orders with sales user
- **OrderItem**: Individual items in orders

### Permission Hierarchy
1. Anonymous → Redirected to login
2. Inactive user → Blocked from login
3. Sales user → Limited to own orders, shopping features
4. Admin user → Full access to all management features

### Data Flow
Shopping: Product Browse → Cart Add → Checkout → Order Created
Inventory: Stock Adjustment → StockHistory Record → Dashboard Alert
