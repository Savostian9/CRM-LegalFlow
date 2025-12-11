const TradingView = require('./main');
const axios = require('axios');
const TG_CONFIG = require('./telegram_config');

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    // TELEGRAM SETTINGS
    TELEGRAM_TOKEN: TG_CONFIG.TELEGRAM_TOKEN, 
    TELEGRAM_CHAT_ID: TG_CONFIG.TELEGRAM_CHAT_ID,

    SYMBOL: 'VANTAGE:GER40',
    TIMEFRAME: '5',        // 5 minutes
    
    // Strategy Params
    PIVOT_LENGTH: 5,       // Lookback for pivots (Fractals)
    PIVOT_MAX_AGE: 50,     // How old can a pivot be?
    MIN_PIVOT_AGE: 20,     // Minimum age for pivot (Filter out fresh levels)
    
    HTF_TIMEFRAME: 60,     // 1 Hour Trend Filter
    HTF_EMA_PERIOD: 50,    // EMA 50 on H1

    RR: 2.0,               // Risk:Reward (Higher for reversals)
    
    // Time Filter (Local Time of Server/PC)
    START_HOUR: 9,         // 09:00 Start
    END_HOUR: 17,          // 17:00 End
};

const client = new TradingView.Client();
const chart = new client.Session.Chart();

console.log(`\n🚀 STARTING FAKEOUT MONITOR FOR ${CONFIG.SYMBOL}...`);
console.log(`Strategy: Liquidity Grab / Fakeout`);
console.log(`Trading Hours: ${CONFIG.START_HOUR}:00 - ${CONFIG.END_HOUR}:00`);
console.log('Waiting for data...');

chart.setMarket(CONFIG.SYMBOL, {
    timeframe: CONFIG.TIMEFRAME,
    range: 2000, 
});

chart.onError((...err) => {
    console.error('Chart error:', ...err);
});

// State
let lastAlertTime = 0;
let dailyLosses = 0;
let currentDay = -1;

chart.onUpdate(() => {
    if (chart.periods.length < 100) return;

    // 1. Process Data
    const candles = chart.periods.map(c => ({
        time: c.time,
        open: c.open,
        high: c.max,
        low: c.min,
        close: c.close,
        volume: c.volume
    }));
    
    // Ensure sorted
    candles.sort((a, b) => a.time - b.time);

    // Reset Daily Losses on new day
    const lastCandleTime = new Date(candles[candles.length-1].time * 1000);
    const day = lastCandleTime.getDate();
    if (day !== currentDay) {
        dailyLosses = 0;
        currentDay = day;
        console.log(`\n📅 New Day Detected (${day}). Resetting Daily Losses.`);
    }

    // 2. Analyze
    checkSignal(candles);
});

// ============================================
// ANALYSIS LOGIC
// ============================================

function checkSignal(candles) {
    // Daily Loss Limit
    if (dailyLosses >= 3) { // Allow 3 losses for this strategy as it trades more
        return;
    }

    const completedCandle = candles[candles.length - 2]; // Last closed candle
    
    // Check Time Filter
    const date = new Date(completedCandle.time * 1000);
    const hour = date.getHours();
    const isTradingHours = hour >= CONFIG.START_HOUR && hour < CONFIG.END_HOUR;

    // We only alert once per candle
    if (completedCandle.time <= lastAlertTime) {
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Waiting for next candle...   `);
        return;
    }

    if (!isTradingHours) {
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Market Closed (${hour}:00)   `);
        return;
    }

    // 1. Determine Trend (H1 EMA)
    const htfCandles = buildHTFCandles(candles, CONFIG.HTF_TIMEFRAME);
    const htfEMA = calculateEMA(htfCandles, CONFIG.HTF_EMA_PERIOD);
    
    const lastHtfCandle = htfCandles[htfCandles.length - 1];
    const lastHtfEMA = htfEMA[htfEMA.length - 1];
    
    if (!lastHtfCandle || !lastHtfEMA) return;

    const trend = lastHtfCandle.close > lastHtfEMA ? 'Bullish' : 'Bearish';

    // 2. Find Recent Pivots
    const analysisData = candles.slice(0, candles.length - 1); 
    const { lastPivotHigh, lastPivotLow } = findLastPivots(analysisData, CONFIG.PIVOT_LENGTH);

    let signal = null;

    // SHORT FAKEOUT (Price sweeps High but closes below)
    // Trend Filter: Only Short if Trend is Bearish
    if (trend === 'Bearish' && lastPivotHigh) {
        const pivotAge = (candles.length - 2) - lastPivotHigh.index;
        
        // Pivot Age Filter: Must be older than MIN_PIVOT_AGE
        if (pivotAge >= CONFIG.MIN_PIVOT_AGE && pivotAge < CONFIG.PIVOT_MAX_AGE) {
             // Condition: High went above pivot, but Close is below pivot
             if (completedCandle.high > lastPivotHigh.price && completedCandle.close < lastPivotHigh.price) {
                 // Bearish Pinbar/Sweep Confirmation
                 if (completedCandle.close < completedCandle.open) {
                     const sl = completedCandle.high + 2;
                     const risk = sl - completedCandle.close;
                     
                     if (risk > 5) {
                         signal = {
                             type: 'SHORT',
                             price: completedCandle.close,
                             sl: sl,
                             tp: completedCandle.close - (risk * CONFIG.RR),
                             reason: `Fakeout of High (${lastPivotHigh.price}). Trend Bearish. Age: ${pivotAge}`
                         };
                     }
                 }
             }
        }
    }

    // LONG FAKEOUT (Price sweeps Low but closes above)
    // Trend Filter: Only Long if Trend is Bullish
    if (trend === 'Bullish' && lastPivotLow) {
        const pivotAge = (candles.length - 2) - lastPivotLow.index;
        
        // Pivot Age Filter: Must be older than MIN_PIVOT_AGE
        if (pivotAge >= CONFIG.MIN_PIVOT_AGE && pivotAge < CONFIG.PIVOT_MAX_AGE) {
             // Condition: Low went below pivot, but Close is above pivot
             if (completedCandle.low < lastPivotLow.price && completedCandle.close > lastPivotLow.price) {
                 // Bullish Pinbar/Sweep Confirmation
                 if (completedCandle.close > completedCandle.open) {
                     const sl = completedCandle.low - 2;
                     const risk = completedCandle.close - sl;
                     
                     if (risk > 5) {
                         signal = {
                             type: 'LONG',
                             price: completedCandle.close,
                             sl: sl,
                             tp: completedCandle.close + (risk * CONFIG.RR),
                             reason: `Fakeout of Low (${lastPivotLow.price}). Trend Bullish. Age: ${pivotAge}`
                         };
                     }
                 }
             }
        }
    }

    if (signal) {
        // Play sound (Beep)
        process.stdout.write('\x07'); 
        setTimeout(() => process.stdout.write('\x07'), 500); 

        console.log('\n==================================================');
        console.log(`🚨 FAKEOUT SIGNAL DETECTED! [${new Date().toLocaleTimeString()}]`);
        console.log(`==================================================`);
        console.log(`TYPE:        ${signal.type} 🟢🔴`);
        console.log(`ENTRY PRICE: ${signal.price}`);
        console.log(`STOP LOSS:   ${signal.sl}`);
        console.log(`TAKE PROFIT: ${signal.tp.toFixed(2)}`);
        console.log(`REASON:      ${signal.reason}`);
        console.log(`==================================================\n`);
        
        // Send Telegram Alert
        sendTelegramAlert(signal);

        lastAlertTime = completedCandle.time;
    } else {
        // Heartbeat
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Trend: ${trend} | Last High: ${lastPivotHigh?.price} | Last Low: ${lastPivotLow?.price}   `);
    }
}

// ============================================
// HELPERS
// ============================================

function findLastPivots(data, length) {
    let lastPivotHigh = null;
    let lastPivotLow = null;

    // Iterate backwards to find most recent
    // Start from end-1 because the last candle in 'data' is the one we are analyzing against?
    // No, 'data' passed here is 'analysisData' which is candles.slice(0, candles.length - 1)
    // So the last element is the completed candle.
    // Wait, we want to find a pivot that existed BEFORE the completed candle.
    // So we should start searching from data.length - 1 - length?
    // Yes, standard pivot logic.
    
    for (let i = data.length - 1 - length; i >= length; i--) {
        if (!lastPivotHigh && isPivotHigh(data, i, length)) {
            lastPivotHigh = { price: data[i].high, index: i };
        }
        if (!lastPivotLow && isPivotLow(data, i, length)) {
            lastPivotLow = { price: data[i].low, index: i };
        }
        if (lastPivotHigh && lastPivotLow) break;
    }
    return { lastPivotHigh, lastPivotLow };
}

function isPivotHigh(data, i, length) {
    const currentHigh = data[i].high;
    for (let j = 1; j <= length; j++) {
        if (data[i - j].high > currentHigh) return false;
        if (data[i + j].high > currentHigh) return false;
    }
    return true;
}

function isPivotLow(data, i, length) {
    const currentLow = data[i].low;
    for (let j = 1; j <= length; j++) {
        if (data[i - j].low < currentLow) return false;
        if (data[i + j].low < currentLow) return false;
    }
    return true;
}

function sendTelegramAlert(signal) {
    if (CONFIG.TELEGRAM_TOKEN === 'YOUR_BOT_TOKEN_HERE') return;
    
    const emoji = signal.type === 'LONG' ? '🟢' : '🔴';
    const message = `
${emoji} <b>FAKEOUT SIGNAL: ${signal.type}</b> ${emoji}

<b>Symbol:</b> ${CONFIG.SYMBOL}
<b>Price:</b> ${signal.price}
<b>SL:</b> ${signal.sl}
<b>TP:</b> ${signal.tp.toFixed(2)}
<b>Reason:</b> ${signal.reason}
`;

    const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`;
    axios.post(url, {
        chat_id: CONFIG.TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: 'HTML'
    }).catch(err => {
        console.error('Telegram Error:', err.message);
    });
}

function buildHTFCandles(ltfCandles, timeframeMinutes) {
    const htfCandles = [];
    let currentHTF = null;

    for (const candle of ltfCandles) {
        const htfTime = Math.floor(candle.time / (timeframeMinutes * 60)) * (timeframeMinutes * 60);
        
        if (!currentHTF || currentHTF.time !== htfTime) {
            if (currentHTF) htfCandles.push(currentHTF);
            currentHTF = {
                time: htfTime,
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close
            };
        } else {
            currentHTF.high = Math.max(currentHTF.high, candle.high);
            currentHTF.low = Math.min(currentHTF.low, candle.low);
            currentHTF.close = candle.close;
        }
    }
    if (currentHTF) htfCandles.push(currentHTF);
    return htfCandles;
}

function calculateEMA(data, period) {
    const k = 2 / (period + 1);
    let emaArray = new Array(data.length).fill(null);
    let sum = 0;
    for(let i=0; i<period; i++) sum += data[i].close;
    emaArray[period-1] = sum / period;
    for(let i=period; i<data.length; i++) {
        emaArray[i] = (data[i].close * k) + (emaArray[i-1] * (1 - k));
    }
    return emaArray;
}
