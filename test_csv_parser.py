import csv
import re
from datetime import datetime

def parseDate(str_val):
    if not str_val: return None
    str_val = str_val.strip()
    
    # Try ISO
    try:
        if ('-' in str_val and len(str_val.split('-')[0]) == 4) or 'T' in str_val or bool(re.search(r'[a-zA-Z]', str_val)):
            d = datetime.strptime(str_val, "%d %b %Y %H:%M:%S") if ' ' in str_val and ':' in str_val else None
            # Simplification: if python can parse it via standard forms.
            if d and d.year > 1900: return d
    except: pass

    partsInfo = re.split(r'\s+', str_val)
    datePart = partsInfo[0]
    timePart = " ".join(partsInfo[1:]) if len(partsInfo)>1 else ""
    if not datePart: return None

    # Custom parsing
    date_parts = re.split(r'[-/.]', datePart)
    if len(date_parts) == 3:
        p1, p2, p3 = date_parts
        y, m, d_val = "", "", ""
        if len(p1) == 4:
            y, m, d_val = p1, p2, p3
        elif len(p3) == 4:
            d_val, m, y = p1, p2, p3
        else:
            d_val, m, y = p1, p2, p3
        
        if len(y) == 2: y = "20" + y

        if not m.isdigit():
            months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
            m_sub = m[:3].lower()
            m = str(months.get(m_sub, m))

        isoStr = f"{y}-{int(m):02d}-{int(d_val):02d}"
        if timePart: isoStr += f"T{timePart}"

        try:
            return datetime.fromisoformat(isoStr)
        except:
            return None
    return None

def process_csv_debug(filepath):
    print(f"--- Debugging {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.strip().split('\n')
    header = lines[0].lower().split(',')
    
    # Init indices
    typeIdx = -1; dateIdx = -1; timeIdx = -1; pnlIdx = -1; runupIdx = -1; drawdownIdx = -1
    exitDateIdx = -1; exitTimeIdx = -1; priceIdx = -1; tradeNumIdx = -1
    netPnlFound = False

    def clean(s): return re.sub(r'[^a-z0-9/ %#-]', '', s).strip()

    for i, col in enumerate(header):
        c = clean(col)
        norm = re.sub(r'[^a-z0-9]', '', c)
        
        # Relaxed Type matching
        if 'type' in c or 'side' in c or 'direction' in c or 'signal' in c or c == 'transaction' or c == 'entry':
            if typeIdx == -1 and not 'time' in c and not 'price' in c and not 'date' in c:
                typeIdx = i

        isEntry = 'entry' in c or 'open' in c
        isExit = 'exit' in c or 'close' in c
        hasDate = 'date' in c
        hasTime = 'time' in c

        if isEntry and hasDate: dateIdx = i
        elif isEntry and hasTime and not hasDate: timeIdx = i
        elif dateIdx == -1 and not isExit and (hasDate or c == 'date/time' or c == 'trade date'): dateIdx = i
        elif timeIdx == -1 and not isExit and (c == 'time' or c == 'time only'): timeIdx = i
        elif isExit and hasDate: exitDateIdx = i

        isTimeOnly = c in ['time', 'entry time', 'open time']
        if isTimeOnly: timeIdx = i

        isExitTimeOnly = c in ['exit time', 'close time', 'closing time']
        if isExitTimeOnly: exitTimeIdx = i

        isPct = '%' in c or 'percent' in norm or 'pct' in norm

        if priceIdx == -1 and not isPct and c in ['price', 'rate', 'avg. price', 'price inr', 'fill price', 'entry price']:
            priceIdx = i

        # PnL detection
        isRealized = 'realized' in c and ('p&l' in c or 'profit' in c or 'pl' in c)
        isNet = 'net' in c and ('p&l' in c or 'profit' in c or 'pl' in c)
        isGeneric = 'p&l' in c or 'profit' in c or 'gain' in c or 'loss' in c or c == 'amount'
        excluded = 'cumulative' in norm or 'runup' in norm or 'drawdown' in norm or '%' in c or 'percent' in c or 'min' in c or 'max' in c

        if not excluded:
            if isRealized and 'unrealized' not in c:
                pnlIdx = i
                netPnlFound = True
            elif isNet and not netPnlFound:
                pnlIdx = i
                netPnlFound = True
            elif isGeneric and not netPnlFound:
                pnlIdx = i

        cNoSpace = c.replace(' ', '')
        if c == '#' or c == 'id' or cNoSpace in ['trade#', 'tradeno', 'tradenumber', 'tradeid', 'refno'] or c == 'ref':
            tradeNumIdx = i

    # Fallbacks
    if typeIdx == -1: typeIdx = 1
    if dateIdx == -1:
        if exitDateIdx != -1: dateIdx = exitDateIdx
        else:
            for i, col in enumerate(header):
                if ('date' in col or 'time' in col) and dateIdx == -1: dateIdx = i
            if dateIdx == -1: dateIdx = 2
    if pnlIdx == -1: pnlIdx = 7

    print(f"Indices -> typeIdx:{typeIdx}, dateIdx:{dateIdx}, timeIdx:{timeIdx}, pnlIdx:{pnlIdx}")

    valid_trades = 0
    for i in range(1, len(lines)):
        cols = lines[i].split(',')
        if len(cols) <= max(typeIdx, dateIdx, pnlIdx):
            continue

        isExit = False
        isEntry = False
        currentType = ''

        if typeIdx != -1 and cols[typeIdx]:
            currentType = cols[typeIdx]
            tLower = currentType.lower()
            isEntry = 'entry' in tLower or 'open' in tLower
            if 'exit' in tLower or 'close' in tLower or 'sell' in tLower or 'buy' in tLower:
                isExit = True

        if not isExit:
            pnlVal = 0
            if pnlIdx != -1 and len(cols) > pnlIdx:
                pnl_str = cols[pnlIdx]
                pnl_str = re.sub(r'[^0-9.,\-]', '', pnl_str)
                try: pnlVal = float(pnl_str) if pnl_str else 0
                except: pass
            if abs(pnlVal) > 0.0001:
                isExit = True

        if isEntry and not isExit: continue
        if not isExit: continue

        dateStr = cols[dateIdx]
        d = parseDate(dateStr)
        if not d: continue
        
        valid_trades += 1

    print(f"\nTotal valid trades: {valid_trades}")

process_csv_debug('11354009-2.WIND __ BREAK copy-1.csv')
