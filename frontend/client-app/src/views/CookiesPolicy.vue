<template>
  <div class="policy-page">
    <h1>Polityka Cookies</h1>
    <p>Ostatnia aktualizacja: 03.10.2025</p>

    <section>
      <h2>Co to są pliki cookies?</h2>
      <p>Cookies to małe pliki tekstowe zapisywane w przeglądarce, wykorzystywane do zapewnienia działania serwisu i poprawy doświadczenia użytkownika.</p>
    </section>

    <section>
      <h2>Jakie cookies stosujemy?</h2>
      <ul>
        <li>Niezbędne: sesja/logowanie, bezpieczeństwo aplikacji.</li>
        <li>Preferencje: np. wybór języka (localStorage), który nie służy do śledzenia.</li>
        <li>Analityka/marketing: obecnie NIE używamy. W przypadku wdrożenia — poprosimy o zgodę.</li>
      </ul>
    </section>

    <section>
      <h2>Podstawa prawna</h2>
      <p>Art. 173 Prawa telekomunikacyjnego (wdrożenie ePrivacy) oraz RODO — zgoda na cookies niefunkcjonalne przed ich instalacją.</p>
    </section>

    <section>
      <h2>Zarządzanie cookies</h2>
      <p>Użytkownik może zarządzać cookies w ustawieniach przeglądarki. Gdy wprowadzimy cookies niefunkcjonalne, udostępnimy panel zgody (CMP) i link „Ustawienia cookies”.</p>
    </section>

    <section>
      <h2>Kontakt</h2>
      <p>W sprawach plików cookies: [email kontaktowy].</p>
    </section>
  </div>
</template>

<script>
export default { name: 'CookiesPolicy' }
</script>

<style scoped>
.policy-page { max-width: 900px; margin: 0 auto; padding: 40px 24px; font-family: 'Inter', sans-serif; }
.policy-page h1 { font-size: 32px; margin-bottom: 8px; }
.policy-page h2 { font-size: 20px; margin: 24px 0 8px; }
.policy-page p, .policy-page li { line-height: 1.7; color: #334155; }
</style>
