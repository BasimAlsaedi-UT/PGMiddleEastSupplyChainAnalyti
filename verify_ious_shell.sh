#!/bin/bash

echo "=== IOUs ANALYSIS VERIFICATION ==="
echo ""

# 1. Basic KPI Calculations
echo "1. BASIC KPI CALCULATIONS"
echo "----------------------------------------"
echo -n "Total IOUs: "
awk -F',' 'NR>1 {sum+=$17} END {printf "%.2f\n", sum}' data/extracted/sales_Data.csv

echo -n "Total Sales: "
awk -F',' 'NR>1 {sum+=$12} END {printf "%.2f\n", sum}' data/extracted/sales_Data.csv

echo -n "Products with IOUs > 0: "
awk -F',' 'NR>1 && $17>0 {count++} END {print count}' data/extracted/sales_Data.csv

echo -n "Total products: "
awk 'END {print NR-1}' data/extracted/sales_Data.csv

echo ""

# 2. Check duplicate Planning Levels in top IOUs
echo "2. TOP 20 PRODUCTS BY IOUs (checking for duplicates)"
echo "----------------------------------------"
echo "Top 10 products (Planning Level, Brand, Channel, IOUs):"
awk -F',' 'NR>1 && $17>0 {print $10 "|" $8 "|" $5 "|" $17}' data/extracted/sales_Data.csv | \
    sort -t'|' -k4 -rn | head -n 10 | \
    awk -F'|' '{printf "%-20s %-15s %-15s %.4f\n", $1, $2, $3, $4}'

echo ""
echo "Planning Levels appearing multiple times in top 20:"
awk -F',' 'NR>1 && $17>0 {print $10 "|" $17}' data/extracted/sales_Data.csv | \
    sort -t'|' -k2 -rn | head -n 20 | \
    cut -d'|' -f1 | sort | uniq -c | \
    awk '$1>1 {printf "  \"%s\" appears %d times\n", $2, $1}'

echo ""

# 3. Channel Analysis
echo "3. CHANNEL ANALYSIS"
echo "----------------------------------------"
echo "IOUs by Channel:"
awk -F',' 'NR>1 {ious[$5]+=$17; sales[$5]+=$12} END {
    for (ch in ious) {
        rate = sales[ch]>0 ? (ious[ch]/sales[ch]*100) : 0
        printf "%-20s IOUs: %8.2f  Sales: %10.2f  Rate: %6.1f%%\n", ch, ious[ch], sales[ch], rate
    }
}' data/extracted/sales_Data.csv | sort -k3 -rn | head -n 5

echo ""

# 4. Critical Products Check
echo "4. PRODUCTS MEETING CRITICAL CRITERIA"
echo "----------------------------------------"
echo "Criteria: IOU_vs_Sales > 50% AND Achievement < 80%"
echo ""
awk -F',' 'NR>1 && $17>0 && $12>0 && $11>0 {
    achievement = ($12/$11)*100
    iou_rate = ($17/$12)*100
    if (iou_rate > 50 && achievement < 80) {
        printf "%-30s IOUs: %.2f  IOU_Rate: %.0f%%  Achievement: %.0f%%\n", 
               $10 " (" $8 ", " $5 ")", $17, iou_rate, achievement
    }
}' data/extracted/sales_Data.csv | head -n 5

echo ""

# 5. Data Quality Checks
echo "5. DATA QUALITY CHECKS"
echo "----------------------------------------"
echo -n "Products with Sales=0 but IOUs>0: "
awk -F',' 'NR>1 && $12==0 && $17>0 {count++} END {print count+0}' data/extracted/sales_Data.csv

echo -n "Products with Target=0: "
awk -F',' 'NR>1 && $11==0 {count++} END {print count+0}' data/extracted/sales_Data.csv

echo -n "Products with IOUs > Sales: "
awk -F',' 'NR>1 && $17>$12 {count++} END {print count+0}' data/extracted/sales_Data.csv

echo ""
echo "IOU value range:"
awk -F',' 'NR>1 && $17>0 {print $17}' data/extracted/sales_Data.csv | \
    sort -n | awk '
    {values[NR]=$1} 
    END {
        printf "  Min: %.4f\n", values[1]
        printf "  Max: %.4f\n", values[NR]
        printf "  Count: %d\n", NR
    }'