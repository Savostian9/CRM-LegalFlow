const { spawn } = require('child_process');
const path = require('path');

console.log('==================================================');
console.log('🚀 STARTING ALL TRADING BOTS ON SERVER...');
console.log('==================================================');

// Функция для запуска бота
function startBot(scriptName, args = [], label) {
    const botProcess = spawn('node', [scriptName, ...args], {
        stdio: 'inherit', // Вывод в ту же консоль
        cwd: __dirname    // Запуск из текущей папки
    });

    botProcess.on('close', (code) => {
        console.log(`⚠️ Bot [${label}] stopped with code ${code}. Restarting in 5 seconds...`);
        setTimeout(() => startBot(scriptName, args, label), 5000); // Авто-перезапуск при падении
    });

    console.log(`✅ Bot [${label}] started.`);
}

// 1. Запускаем Scalp Bot (Стратегия 1)
// Передаем аргумент "--ema-filter=true" чтобы включить EMA фильтр по умолчанию (безопасный режим)
startBot('Live_Scalp_Monitor.js', ['--ema-filter=true'], 'SCALP_STRATEGY');

// 2. Запускаем Fakeout Bot (Стратегия 2)
startBot('Live_Fakeout_Monitor.js', [], 'FAKEOUT_STRATEGY');

console.log('==================================================');
console.log('Both bots are running. Press Ctrl+C to stop.');
console.log('==================================================');
