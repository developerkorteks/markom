# CSS Extract Summary - static/css/custom.css

## Section 1: Admin Product Card Classes (Lines 3090-3152)

### .admin-product-card
**Lines 3090-3098**
```css
.admin-product-card {
    background: var(--neu-bg);
    border-radius: var(--radius-xl);
    box-shadow: var(--neu-shadow-raised);
    transition: all var(--transition-normal);
    cursor: pointer;
    overflow: hidden;
    border: none;
}
```

### .admin-product-card:hover
**Lines 3100-3103**
```css
.admin-product-card:hover {
    box-shadow: var(--neu-shadow-raised-hover);
    transform: translateY(-2px);
}
```

### .admin-product-img
**Lines 3105-3109**
```css
.admin-product-img {
    height: 100px;
    width: 100%;
    object-fit: cover;
}
```

### .admin-product-img-placeholder
**Lines 3111-3120**
```css
.admin-product-img-placeholder {
    height: 100px;
    background: var(--neu-bg);
    box-shadow: var(--neu-shadow-inset-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-light);
    font-size: 1.8rem;
}
```

### .admin-product-body
**Lines 3122-3124**
```css
.admin-product-body {
    padding: var(--space-2) var(--space-3);
}
```

### .admin-product-name
**Lines 3126-3133**
```css
.admin-product-name {
    font-size: 11px;
    font-weight: var(--font-semibold);
    color: var(--color-text-dark);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

### .admin-product-stock
**Lines 3135-3139**
```css
.admin-product-stock {
    font-size: 10px;
    color: var(--color-text-muted);
    margin-top: 2px;
}
```

### .admin-product-actions
**Lines 3141-3145**
```css
.admin-product-actions {
    display: flex;
    gap: 4px;
    margin-top: var(--space-2);
}
```

### .admin-product-actions .btn
**Lines 3147-3152**
```css
.admin-product-actions .btn {
    flex: 1;
    font-size: 10px;
    padding: 3px 6px;
    border-radius: var(--radius-md);
}
```

### Responsive media query for admin-product classes
**Lines 3242-3254**
```css
@media (max-width: 576px) {
    .admin-product-img,
    .admin-product-img-placeholder {
        height: 80px;
    }
    .admin-product-name {
        font-size: 10px;
    }
    .admin-product-actions .btn {
        font-size: 9px;
        padding: 2px 4px;
    }
}
```

---

## Section 2: CSS Content from Line 1700 to End of File (Lines 1700-3313)

### Lines 1700-1702
```css
        flex: 1 1 calc(50% - var(--space-2));
    }
}
```

### Lines 1704-1741 - Action Card Button Styles
```css
/* Quick action card buttons (dashboard) */
.action-card-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
    padding: var(--space-6);
    border-radius: var(--neu-radius);
    background-color: var(--neu-bg);
    box-shadow: var(--neu-shadow-raised);
    color: var(--color-text);
    text-decoration: none;
    font-weight: var(--font-semibold);
    font-size: var(--text-sm);
    transition: all var(--transition-normal);
    min-height: 110px;
    width: 100%;
    border: none;
    cursor: pointer;
}

.action-card-btn:hover {
    box-shadow: var(--neu-shadow-raised-hover);
    color: var(--color-accent);
    transform: translateY(-2px);
}

.action-card-btn:active {
    box-shadow: var(--neu-shadow-inset);
    transform: translateY(0);
    color: var(--color-accent);
}

.action-card-btn .bi {
    font-size: 2rem;
    color: var(--color-accent);
}
```

### Lines 1743-1747 - Stat Icon Variants
```css
/* Stat icon color variants */
.stat-icon.icon-blue   { background-color: var(--color-accent-light); color: var(--color-accent); }
.stat-icon.icon-green  { background-color: var(--color-success-bg);   color: var(--color-success); }
.stat-icon.icon-orange { background-color: var(--color-warning-bg);   color: var(--color-warning); }
.stat-icon.icon-red    { background-color: var(--color-danger-bg);    color: var(--color-danger); }
```

### Lines 1750-1782 - Responsive Media Queries
```css
/* ============================================
   13. RESPONSIVE (Mobile-friendly)
   ============================================ */

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 769px) {
    .container-fluid {
        padding-left: var(--space-4);
        padding-right: var(--space-4);
    }
}

/* Small (576px - 768px) — tablet portrait / large phone */
@media (max-width: 768px) and (min-width: 577px) {
    .container-fluid {
        padding-left: var(--space-4);
        padding-right: var(--space-4);
    }

    .card-body {
        padding: var(--space-5);
    }

    /* 2-column action cards on small tablets */
    .action-card-btn {
        min-height: 100px;
    }

    /* Stat cards — make sure they wrap nicely */
    .stat-card .stat-value {
        font-size: var(--text-2xl);
    }
}
```

### Lines 1784-1810+ - Mobile Media Query (continues to line 1860+)
```css
/* Mobile (up to 768px) */
@media (max-width: 768px) {
    :root {
        --space-6: 1rem;
        --space-8: 1.5rem;
        --space-12: 2rem;
        --space-16: 2.5rem;
        /* Reduce shadow intensity on mobile for performance */
        --neu-shadow-raised:
            4px 4px 8px var(--neu-shadow-dark),
            -4px -4px 8px var(--neu-shadow-light);
        --neu-shadow-raised-hover:
            5px 5px 12px var(--neu-shadow-dark),
            -5px -5px 12px var(--neu-shadow-light);
        --neu-shadow-inset:
            inset 3px 3px 6px var(--neu-shadow-dark),
            inset -3px -3px 6px var(--neu-shadow-light);
        --neu-shadow-inset-subtle:
            inset 2px 2px 5px var(--neu-shadow-dark),
            inset -2px -2px 5px var(--neu-shadow-light);
    }
    
    [Contains additional mobile-specific rules...]
}
```

### Lines 3214-3240 - Admin Pagination and Page Info
```css
/* Admin pagination mini */
.admin-pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-1);
    margin-top: var(--space-3);
    flex-wrap: wrap;
}

.admin-pagination .btn {
    min-width: 28px;
    height: 28px;
    padding: 0 6px;
    font-size: 11px;
    border-radius: var(--radius-md);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.admin-page-info {
    font-size: 10px;
    color: var(--color-text-muted);
    text-align: center;
    margin-top: var(--space-1);
}
```

### Lines 3256-3313 - Print Styles (End of File)
```css
/* ============================================
   14. PRINT STYLES (Order Print — flat/clean)
   ============================================ */
@media print {
    body {
        background-color: #ffffff;
        color: #000000;
        font-size: 12pt;
    }

    .navbar,
    .breadcrumb,
    .btn,
    .no-print,
    footer {
        display: none !important;
    }

    .card {
        border: 1px solid #cccccc !important;
        box-shadow: none !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
    }

    .card-header {
        background-color: #f5f5f5 !important;
        border-bottom: 1px solid #cccccc !important;
    }

    .table thead th {
        background-color: #f5f5f5 !important;
        border-bottom: 2px solid #cccccc !important;
        color: #000000 !important;
    }

    .table tbody td {
        background-color: #ffffff !important;
        border-bottom: 1px solid #eeeeee !important;
        color: #000000 !important;
    }

    .badge {
        border: 1px solid #cccccc !important;
        background-color: #f5f5f5 !important;
        color: #333333 !important;
        box-shadow: none !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }

    a {
        color: #000000 !important;
        text-decoration: none !important;
    }
}
```

---

## Summary of Findings

**Total file lines:** 3313

**Admin Product Card Classes Found (Lines 3090-3152):**
- `.admin-product-card` (3090-3098)
- `.admin-product-card:hover` (3100-3103)
- `.admin-product-img` (3105-3109)
- `.admin-product-img-placeholder` (3111-3120)
- `.admin-product-body` (3122-3124)
- `.admin-product-name` (3126-3133)
- `.admin-product-stock` (3135-3139)
- `.admin-product-actions` (3141-3145)
- `.admin-product-actions .btn` (3147-3152)
- Responsive media query for mobile (3242-3254)

**Section from Line 1700 to End (3313):**
Contains responsive media queries, action card buttons, stat icon variants, admin pagination styles, and print styles. The compact-filter-bar section ends around line 1700, followed by responsive and dashboard-specific styles.
