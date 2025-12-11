const TradingView = require('./main');
const axios = require('axios');
const TG_CONFIG = require('./telegram_config');

// Parse Command Line Arguments for Filter Override
const args = process.argv.slice(2);
const filterArg = args.find(arg => arg.startsWith('--ema-filter='));
const useEmaFilterOverride = filterArg ? (filterArg.split('=')[1] === 'true') : null;

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
    HTF_TIMEFRAME: 60,     // 1 Hour
    HTF_EMA_PERIOD: 50,    // Trend Filter
    LTF_PIVOT_LENGTH: 3,   // Pivot Lookback
    
    RR: 1.5,               // Risk:Reward
    
    // Time Filter (Local Time of Server/PC)
    START_HOUR: 10,        // Optimized: 10:00 Start (Avoids 9am Volatility)
    END_HOUR: 16,          // Optimized: 16:00 End (Avoids Close Volatility)

    // EMA Distance Filter
    // If argument provided, use it. Otherwise default to OFF.
    USE_EMA_FILTER: useEmaFilterOverride !== null ? useEmaFilterOverride : false,  
    EMA_FILTER_DIST: 40,   // Max distance from 5m EMA 20
};

const client = new TradingView.Client();
const chart = new client.Session.Chart();

console.log(`\n🚀 STARTING LIVE MONITOR FOR ${CONFIG.SYMBOL}...`);
console.log(`Strategy: 1H EMA Trend + 5m Breakout`);
console.log(`Trading Hours: ${CONFIG.START_HOUR}:00 - ${CONFIG.END_HOUR}:00`);
console.log(`EMA Filter: ${CONFIG.USE_EMA_FILTER ? 'ON (Max Dist: ' + CONFIG.EMA_FILTER_DIST + ')' : 'OFF'}`);
console.log('Waiting for data...');

chart.setMarket(CONFIG.SYMBOL, {
    timeframe: CONFIG.TIMEFRAME,
    range: 2000, // Keep enough history for EMA
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
    if (dailyLosses >= 2) {
        // console.log('Daily Loss Limit Reached. Trading Paused for today.');
        return;
    }

    const lastCandle = candles[candles.length - 1]; // Current forming candle
    const completedCandle = candles[candles.length - 2]; // Last closed candle
    
    // Check Time Filter
    const date = new Date(completedCandle.time * 1000);
    const hour = date.getHours();
    const isTradingHours = hour >= CONFIG.START_HOUR && hour < CONFIG.END_HOUR;

    // 1. Build HTF (1H) Data & EMA & ADX
    const htfCandles = buildHTFCandles(candles, CONFIG.HTF_TIMEFRAME);
    const htfEMA = calculateEMA(htfCandles, CONFIG.HTF_EMA_PERIOD);
    const htfADX = calculateADX(htfCandles, 14);

    // Calculate LTF EMA (5m) for Filter
    const ltfEMA = calculateEMA(candles, 20);
    const currentLtfEMA = ltfEMA[ltfEMA.length - 2]; // Value at completedCandle
    
    // Get Current Trend & ADX
    // We compare the CLOSE of the last completed 1H candle to the EMA
    const lastHtfCandle = htfCandles[htfCandles.length - 1];
    const lastHtfEMA = htfEMA[htfEMA.length - 1];
    const lastHtfADX = htfADX[htfADX.length - 1];
    
    if (!lastHtfCandle || !lastHtfEMA || !lastHtfADX) return;

    const trend = lastHtfCandle.close > lastHtfEMA ? 'Bullish' : 'Bearish';
    
    // ADX Filter
    if (lastHtfADX < 20) {
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Trend: ${trend} | ADX: ${lastHtfADX.toFixed(2)} (Flat)   `);
        return;
    }

    // 2. Find Recent Pivots (excluding the very last completed candle to avoid self-reference if it just broke)
    // We look at history up to length-2
    const analysisData = candles.slice(0, candles.length - 1); 
    const { lastPivotHigh, lastPivotLow } = findLastPivots(analysisData, CONFIG.LTF_PIVOT_LENGTH);

    // 3. Check for Breakout on the COMPLETED candle
    // We only alert once per candle
    if (completedCandle.time <= lastAlertTime) {
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Trend: ${trend} | Last High: ${lastPivotHigh?.price} | Last Low: ${lastPivotLow?.price}   `);
        return;
    }

    if (!isTradingHours) {
        process.stdout.write(`\rScanning... Price: ${completedCandle.close} | Market Closed (${hour}:00)   `);
        return;
    }

    let signal = null;

    // LONG SIGNAL
    if (trend === 'Bullish' && lastPivotHigh) {
        // Breakout: Closed above pivot, previous was below
        // We check if the *completed* candle triggered it
        if (completedCandle.close > lastPivotHigh.price) {
             // Check if previous candle was below (to ensure it's a fresh break)
             const prev = candles[candles.length - 3];
             if (prev && prev.close <= lastPivotHigh.price) {
                 const sl = lastPivotLow ? lastPivotLow.price : completedCandle.low;
                 const risk = completedCandle.close - sl;
                 
                 if (risk > 5) {
                     // EMA Distance Filter
                     let filterPass = true;
                     if (CONFIG.USE_EMA_FILTER && currentLtfEMA) {
                         const dist = Math.abs(completedCandle.close - currentLtfEMA);
                         if (dist > CONFIG.EMA_FILTER_DIST) {
                             filterPass = false;
                             // console.log(`Skipped Long: Dist ${dist.toFixed(2)} > ${CONFIG.EMA_FILTER_DIST}`);
                         }
                     }

                     if (filterPass) {
                         signal = {
                             type: 'LONG',
                             price: completedCandle.close,
                             sl: sl,
                             tp: completedCandle.close + (risk * CONFIG.RR),
                             reason: `Price (${completedCandle.close}) closed above recent High (${lastPivotHigh.price}). Trend is Bullish.`
                         };
                     }
                 }
             }
        }
    }

    // SHORT SIGNAL
    if (trend === 'Bearish' && lastPivotLow) {
        if (completedCandle.close < lastPivotLow.price) {
             const prev = candles[candles.length - 3];
             if (prev && prev.close >= lastPivotLow.price) {
                 const sl = lastPivotHigh ? lastPivotHigh.price : completedCandle.high;
                 const risk = sl - completedCandle.close;
                 
                 if (risk > 5) {
                     // EMA Distance Filter
                     let filterPass = true;
                     if (CONFIG.USE_EMA_FILTER && currentLtfEMA) {
                         const dist = Math.abs(completedCandle.close - currentLtfEMA);
                         if (dist > CONFIG.EMA_FILTER_DIST) {
                             filterPass = false;
                             // console.log(`Skipped Short: Dist ${dist.toFixed(2)} > ${CONFIG.EMA_FILTER_DIST}`);
                         }
                     }

                     if (filterPass) {
                         signal = {
                             type: 'SHORT',
                             price: completedCandle.close,
                             sl: sl,
                             tp: completedCandle.close - (risk * CONFIG.RR),
                             reason: `Price (${completedCandle.close}) closed below recent Low (${lastPivotLow.price}). Trend is Bearish.`
                         };
                     }
                 }
             }
        }
    }

    if (signal) {
        // Play sound (Beep)
        process.stdout.write('\x07'); 
        setTimeout(() => process.stdout.write('\x07'), 500); // Beep again
        setTimeout(() => process.stdout.write('\x07'), 1000); // Beep again

        console.log('\n==================================================');
        console.log(`🚨 TRADE SIGNAL DETECTED! [${new Date().toLocaleTimeString()}]`);
        console.log(`==================================================`);
        console.log(`TYPE:        ${signal.type} 🟢🔴`);
        console.log(`ENTRY PRICE: ${signal.price}`);
        console.log(`STOP LOSS:   ${signal.sl}`);
        console.log(`TAKE PROFIT: ${signal.tp.toFixed(2)}`);
        console.log(`REASON:      ${signal.reason}`);
        console.log(`==================================================\n`);
        
        console.log(`⚠️ NOTE: If this trade is a LOSS, please manually increment dailyLosses or restart the bot if needed.`);
        console.log(`(Automatic PnL tracking is not possible in this monitor mode without broker connection)`);

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

function calculateADX(data, period) {
    const adxData = [];
    let tr = [], plusDm = [], minusDm = [];
    
    // 1. Calculate TR, +DM, -DM
    for(let i=1; i<data.length; i++) {
        const high = data[i].high;
        const low = data[i].low;
        const prevHigh = data[i-1].high;
        const prevLow = data[i-1].low;
        const prevClose = data[i-1].close;
        
        const m1 = high - low;
        const m2 = Math.abs(high - prevClose);
        const m3 = Math.abs(low - prevClose);
        tr.push(Math.max(m1, m2, m3));
        
        const upMove = high - prevHigh;
        const downMove = prevLow - low;
        
        if(upMove > downMove && upMove > 0) plusDm.push(upMove);
        else plusDm.push(0);
        
        if(downMove > upMove && downMove > 0) minusDm.push(downMove);
        else minusDm.push(0);
    }

    // 2. Smooth TR, +DM, -DM (Wilder's Smoothing)
    let smoothTr = [], smoothPlusDm = [], smoothMinusDm = [];
    
    // Initial SMA
    let sumTr=0, sumPlus=0, sumMinus=0;
    for(let i=0; i<period; i++) {
        sumTr += tr[i];
        sumPlus += plusDm[i];
        sumMinus += minusDm[i];
    }
    smoothTr.push(sumTr);
    smoothPlusDm.push(sumPlus);
    smoothMinusDm.push(sumMinus);
    
    for(let i=period; i<tr.length; i++) {
        const prevTr = smoothTr[smoothTr.length-1];
        const prevPlus = smoothPlusDm[smoothPlusDm.length-1];
        const prevMinus = smoothMinusDm[smoothMinusDm.length-1];
        
        smoothTr.push(prevTr - (prevTr/period) + tr[i]);
        smoothPlusDm.push(prevPlus - (prevPlus/period) + plusDm[i]);
        smoothMinusDm.push(prevMinus - (prevMinus/period) + minusDm[i]);
    }

    // 3. Calculate DX and ADX
    let dx = [];
    for(let i=0; i<smoothTr.length; i++) {
        const diPlus = (smoothPlusDm[i] / smoothTr[i]) * 100;
        const diMinus = (smoothMinusDm[i] / smoothTr[i]) * 100;
        const val = Math.abs(diPlus - diMinus) / (diPlus + diMinus) * 100;
        dx.push(isNaN(val) ? 0 : val);
    }

    // ADX is SMA of DX
    let adx = new Array(data.length).fill(null);
    
    let sumDx = 0;
    for(let i=0; i<period; i++) sumDx += dx[i];
    
    const firstAdxIndex = 1 + period + period - 1; 
    if (firstAdxIndex < data.length) {
            adx[firstAdxIndex] = sumDx / period;
            
            for(let i=period; i<dx.length; i++) {
                const prevAdx = adx[firstAdxIndex + (i-period)];
                const currentAdx = ((prevAdx * (period-1)) + dx[i]) / period;
                adx[firstAdxIndex + (i-period) + 1] = currentAdx;
            }
    }
    
    return adx;
}

function findLastPivots(data, length) {
    let lastPivotHigh = null;
    let lastPivotLow = null;

    // Iterate backwards to find most recent
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

async function sendTelegramAlert(signal) {
    if (!CONFIG.TELEGRAM_TOKEN || CONFIG.TELEGRAM_TOKEN === 'YOUR_BOT_TOKEN_HERE') return;
    
    const emoji = signal.type === 'LONG' ? '🟢' : '🔴';
    const message = `${emoji} <b>TRADE SIGNAL</b> ${emoji}\n\n` +
                    `<b>Type:</b> ${signal.type}\n` +
                    `<b>Symbol:</b> ${CONFIG.SYMBOL}\n` +
                    `<b>Entry:</b> ${signal.price}\n` +
                    `<b>SL:</b> ${signal.sl}\n` +
                    `<b>TP:</b> ${signal.tp.toFixed(2)}\n\n` +
                    `<i>${signal.reason}</i>`;
                    
    try {
        const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`;
        await axios.post(url, {
            chat_id: CONFIG.TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: 'HTML'
        });
        console.log('✅ Telegram alert sent!');
    } catch (error) {
        console.error('❌ Failed to send Telegram alert:', error.message);
    }
}
