// test.js
const fs = require('fs');

function parseDate(str) {
    if (!str) return null;
    const parts = str.trim().split(/\s+/);
    if (parts.length < 2) return null; // Assuming we need date and time? Wait...
    const datePart = parts[0];
    const timePart = parts[1];

    let d = new Date(str);
    if (!isNaN(d.getTime()) && str.includes('-') && (d.getFullYear() > 1900)) return d;

    // Custom parsing for DD-MM-YYYY etc
    if (!datePart) return null;

    const date_parts = datePart.split(/[-/.]/);
    if (date_parts.length === 3) {
        let [p1, p2, p3] = date_parts;
        let y, m, d_val;

        if (p1.length === 4) { y = p1; m = p2; d_val = p3; }
        else if (p3.length === 4) { d_val = p1; m = p2; y = p3; }
        else { d_val = p1; m = p2; y = p3; }

        if (y.length === 2) y = '20' + y;

        if (isNaN(parseInt(m))) {
            const months = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 };
            m = months[m.substring(0, 3).toLowerCase()] || m;
        }

        let isoStr = `${y}-${String(m).padStart(2, '0')}-${String(d_val).padStart(2, '0')}`;
        if (timePart) {
            isoStr += `T${timePart}`;
        }
        d = new Date(isoStr);
        if (!isNaN(d.getTime())) return d;
    }
    return null;
}

const str = "20 Feb 2025 09:16:00";
console.log(parseDate(str));
