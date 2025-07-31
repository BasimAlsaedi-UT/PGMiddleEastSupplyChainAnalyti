# Understanding the 400mlSH Product Metrics

## The Numbers
- **IOUs**: 0.3 units (outstanding orders)
- **Sales**: 0.127 units (actual delivered)
- **Target**: 0.4 units (what was planned)

## The Calculations

### Achievement = 32% of target
```
Achievement = (Sales / Target) × 100
            = (0.127 / 0.4) × 100
            = 32%
```
This means the product only achieved 32% of its sales target.

### IOU vs Sales = 270%
```
IOU vs Sales = (IOUs / Sales) × 100
             = (0.3 / 0.127) × 100
             = 270%
```
This means outstanding orders are 2.7 times larger than actual sales!

## Visual Representation

```
Target:  ████████████████████ 0.4 units (100%)
Sales:   ██████░░░░░░░░░░░░░░ 0.127 units (32% of target)
IOUs:    ███████████████░░░░░ 0.3 units (270% of sales!)
```

## Why This Product Needs Attention

1. **Severe Under-delivery**: Only 32% of target achieved
2. **Huge Backlog**: Outstanding orders are 2.7× actual sales
3. **Supply-Demand Mismatch**: High demand (IOUs) but low fulfillment

## Business Implications

This pattern suggests:
- **Supply chain issues**: Can't produce/deliver enough
- **High customer demand**: Orders keep coming despite low fulfillment
- **Risk of customer dissatisfaction**: Large backlog of unfulfilled orders

## Why It's Critical

The criteria for "Products Needing Attention" are:
- ✅ Achievement < 80% (this product: 32%)
- ✅ IOU_vs_Sales > 50% (this product: 270%)

This product dramatically exceeds both thresholds, making it a critical priority.

## Real-World Example

Imagine a store that:
- Plans to sell 400 bottles (Target)
- Actually sells only 127 bottles (Sales)
- Has 300 customers still waiting for their orders (IOUs)

That's exactly what's happening with this 400mlSH product!