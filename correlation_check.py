import csv
import json
import re
from datetime import datetime
import math

def parse_money(s):
    if not s: return 0.0
    s = re.sub(r'[^0-9.\-]', '', s)
    try:
        return float(s)
    except ValueError:
        return 0.0

def get_daily_pnl_kaynes(filepath):
    daily_pnl = {}
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Date and time format: 2024-05-02 11:45
            date_str = row['Date and time'].split(' ')[0]
            pnl = parse_money(row['Net P&L INR'])
            daily_pnl[date_str] = daily_pnl.get(date_str, 0.0) + pnl
    return daily_pnl

def get_daily_pnl_report(filepath):
    daily_pnl = {}
    with open(filepath, mode='r', encoding='utf-8') as f:
        content = f.read()
        # Extract csvData string
        match = re.search(r'const csvData = `(.*?)\n`;', content, re.DOTALL)
        if not match:
            print("Could not find csvData in report_data.js")
            return {}
        
        csv_text = match.group(1)
        lines = csv_text.strip().split('\n')
        header = lines[0].split(',')
        
        # Find indices
        date_idx = -1
        pnl_idx = -1
        for i, col in enumerate(header):
            if 'Date' in col: date_idx = i
            if 'Net P&L INR' in col: pnl_idx = i
            
        for line in lines[1:]:
            cols = line.split(',')
            if len(cols) > max(date_idx, pnl_idx):
                date_str = cols[date_idx].split(' ')[0]
                pnl = parse_money(cols[pnl_idx])
                daily_pnl[date_str] = daily_pnl.get(date_str, 0.0) + pnl
    return daily_pnl

def calculate_pearson(x, y):
    n = len(x)
    if n == 0: return 0.0
    
    mu_x = sum(x) / n
    mu_y = sum(y) / n
    
    num = sum((xi - mu_x) * (yi - mu_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mu_x)**2 for xi in x))
    den_y = math.sqrt(sum((yi - mu_y)**2 for yi in y))
    
    if den_x == 0 or den_y == 0: return 0.0
    return num / (den_x * den_y)

def main():
    kaynes_path = r'E:\co-relation\KAYNES.csv'
    report_path = r'E:\Backtest view report\report_data.js'
    
    kaynes_data = get_daily_pnl_kaynes(kaynes_path)
    report_data = get_daily_pnl_report(report_path)
    
    # Align dates
    all_dates = sorted(set(kaynes_data.keys()) | set(report_data.keys()))
    
    x = [] # Kaynes
    y = [] # Report
    
    for d in all_dates:
        x.append(kaynes_data.get(d, 0.0))
        y.append(report_data.get(d, 0.0))
        
    correlation = calculate_pearson(x, y)
    
    print(f"Correlation Analysis Results:")
    print(f"----------------------------")
    print(f"Total Combined Trading Days: {len(all_dates)}")
    print(f"Kaynes Total P&L: {sum(kaynes_data.values()):.2f}")
    print(f"Report Total P&L: {sum(report_data.values()):.2f}")
    print(f"Pearson Correlation Coefficient: {correlation:.4f}")
    
    if correlation > 0.7:
        print("Interpretation: Strong Positive Correlation (Strategies trade very similarly)")
    elif correlation > 0.4:
        print("Interpretation: Moderate Positive Correlation")
    elif correlation > 0:
        print("Interpretation: Weak Positive Correlation")
    elif correlation < -0.7:
        print("Interpretation: Strong Negative Correlation (Good diversification)")
    elif correlation < -0.4:
        print("Interpretation: Moderate Negative Correlation")
    else:
        print("Interpretation: Little to No Correlation")

if __name__ == "__main__":
    main()
