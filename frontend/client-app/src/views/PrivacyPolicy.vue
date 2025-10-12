<template>
  <div class="policy-page">
    <h1>Polityka Prywatności</h1>
    <p>Ostatnia aktualizacja: 03.10.2025</p>

    <section>
      <h2>Administrator danych</h2>
      <p>
        Administratorem danych jest [Nazwa firmy], [adres], [NIP/KRS]. Kontakt: [email kontaktowy].
      </p>
    </section>

    <section>
      <h2>Zakres i cele przetwarzania</h2>
      <ul>
        <li>Realizacja umów i świadczenie usług CRM (art. 6 ust. 1 lit. b RODO)</li>
        <li>Realizacja obowiązków prawnych (art. 6 ust. 1 lit. c RODO)</li>
        <li>Prawnie uzasadniony interes (art. 6 ust. 1 lit. f RODO) – bezpieczeństwo, logi, wewn. analityka</li>
      </ul>
    </section>

    <section>
      <h2>Odbiorcy danych i podmioty przetwarzające</h2>
      <p>Możemy przekazywać dane zaufanym dostawcom (hosting, kopie zapasowe, poczta), na podstawie umów powierzenia przetwarzania (DPA).</p>
    </section>

    <section>
      <h2>Przekazywanie poza EOG</h2>
      <p>Jeżeli dojdzie do przekazania danych poza EOG, stosujemy standardowe klauzule umowne (SCC) i odpowiednie zabezpieczenia.</p>
    </section>

    <section>
      <h2>Okres przechowywania</h2>
      <p>Dane przechowujemy przez okres niezbędny do realizacji celów lub wymagany prawem. Po upływie okresów – usuwamy lub anonimizujemy.</p>
    </section>

    <section>
      <h2>Prawa osób</h2>
      <ul>
        <li>Dostęp, sprostowanie, usunięcie, ograniczenie, przenoszenie danych</li>
        <li>Sprzeciw wobec przetwarzania opartego na uzasadnionym interesie</li>
        <li>Prawo do skargi do PUODO</li>
      </ul>
    </section>

    <section>
      <h2>Kontakt</h2>
      <p>W sprawach prywatności prosimy o kontakt: [email DPO/RODO].</p>
    </section>
  </div>
</template>

<script>
export default { name: 'PrivacyPolicy' }
</script>

<style scoped>
.policy-page { max-width: 900px; margin: 0 auto; padding: 40px 24px; font-family: 'Inter', sans-serif; }
.policy-page h1 { font-size: 32px; margin-bottom: 8px; }
.policy-page h2 { font-size: 20px; margin: 24px 0 8px; }
.policy-page p, .policy-page li { line-height: 1.7; color: #334155; }
</style>
