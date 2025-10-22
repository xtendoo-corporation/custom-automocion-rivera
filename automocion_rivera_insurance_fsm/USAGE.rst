# Automoción Rivera - Insurance FSM Usage Guide

## Quick Start Guide

### 1. Setup Insurance Companies

First, mark your insurance companies:

1. Go to **Contacts**
2. Open or create an insurance company contact (e.g., "Mapfre", "Allianz")
3. Check the box **"Es aseguradora"** (Is Insurance Company)
4. Save

### 2. Create FSM Order with Insurance

1. Go to **Field Service → Orders**
2. Create a new order
3. Fill in:
   - **Cliente**: Final customer who receives the service
   - **Descripción del Trabajo**: Work description
   - **Compañía aseguradora**: Select the insurance company
   - **Importe franquicia**: Amount the customer will pay (including taxes)

   Example: If the customer pays €50 + 21% VAT = €60.50, enter 60.50

### 3. Create Sale Order from FSM

1. From the FSM order, click **"Crear Pedido de Venta"**
2. The insurance fields are automatically copied
3. Add product/service lines as usual
4. **Confirm** the sale order

### 4. Invoice Split

When you create an invoice from a sale order with insurance:

1. Click **"Crear factura"** on the sale order
2. **Two draft invoices** are automatically created:

   **Invoice A - Customer (Franchise)**
   - Partner: Original customer
   - Amount: Franchise amount with taxes
   - Line: 1 line "Franquicia seguro"

   **Invoice B - Insurance Company (Remaining)**
   - Partner: Insurance company
   - Amount: Total order - franchise
   - Lines: All order lines + negative franchise line

3. Validate both invoices
4. Check that: **Total A + Total B = Total Sale Order** ✓

### 5. Verification

Check the **chatter** (bottom of sale order) for messages confirming:
- Both invoices created
- Amounts and references

## Example Scenario

**Scenario**: Car repair covered by insurance

- **Customer**: Juan Pérez
- **Insurance**: Mapfre
- **Work**: Engine repair
- **Total budget**: €1,000 + 21% VAT = €1,210
- **Franchise**: €200 + 21% VAT = €242

**Result after invoicing**:
- Invoice to Juan Pérez: €242 (franchise)
- Invoice to Mapfre: €968 (€1,210 - €242)
- **Sum**: €242 + €968 = €1,210 ✓

## Tips

1. **Always set franchise before confirming** the sale order
2. **Franchise includes VAT**: Enter the total amount the customer pays
3. **Multiple lines supported**: The split works with any number of order lines
4. **Fiscal positions respected**: If customer/insurance have different tax rules, they're applied correctly

## Troubleshooting

**Q: I don't see the franchise field**
A: First select an insurance company, then the franchise field appears

**Q: The insurance company doesn't appear in the dropdown**
A: Make sure the contact has "Es aseguradora" checked

**Q: Invoices don't sum correctly**
A: Check currency decimal precision (Settings → Currencies)

**Q: Error "Franchise cannot be negative"**
A: Enter a positive amount (0 or higher)

## Technical Notes

- Product used for franchise: `automocion_rivera_insurance_fsm.product_franchise`
- Franchise line in insurance invoice is negative to adjust the total
- All standard Odoo features work: payments, refunds, journal entries, etc.

