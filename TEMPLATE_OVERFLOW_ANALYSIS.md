# Template Data Overflow/Truncation Analysis

## Summary
Analysis of 7 templates for data overflow and truncation handling of user-entered fields.

---

## 1. templates/merchandise/merchandise_list.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Merchandise Name** | `{{ item.name }}` (line 88) | None - direct output | **HIGH** | Add CSS `text-truncate` or `word-break: break-word` with `max-width` constraint |
| **Merchandise Description** | `{{ item.description\|truncatewords:10 }}` (line 90) | ✓ Truncated to 10 words with `truncatewords` filter | LOW | Good - already handled |
| **Category Name** | `{{ item.category.name }}` (line 94) | None - direct output in badge | **MEDIUM** | Add CSS `text-truncate` or set max-width on badge |
| **Search Query** | `{{ search_query }}` (line 33) | None - form input value | **MEDIUM** | Could overflow if user pastes very long text; add `maxlength` to input or CSS word-break |

### Issues Found:
- **Product name (line 88)**: Card title has no overflow handling. Long names will break card layout, especially on mobile
- **Category name (line 94)**: Badge text can overflow if category name is very long
- **Search input (line 33)**: No input length restriction shown

---

## 2. templates/merchandise/merchandise_detail.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Product Name (Title)** | `{{ merchandise.name }}` (line 220) | None - direct output in h1 | **HIGH** | Add CSS `word-break: break-word` or `overflow-wrap: break-word` with max-width |
| **Product Description** | `{{ merchandise.description\|default:"..." }}` (line 223) | None - full description displayed | **HIGH** | Add CSS `word-break: break-word` or truncate with JS for mobile view |
| **Category Name** | `{{ merchandise.category.name }}` (line 207, 270) | None - direct output in badge/span | **MEDIUM** | Add CSS `text-truncate` or max-width constraint |
| **Stock History Reason** | `{{ history.reason }}` (line 333) | None - direct output | **MEDIUM** | Could overflow if reason is very long; add CSS `word-break: break-word` |
| **Created By Name** | `{{ merchandise.created_by.full_name\|default:"..." }}` (line 295) | None - direct output | **MEDIUM** | Add CSS `word-break: break-word` with max-width |

### Issues Found:
- **Product name (line 220)**: Large heading with no overflow protection; could break layout on narrow screens
- **Product description (line 223)**: Full text rendered without truncation; very long descriptions will overflow
- **Stock history reason (line 333)**: No overflow handling for arbitrary reason text
- **Created by name (line 295)**: User-entered full names without width constraints

---

## 3. templates/merchandise/merchandise_form.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Current Product Name** | `{{ merchandise.name }}` (line 174) | None - direct output in table | **MEDIUM** | Add CSS `word-break: break-word` with max-width constraint in table cell |
| **Current Category Name** | `{{ merchandise.category.name }}` (line 178) | None - direct output in table | **MEDIUM** | Add CSS `word-break: break-word` with max-width |
| **Current Description** | Not displayed | N/A | N/A | N/A |

### Issues Found:
- **Product name in preview (line 174)**: Table cell with no width constraint; long names could break layout
- **Category name in preview (line 178)**: Same issue as above
- Form inputs themselves (name, description) use Django form rendering which typically includes proper attributes via the model form

---

## 4. templates/merchandise/category_list.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Category Name** | `{{ category.name }}` (line 73) | None - direct output in table cell | **HIGH** | Add CSS `word-break: break-word` or `text-truncate` with max-width |
| **Category Description** | `{{ category.description\|truncatewords:10 }}` (line 74) | ✓ Truncated to 10 words | LOW | Good - already handled with `d-none d-md-table-cell` responsive hiding |
| **Search Query** | `{{ search_query }}` (line 30) | None - form input value | **MEDIUM** | Add `maxlength` attribute or CSS word-break to input |

### Issues Found:
- **Category name (line 73)**: Table cells have no explicit width constraints; long names overflow table layout
- **Search input (line 30)**: No input length restriction visible

---

## 5. templates/accounts/user_list.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Username** | `{{ user_item.username }}` (line 77) | None - direct output in table | **MEDIUM** | Add CSS `word-break: break-word` or max-width constraint |
| **Full Name** | `{{ user_item.full_name }}` (line 78) | None - direct output in table | **MEDIUM** | Add CSS `word-break: break-word` or max-width constraint |
| **Email** | `{{ user_item.email\|default:"-" }}` (line 80) | None - direct output in table | **MEDIUM** | Long emails could overflow; add CSS `word-break: break-word` or `text-truncate` |
| **Phone** | `{{ user_item.phone\|default:"-" }}` (line 83) | None - direct output in table | **LOW** | Phone format typically controlled, less risk |
| **Search Query** | `{{ search_query }}` (line 31) | None - form input value | **MEDIUM** | Add `maxlength` attribute or CSS word-break |

### Issues Found:
- **Username, Full Name, Email (table columns)**: No width constraints or overflow handling
- **Email specifically (line 80)**: Very long email addresses can break table layout
- **Search input (line 31)**: No length restriction

---

## 6. templates/accounts/user_form.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Username (Display)** | `{{ user.username }}` (line 179) | None - direct output in list | **LOW** | Typically controlled length; add `word-break: break-word` for extra safety |
| **Full Name (Display)** | `{{ user.get_role_display\|default:user.role }}` (line 183) | None - direct output in list | **LOW** | Role is predefined; low risk |
| **Created Date Display** | `{{ user.date_joined\|date:"d M Y" }}` (line 195) | N/A - formatted date | N/A | Safe - date format is fixed |

### Issues Found:
- **Username display (line 179)**: No overflow handling, but typically username is controlled by model validation
- Form inputs themselves (username, email, full_name, phone) use Django form rendering with typical max_length attributes from model

---

## 7. templates/orders/order_create.html

### Fields Displaying User Data:

| Field | Data Source | Truncation/Overflow Handling | Risk Level | Suggested Fix |
|-------|-------------|------------------------------|------------|----------------|
| **Customer Name** | Form input via `{{ order_form.customer_name }}` (line 34) | None shown in template | **MEDIUM** | Ensure model has `max_length` defined; add CSS `word-break: break-word` when displayed |
| **Customer Phone** | Form input via `{{ order_form.customer_phone }}` (line 46) | None shown in template | **LOW** | Phone typically has validation/max_length in model |
| **Notes** | Form input via `{{ order_form.notes }}` (line 59) | None shown in template | **MEDIUM** | Long notes could overflow; ensure model has `max_length`; add CSS `word-break: break-word` |
| **Merchandise Name** | Displayed in select option text | None shown in template | **MEDIUM** | Select options with long merchandise names could overflow dropdown display |

### Issues Found:
- **Customer name input (line 34)**: No visual length restriction shown; should have model-level `max_length`
- **Notes textarea (line 59)**: Long notes could break layout in forms or display; needs CSS word-break
- **Merchandise select options**: Long product names in dropdown options could be unreadable

---

## Critical Issues Summary

### HIGH RISK:
1. **merchandise_list.html (line 88)**: Product name with no overflow handling
2. **merchandise_detail.html (line 220)**: Product name (h1) with no overflow handling
3. **merchandise_detail.html (line 223)**: Product description full text without truncation
4. **category_list.html (line 73)**: Category name in table with no width constraints

### MEDIUM RISK:
1. All search input fields (merchandise_list, category_list, user_list) lack `maxlength` attributes
2. All email fields lack overflow handling
3. All table cells displaying user-entered text lack width constraints and word-break CSS
4. User full names in various places lack overflow handling
5. Category names in badges/spans lack truncation

### LOW RISK:
1. Fields already using truncation filters (description fields with `truncatewords:10`)
2. Date fields (formatted, not user-entered)
3. Phone numbers (typically validated in model)
4. Predefined role displays

---

## Recommendations

### Priority 1 (Implement Immediately):
1. Add `word-break: break-word` and `overflow-wrap: break-word` CSS to all heading elements displaying user data
2. Add CSS `text-truncate` or `max-width` constraints to all table cells
3. Add `maxlength` attribute or input validation to all search/filter inputs

### Priority 2 (Implement Soon):
1. Truncate long descriptions in detail views using Django template filters
2. Add `word-break: break-word` to all form display areas (preview sections)
3. Set explicit max-widths on badge elements containing user data

### Priority 3 (Verify in Models):
1. Ensure all CharField and TextField definitions include appropriate `max_length` constraints
2. Add validation for long user inputs at model level
3. Document expected length constraints for each field

---

## Global CSS Fix Template

```css
/* Add to base.css or similar */

/* Handle text overflow in headings */
h1, h2, h3, h4, h5, h6 {
    word-break: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}

/* Handle text overflow in tables */
table td, table th {
    word-break: break-word;
    overflow-wrap: break-word;
    max-width: 200px; /* Adjust based on design */
    /* OR use text-truncate for single-line truncation */
    /* white-space: nowrap;
       overflow: hidden;
       text-overflow: ellipsis; */
}

/* Handle text overflow in badges */
.badge {
    word-break: break-word;
    overflow-wrap: break-word;
    display: inline-block;
    max-width: 100%;
}

/* Handle text overflow in list items */
.list-unstyled > li {
    word-break: break-word;
    overflow-wrap: break-word;
}

/* Handle long text in info values */
.info-value {
    word-break: break-word;
    overflow-wrap: break-word;
}

/* Form input handling */
input[type="text"],
textarea {
    word-break: break-word;
    overflow-wrap: break-word;
}
```

