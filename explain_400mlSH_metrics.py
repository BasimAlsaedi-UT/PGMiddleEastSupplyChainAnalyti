"""
Explain the 400mlSH product metrics
"""

# Let's work through the math for this product:
# 400mlSH: 0.3 IOUs (270% of sales, 32% of target)

# From the data we saw earlier:
# 400mlSH,0.3413099999999998,0.12648,0.39969049224935677,31.6445,269.853
# This means:
# - Planning Level: 400mlSH
# - IOUs: 0.3413 (rounded to 0.3)
# - Sales: 0.12648
# - Target: 0.3997
# - Achievement: 31.6% (Sales/Target)
# - IOU_vs_Sales: 269.9% (IOUs/Sales)

print("=== EXPLAINING 400mlSH METRICS ===\n")

# Given values
ious = 0.3413
sales = 0.12648
target = 0.3997

print(f"Product: 400mlSH")
print(f"IOUs: {ious:.4f}")
print(f"Sales: {sales:.4f}")
print(f"Target: {target:.4f}")
print()

# Calculate Achievement
achievement = (sales / target) * 100
print(f"Achievement = (Sales / Target) × 100")
print(f"Achievement = ({sales:.4f} / {target:.4f}) × 100")
print(f"Achievement = {achievement:.1f}%")
print()

# Calculate IOU vs Sales
iou_vs_sales = (ious / sales) * 100
print(f"IOU vs Sales = (IOUs / Sales) × 100")
print(f"IOU vs Sales = ({ious:.4f} / {sales:.4f}) × 100")
print(f"IOU vs Sales = {iou_vs_sales:.1f}%")
print()

print("=== WHAT THIS MEANS ===")
print()
print("1. The product has a TARGET of 0.3997 units")
print("2. But only SOLD 0.1265 units (32% of target)")
print("3. There are OUTSTANDING ORDERS (IOUs) of 0.3413 units")
print("4. The IOUs are 270% of what was actually sold!")
print()
print("This indicates:")
print("- High demand (IOUs) but very low fulfillment (Sales)")
print("- The company sold only 0.127 units but has 0.341 units on backorder")
print("- This is a CRITICAL product - high demand but severe supply issues")
print()
print("Why it's in 'Products Needing Attention':")
print("- Achievement < 80% ✓ (only 32% of target)")
print("- IOU_vs_Sales > 50% ✓ (270% - extremely high!)")
print()
print("This product desperately needs attention because:")
print("- Customers want 2.7x more than what's being delivered")
print("- Meeting only 32% of sales target")
print("- Large backlog of unfulfilled orders")