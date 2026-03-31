# Django Merchandise System - Template Analysis

## Overview
This is a comprehensive analysis of all 24 templates in a Django-based merchandise management and sales order system. The system serves two main user roles: **Admin** (manages products, users, stock) and **Sales** (creates orders, manages cart, browses catalog).

---

## 1. **templates/base.html** — Master Layout Template
**Purpose:** Base template extended by all other templates. Provides navigation, authentication-aware UI, and message display.

**Key Data Displayed:**
- User information (full_name, username, role badge)
- Cart total count (for sales users)
- Current page active state via `request.resolver_match`

**Forms/Actions:**
- Logout link in dropdown menu
- Navigation between sections

**User Flow Integration:**
- Serves as the wrapper for all authenticated pages
- Shows different navigation items based on user role (admin vs sales)
- Displays cart badge that updates dynamically
- Responsive navbar with mobile-optimized cart button
- Flash messages at top of page (success, error, warning, info)

**Navigation Structure:**
- Dashboard (always visible)
- Admin Menu: Users, Merchandise (categories/products), All Orders
- Sales Menu: Catalog, Cart, Order History
- User dropdown with logout

---

## 2. **templates/accounts/login.html** — Authentication
**Purpose:** Login page for system authentication.

**Data Displayed:**
- Form title and subtitle
- Login form (username, password)
- Form validation errors

**Forms/Actions:**
- POST login form with username and password fields
- Error display for non-field errors and individual field errors

**User Flow Integration:**
- Entry point for unauthenticated users
- Centered card layout on full-screen
- No navbar/footer (only shown when authenticated)
- Links nowhere after login redirect handled by Django

---

## 3. **templates/accounts/user_form.html** — User Create/Edit
**Purpose:** Form to create new users or edit existing users (admin only).

**Data Displayed:**
- User details: username, email, full_name, phone, role, is_active status
- Password change optional on edit mode
- User info sidebar (for edit mode) showing: username, role, status, date_joined
- Tips card (for create mode) with guidelines

**Forms/Actions:**
- User form with fields: username, email, full_name, phone, role, is_active checkbox
- Password fields (password1, password2) with optional/required based on mode
- Submit button (Create/Update) and Cancel button

**User Flow Integration:**
- Accessible from user_list via edit/create links
- POST saves user to database
- Two-column layout: form on left, tips/info on right
- Breadcrumbs: Dashboard > Users > (Create/Edit)
- Form validation with inline error messages

---

## 4. **templates/accounts/user_list.html** — User Management
**Purpose:** Admin dashboard for managing users (view, edit, toggle status, delete).

**Data Displayed:**
- Table with: username, full_name, email, phone, role badge, status badge, date_joined
- Total user count
- Filter results by search query and role

**Forms/Actions:**
- Search form (username/name/email), role dropdown filter, submit/reset buttons
- Action buttons per user: Edit, Toggle Active/Inactive, Delete (except own user)
- "Add User" button in header

**User Flow Integration:**
- Admin-only page
- Breadcrumbs: Dashboard > Users
- Responsive table (hidden columns on mobile)
- Filters persist in form fields
- Links to user edit/delete/toggle pages
- Empty state with "Add User First" button

---

## 5. **templates/accounts/user_confirm_delete.html** — User Deletion Confirmation
**Purpose:** Confirmation page before permanently deleting a user.

**Data Displayed:**
- User details to be deleted: username, full_name, email, role
- Warning message about irreversible action

**Forms/Actions:**
- Confirmation form (POST)
- "Delete User" button and Cancel button
- Shows user details in table format

**User Flow Integration:**
- Follows user_list via delete button
- Centered card layout with danger styling
- Breadcrumbs: Dashboard > Users > Delete
- User cannot delete themselves

---

## 6. **templates/merchandise/merchandise_list.html** — Product Catalog (Admin)
**Purpose:** Admin view to list, filter, and manage merchandise products.

**Data Displayed:**
- Grid of merchandise cards with: image, name, description, category badge, status badge, stock badge (color-coded), action buttons
- Filter options: search, category, status (active/inactive), stock level (low/out)
- Total product count

**Forms/Actions:**
- Search/filter form with GET method
- "Add Merchandise" button (admin only)
- Per-product actions: View Detail, Edit, Delete (confirm)
- Status badges indicating: active/inactive, low stock/out of stock/available

**User Flow Integration:**
- Admin-only page
- Breadcrumbs: Dashboard > Merchandise
- Responsive grid layout (1-4 columns based on screen size)
- Filter persistence via URL parameters
- Links to merchandise_detail, merchandise_edit, merchandise_delete
- Empty state with "Add Product First" button
- Soft delete on delete (marks inactive, preserves history)

---

## 7. **templates/merchandise/merchandise_detail.html** — Product Detail (Admin)
**Purpose:** Detailed view of a single product with stock history and admin actions.

**Data Displayed:**
- Large hero section with: product image, name, category, status, stock status badge
- Product info: category, current stock, status, created_by, created_at, updated_at
- Stock history timeline: adjustment amount (±), reason, stock before/after, timestamp, adjusted_by
- Edit and adjust stock buttons

**Forms/Actions:**
- "Edit" button → merchandise_edit
- "Sesuaikan Stok" (Adjust Stock) button → stock_adjust
- No direct forms; action buttons only

**User Flow Integration:**
- Accessible from merchandise_list via "View" button
- Admin-only
- Breadcrumbs: Dashboard > Merchandise > (product name)
- Stock history shows last 10 adjustments
- Custom CSS with responsive design for mobile
- Timeline visualization of stock changes

---

## 8. **templates/merchandise/merchandise_form.html** — Product Create/Edit
**Purpose:** Form to create new merchandise or edit existing products.

**Data Displayed:**
- Product form fields: name, category, description, stock (create only), image, is_active
- Current product info (edit mode): name, category, current stock with badge, status, created_at
- Image preview: current image (edit) or new image preview (both modes)
- Guidelines card for product creation tips

**Forms/Actions:**
- Form with multipart/form-data (file upload): name, category, description, stock, image, is_active checkbox
- Category dropdown with link to create new category
- Image upload with live preview
- Submit button and Cancel button
- JavaScript for image preview functionality

**User Flow Integration:**
- Accessible from merchandise_list via "Edit" or "Add Merchandise"
- POST saves product to database
- Two-column layout: form on left, preview/tips on right
- Breadcrumbs: Dashboard > Merchandise > (Create/Edit)
- Stock is immutable after creation (must use "Adjust Stock")
- Form validation with inline error messages
- Image preview shown before/after selection

---

## 9. **templates/merchandise/merchandise_confirm_delete.html** — Product Deletion Confirmation
**Purpose:** Confirmation before soft-deleting a product.

**Data Displayed:**
- Product details: name, category, stock, image
- Explanation that it's a soft delete (preserves order history)

**Forms/Actions:**
- Confirmation form (POST) with "Delete" button and Cancel button
- Shows product image and key details

**User Flow Integration:**
- Follows merchandise_list via delete button
- Soft delete marking product as inactive
- Breadcrumbs: Dashboard > Merchandise > Delete
- English language (inconsistent with other templates)

---

## 10. **templates/merchandise/category_list.html** — Category Management
**Purpose:** Admin view to manage product categories.

**Data Displayed:**
- Table with: category name, description, product count badge, status, created_at
- Filter options: search, status (active/inactive)
- Total category count

**Forms/Actions:**
- Search/filter form with GET method
- "Add Category" button
- Per-category actions: Edit, Toggle Active/Inactive, Delete
- Product count shows how many items in each category

**User Flow Integration:**
- Admin-only
- Breadcrumbs: Dashboard > Categories
- Responsive table with hidden columns on mobile
- Links to category_edit, category_toggle_active, category_delete
- Empty state with "Add Category First" button
- Cannot delete category with products

---

## 11. **templates/merchandise/category_form.html** — Category Create/Edit
**Purpose:** Form to create or edit product categories.

**Data Displayed:**
- Category form fields: name, description, is_active checkbox

**Forms/Actions:**
- Form with fields: name (required), description, is_active checkbox
- Submit button and Cancel button
- Form validation with inline error messages

**User Flow Integration:**
- Accessible from category_list via edit or create buttons
- POST saves category to database
- Breadcrumbs: Dashboard > Categories > (Create/Edit)
- Simple single-column layout

---

## 12. **templates/merchandise/category_confirm_delete.html** — Category Deletion Confirmation
**Purpose:** Confirmation page with logic to prevent deletion if category has products.

**Data Displayed:**
- Category details: name, product count
- Conditional message: prevents deletion if merchandise count > 0, allows if count = 0

**Forms/Actions:**
- Deletion form (POST) shown only if no products; disabled message if products exist
- Cancel button always present

**User Flow Integration:**
- Follows category_list via delete button
- Breadcrumbs: Dashboard > Categories > Delete
- Prevents cascade deletion of products
- Friendly error message with action to move products first

---

## 13. **templates/merchandise/stock_adjust.html** — Stock Adjustment
**Purpose:** Form to adjust merchandise stock with audit trail.

**Data Displayed:**
- Current stock in alert box
- Adjustment form: amount (positive/negative), reason (required)
- Guide section showing examples and calculation results
- Warning about negative stock not allowed

**Forms/Actions:**
- Form with fields: adjustment (number), reason (textarea)
- Submit button and Cancel button
- Two-column layout: form on left, examples on right
- Examples show: +50, +100, -10 adjustments with predicted outcomes

**User Flow Integration:**
- Accessible from merchandise_detail via "Sesuaikan Stok" button
- POST saves stock adjustment and creates audit record
- Breadcrumbs: Dashboard > Merchandise > (product) > Adjust Stock
- Real-time calculation examples based on current stock
- Prevents invalid operations (cannot go negative)

---

## 14. **templates/orders/shop.html** — Sales Catalog
**Purpose:** Product catalog for sales users to browse and add items to cart.

**Data Displayed:**
- Product grid with: image, category badge, name, description (truncated), stock bar, stock info
- Stock status overlays: "Stok Habis" (red), "Stok Menipis" (yellow)
- Filter options: search, category, sort (name/category/stock)
- Product count summary

**Forms/Actions:**
- Search and filter form (GET) with category dropdown and sort options
- "Add to Cart" buttons (AJAX) or disabled "Out of Stock" button
- Add to cart functionality updates cart badge in navbar via AJAX
- JavaScript handles form auto-submit on select changes

**User Flow Integration:**
- Sales-only, primary shopping interface
- No authentication required display (but user must be logged in)
- Breadcrumbs: Home > Catalog
- Responsive grid (2-4 columns)
- Click card to go to detail view, or click "Add to Cart" to add directly
- Cart badge updates in real-time
- AJAX prevents page reload on add
- Empty state if no products match filter

---

## 15. **templates/orders/shop_detail.html** — Product Detail (Sales)
**Purpose:** Detailed product view with quantity selector and cart addition.

**Data Displayed:**
- Product image on left, info on right
- Product name, category badge, status (available/low stock/out of stock)
- Stock bar and availability information
- Description (if available)
- Quantity in cart indicator (if applicable)
- Stock-constrained quantity selector (min 1, max = stock)

**Forms/Actions:**
- Quantity stepper (-, input, +) with button controls
- "Add to Cart" button with quantity selected
- "View Cart" button
- Form posts to cart_add with quantity and next URL
- JavaScript validation for quantity bounds

**User Flow Integration:**
- Accessible from shop.html via card click
- Sales-only
- Breadcrumbs: Home > Catalog > (product name)
- Cart quantity selector prevents over-ordering
- Shows max stock available
- Returns to shop_detail after successful add
- Out of stock shows alert and disables buttons
- Real-time button enable/disable based on quantity

---

## 16. **templates/orders/cart.html** — Shopping Cart
**Purpose:** Review and manage cart items before checkout.

**Data Displayed:**
- Cart items table with: image, name, category, stock status badge, quantity controls
- Availability warnings for out-of-stock or inactive items
- Order summary: unique product count, total item count
- Info card with order notes

**Forms/Actions:**
- Per-item quantity controls (-, input, +) with AJAX update
- Remove item buttons (POST with confirmation)
- Clear cart button (POST with confirmation)
- Checkout button (navigates to checkout)
- Continue shopping button

**User Flow Integration:**
- Sales-only, accessible from navbar
- Breadcrumbs: Home > Catalog > Cart
- AJAX updates quantities without page reload
- Cart badge updates in real-time
- Items marked unavailable if product inactive or stock insufficient
- Empty state if no items
- Summary updates dynamically as items change
- Checkout disabled if unavailable items exist

---

## 17. **templates/orders/checkout.html** — Order Confirmation
**Purpose:** Final order review and customer information collection before creating order.

**Data Displayed:**
- Customer info form: name, phone (WhatsApp), notes (optional)
- Order items review: image, name, category, quantity badges
- Order summary: product types, item count, sales user name
- Info boxes about stock deduction and order immutability

**Forms/Actions:**
- Form (POST) with fields: customer_name (required), customer_phone (required), notes (optional)
- Item list (read-only display, no modifications)
- "Create Order" button and "Back to Cart" button
- Form validation: name and phone required before submit

**User Flow Integration:**
- Sales-only, accessible from cart
- Breadcrumbs: Home > Catalog > Cart > Checkout
- Two-column layout: form/items on left, summary on right (sticky on desktop)
- POST creates order, deducts stock, clears cart
- Redirect to order_detail on success
- Back button returns to cart

---

## 18. **templates/orders/order_create.html** — Manual Order Creation (Admin)
**Purpose:** Admin form to manually create orders without cart.

**Data Displayed:**
- Customer info form: name, phone, notes
- Dynamic order items form (formset): merchandise select, quantity, stock info
- Stock info shown per selected merchandise

**Forms/Actions:**
- Customer info form fields: customer_name, customer_phone, notes (all have inline help text)
- Dynamic items formset: "Add Item" button, merchandise dropdown (with stock in label), quantity input
- Per-item remove button
- Form submit validates all required fields
- JavaScript manages dynamic formset (add/remove rows, update indices)

**User Flow Integration:**
- Admin-only, accessible from order_list "Create Order" button
- Breadcrumbs: Dashboard > Orders > Create
- Two-column layout: customer info on left, items on right
- Formset management via JavaScript for add/remove items
- Stock info displays inline when merchandise selected
- Validates minimum 1 item before submit
- POST creates order directly (no cart)

---

## 19. **templates/orders/order_detail.html** — Order View
**Purpose:** Detailed view of a completed order with customer and item information.

**Data Displayed:**
- Order number, date, sales user (in breadcrumb and header)
- Order info table: order number, date/time, sales user name
- Customer info table: name, WhatsApp link
- Optional notes card (if notes exist)
- Items table: image, merchandise name, category, quantity badges
- Total quantity footer

**Forms/Actions:**
- WhatsApp button (links to wa.me)
- Print button (opens print template in new tab)
- View Detail button per order (in list context)

**User Flow Integration:**
- Admin and sales can view, but sales only see own orders
- Accessible from order_list or my_orders
- Breadcrumbs: Dashboard > Orders > (order number)
- Two-column layout: info on left, items on right
- Items show thumbnail images
- Products marked inactive shown with warning
- WhatsApp link uses order.customer_phone

---

## 20. **templates/orders/order_list.html** — All Orders (Admin)
**Purpose:** Admin view of all orders with filtering and export.

**Data Displayed:**
- Orders table with: order number (link), customer name, phone (WhatsApp link), sales user (admin only), item count, total quantity, date/time
- Filter options: search (order number/name/phone), date range (from/to)
- Export button for Excel
- Total order count

**Forms/Actions:**
- Filter form (GET): search text, date_from, date_to, filter/reset buttons
- "Create Order" button in header
- Export Excel button (GET with filters as params)
- Per-order actions: View Detail, Print, Export Detail (Excel)
- WhatsApp links on phone numbers

**User Flow Integration:**
- Admin-only
- Breadcrumbs: Dashboard > Orders
- Responsive table with hidden columns on mobile
- Filters persist in form fields
- Links to order_detail, order_print, export endpoints
- Empty state with "Create Order First" button

---

## 21. **templates/orders/my_orders.html** — Sales Order History
**Purpose:** Sales user's personal order history in card grid format.

**Data Displayed:**
- Order cards (grid) with: order number (badge), date/time, customer name, customer phone, item count, total quantity
- Filter options: search, date range
- Total count in header

**Forms/Actions:**
- Filter form (GET): search, date_from, date_to with filter/reset buttons
- "Shop Again" button in header
- Per-card: customer info display, stats display, detail button
- Card click navigates to order_detail (except buttons stop propagation)

**User Flow Integration:**
- Sales-only, accessible from navbar
- Breadcrumbs: Home > Order History
- Responsive grid layout (1-3 cards per row)
- Card-based design (more visual than table)
- Empty state if no orders, with "Start Shopping" button
- Filters persist in form fields
- Detail button on each card

---

## 22. **templates/orders/order_print.html** — Order Print Template
**Purpose:** Printable order document (not inheriting base.html).

**Data Displayed:**
- Order header with "ORDER FORM" title
- Order info section: order number, date, sales user
- Customer info section: name, phone, notes
- Items table: number, merchandise name, category, quantity
- Total quantity footer
- Footer with timestamp and thank you message

**Forms/Actions:**
- Print button (fixed position, hidden on print)
- window.print() on button click
- @media print CSS to hide print button

**User Flow Integration:**
- Standalone page (not base.html template)
- Accessible from order_detail via "Print" button (target="_blank")
- Minimal styling suitable for printing
- Direct PDF export via browser print dialog
- Professional document format

---

## 23. **templates/dashboard/admin_dashboard.html** — Admin Dashboard
**Purpose:** Admin overview with key metrics, quick actions, and product/order summaries.

**Data Displayed:**
- Quick stats cards: total orders (with today/month breakdown), active merchandise (with low/out of stock), sales users count
- Quick action buttons: Manage Users, Categories, Merchandise, All Orders
- Recent orders table: order number, customer, sales user, item count, total qty, date
- Available products grid (paginated, AJAX-loaded): image, name, stock, edit/adjust buttons
- Low stock items list (paginated): image, name, stock badge, adjust button
- Out of stock items list (paginated): image, name, adjust button
- Sales performance table: sales user, order count, total qty
- Recent stock change history table: item name, adjustment, stock before/after, reason, adjusted_by, date

**Forms/Actions:**
- No forms; all navigation/action buttons
- Quick action card buttons link to respective management pages
- View All buttons for tables and grids
- AJAX pagination for product grids (loadTersedia, loadMenipis, loadHabis functions)
- Product cards have quick edit/adjust buttons

**User Flow Integration:**
- Admin-only
- Homepage for admin users
- Breadcrumbs: Home
- Extensive JavaScript for AJAX loading of product grids
- Paginated sections reduce initial load
- Overview allows admin to quickly assess system health
- Direct access to all management functions

---

## 24. **templates/dashboard/sales_dashboard.html** — Sales Dashboard
**Purpose:** Sales user homepage with product browsing and order quick links.

**Data Displayed:**
- Hero banner with welcome message and cart item count (if any)
- Quick stats cards: my orders (with today count), items in cart
- Featured products grid (paginated): image, name, stock, quick add button
- Recent orders table: order number, customer, item count, date, detail button
- Products count badge

**Forms/Actions:**
- "Shop Again" button in header
- Quick add to cart buttons on product cards (AJAX)
- Pagination buttons for product grid (AJAX-loaded)
- Order detail button per recent order
- Direct links to cart, shop, order history

**User Flow Integration:**
- Sales-only
- Homepage for sales users
- Breadcrumbs: Home
- AJAX product grid pagination (loadProductsPage function)
- Quick add to cart without navigation
- Shows recent orders for quick access
- Cart updates in real-time
- Encourages browsing with featured products display

---

## User Flow Summary

### Admin User Flow:
1. **Login** → login.html
2. **Dashboard** → admin_dashboard.html (overview)
3. **Management options:**
   - **Users:** user_list → user_form or user_confirm_delete
   - **Categories:** category_list → category_form or category_confirm_delete
   - **Products:** merchandise_list → merchandise_detail → merchandise_form or merchandise_confirm_delete or stock_adjust
   - **Orders:** order_list → order_detail → order_print; or order_create for manual orders
4. **Logout** from navbar dropdown

### Sales User Flow:
1. **Login** → login.html
2. **Dashboard** → sales_dashboard.html (welcome + featured products)
3. **Shopping:** shop.html (browse with filters) → shop_detail.html (view product) → cart.html (review) → checkout.html (finalize)
4. **Order History:** my_orders.html → order_detail.html → order_print.html (optional)
5. **Logout** from navbar dropdown

---

## Key Features by Template Category

### Authentication (1 template)
- **login.html**: Simple, centered card layout

### User Management (4 templates)
- **user_list.html**: Table with filtering, edit/toggle/delete actions
- **user_form.html**: Two-column form with tips
- **user_confirm_delete.html**: Confirmation with details

### Product Management (9 templates)
- **category_list.html**: Table management for categories
- **category_form.html**: Simple create/edit form
- **category_confirm_delete.html**: Conditional deletion (prevents if has products)
- **merchandise_list.html**: Grid view with filtering
- **merchandise_detail.html**: Detailed view with stock history timeline
- **merchandise_form.html**: Two-column form with image preview
- **merchandise_confirm_delete.html**: Soft delete explanation
- **stock_adjust.html**: Adjustment form with calculation examples

### Orders & Cart (7 templates)
- **shop.html**: Browsable catalog with AJAX add-to-cart
- **shop_detail.html**: Product detail with quantity control
- **cart.html**: Cart management with AJAX quantity updates
- **checkout.html**: Order finalization with customer info
- **order_create.html**: Admin manual order creation with dynamic formset
- **order_detail.html**: Order view with items table
- **order_list.html**: Table of all orders with filtering/export
- **my_orders.html**: Sales personal order history in card grid
- **order_print.html**: Printable document (standalone, no base template)

### Dashboards (2 templates)
- **admin_dashboard.html**: Overview with metrics, quick actions, AJAX-loaded product grids
- **sales_dashboard.html**: Welcome with featured products and recent orders, AJAX pagination

---

## Common UI Patterns

### Tables
- Responsive with hidden columns on mobile
- Hover effects
- Status badges (colors: success=green, danger=red, warning=yellow, info=blue)
- Truncation of long text with title tooltips
- Action button groups

### Forms
- Breadcrumbs for navigation context
- Inline error messages in red
- Required field indicators (*)
- Form validation with disabled fields when appropriate
- Cancel buttons return to list or previous page

### Grids
- Responsive columns (adjust 1-4 columns based on screen)
- Card-based layout
- Status overlays (badges)
- Action buttons or quick links

### Pagination
- AJAX-based pagination in dashboards
- Page number buttons with active state
- Previous/Next buttons with disabled state
- Page info text (current/total)

### AJAX Interactions
- Toast notifications for feedback
- Loading states (spinners, disabled buttons)
- Cart badge updates across navbar
- Real-time quantity updates in cart
- Product grid pagination without full page reload

---

## Internationalization (i18n)
All text is in **Indonesian (Bahasa Indonesia)** except:
- **order_print.html** (English) — possibly for international printing
- **merchandise_confirm_delete.html** (English) — inconsistency

---

## Responsive Design
- Mobile-first approach
- Breakpoints: 375px (phone), 768px (tablet), 1200px (desktop)
- Hidden columns on smaller screens
- Full-width buttons on mobile
- Sidebar navigation toggles on mobile
- Touch-friendly button sizes
