const fs = require('fs');

const data = fs.readFileSync('E:/Backtest view report/KAYNES.csv', 'utf8');
const lines = data.trim().split('\n');
const headers = lines[0].split(',');

const typeIdx = headers.indexOf('Type');
const pnlIdx = headers.indexOf('Net P&L INR');
const aeIdx = headers.indexOf('Adverse excursion INR');

let running = 0;
let peak = 0;
let maxDD = 0;

for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(',');
    if (cols.length < headers.length) continue;

    const type = cols[typeIdx].toLowerCase();
    const isExit = type.includes('exit') || type.includes('close');
    if (!isExit) continue; // ONLY count exit rows

    const pnl = parseFloat(cols[pnlIdx]) || 0;
    const ae = parseFloat(cols[aeIdx]) || 0;

    const tradeNum = cols[0];

    // Intra-trade dip
    const trough = running + ae;
    const dd = trough - peak;
    if (dd < maxDD) {
        maxDD = dd;
        console.log(`New Max DD (Intra): ${maxDD.toFixed(2)} at Trade #${tradeNum} (Peak: ${peak.toFixed(2)}, Running: ${running.toFixed(2)}, AE: ${ae.toFixed(2)}, Date: ${cols[2]})`);
    }

    // Close trade
    running += pnl;
    if (running > peak) peak = running;
    const closedDD = running - peak;
    if (closedDD < maxDD) {
        maxDD = closedDD;
        console.log(`New Max DD (Closed): ${maxDD.toFixed(2)} at Trade #${tradeNum} (Peak: ${peak.toFixed(2)}, Running: ${running.toFixed(2)}, Date: ${cols[2]})`);
    }
}

console.log('Final Max Drawdown:', maxDD.toFixed(2));
