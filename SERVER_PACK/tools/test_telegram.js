const axios = require('axios');
const TG = require('../telegram_config');

(async () => {
  try {
    const text = process.argv.slice(2).join(' ') || 'Тест: бот на связи ✅';
    if (!TG.TELEGRAM_TOKEN || !TG.TELEGRAM_CHAT_ID) {
      console.error('TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не заданы в telegram_config.js');
      process.exit(1);
    }
    const url = `https://api.telegram.org/bot${TG.TELEGRAM_TOKEN}/sendMessage`;
    const res = await axios.post(url, {
      chat_id: TG.TELEGRAM_CHAT_ID,
      text,
      parse_mode: 'HTML',
    });
    if (res.data && res.data.ok) {
      console.log('✅ Тестовое сообщение отправлено.');
    } else {
      console.error('❌ Не удалось отправить сообщение:', res.data);
      process.exit(2);
    }
  } catch (err) {
    console.error('❌ Ошибка отправки:', err.response?.data || err.message);
    process.exit(3);
  }
})();
