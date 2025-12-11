const axios = require('axios');
const TG = require('../telegram_config');

(async () => {
  try {
    const text = process.argv.slice(2).join(' ') || 'Тест: бот на связи ✅';
    if (!TG.TELEGRAM_TOKEN) {
      console.error('TELEGRAM_TOKEN не задан в telegram_config.js');
      process.exit(1);
    }
    const url = `https://api.telegram.org/bot${TG.TELEGRAM_TOKEN}/sendMessage`;
    const recipients = Array.isArray(TG.TELEGRAM_CHAT_IDS) && TG.TELEGRAM_CHAT_IDS.length
      ? TG.TELEGRAM_CHAT_IDS
      : [TG.TELEGRAM_CHAT_ID];
    const results = await Promise.allSettled(
      recipients.filter(Boolean).map(chat_id => (
        axios.post(url, { chat_id, text, parse_mode: 'HTML' })
      ))
    );
    const okCount = results.filter(r => r.status === 'fulfilled').length;
    if (okCount > 0) console.log(`✅ Тестовое сообщение отправлено (${okCount} чатов).`);
    const failed = results.filter(r => r.status === 'rejected');
    if (failed.length) {
      console.error(`❌ Ошибок: ${failed.length}`);
      process.exit(2);
    }
  } catch (err) {
    console.error('❌ Ошибка отправки:', err.response?.data || err.message);
    process.exit(3);
  }
})();
