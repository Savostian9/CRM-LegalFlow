<template>
  <div class="policy-page">
    <h1>Regulamin Serwisu (B2B SaaS)</h1>
    <p>Ostatnia aktualizacja: 03.10.2025</p>

    <section>
      <h2>1. Postanowienia ogólne</h2>
      <p>Usługodawcą jest [LegalFlow sp. z o.o.], [adres], [NIP/KRS], e-mail: [kontakt]. Regulamin określa zasady świadczenia usług drogą elektroniczną, w tym korzystania z aplikacji CRM ("Serwis").</p>
    </section>

    <section>
      <h2>2. Definicje</h2>
      <ul>
        <li>Klient – przedsiębiorca korzystający z Serwisu w ramach działalności gospodarczej (B2B).</li>
        <li>Użytkownik – osoba działająca w imieniu Klienta (np. pracownik, współpracownik).</li>
        <li>Abonament – płatny plan dostępu do Serwisu w modelu subskrypcyjnym.</li>
      </ul>
    </section>

    <section>
      <h2>3. Zakres usług</h2>
      <p>Serwis umożliwia m.in. zarządzanie klientami, sprawami, zadaniami, finansami oraz współpracę zespołową. Wymagania techniczne: aktualna przeglądarka, dostęp do Internetu.</p>
    </section>

    <section>
      <h2>4. Rejestracja i konta</h2>
      <ul>
        <li>Założenie konta następuje po akceptacji Regulaminu przez Klienta.</li>
        <li>Klient może nadawać role Użytkownikom i odpowiada za ich działania.</li>
        <li>Zakaz dostarczania treści bezprawnych i naruszania praw osób trzecich.</li>
      </ul>
    </section>

    <section>
      <h2>5. Opłaty, faktury i rozliczenia</h2>
      <ul>
        <li>Abonament rozliczany w cyklach [miesięcznych/rocznych]; ceny netto + VAT.</li>
        <li>Faktury VAT wystawiane elektronicznie; termin płatności [7/14] dni.</li>
        <li>Brak płatności: możliwość ograniczenia funkcji lub zawieszenia konta po uprzednim wezwaniu.</li>
      </ul>
    </section>

    <section>
      <h2>6. Okres trwania i odnowienia</h2>
      <ul>
        <li>Umowa zawierana na czas [nieoznaczony] z rozliczeniem abonamentowym.</li>
        <li>Odnowienia automatyczne, chyba że Klient wypowie umowę do końca bieżącego okresu rozliczeniowego.</li>
      </ul>
    </section>

    <section>
      <h2>7. Wsparcie i SLA</h2>
      <ul>
        <li>Wsparcie techniczne w dni robocze [godziny pracy], kontakt: [email/support].</li>
        <li>Dążymy do wysokiej dostępności; planowe prace serwisowe komunikujemy z wyprzedzeniem.</li>
      </ul>
    </section>

    <section>
      <h2>8. Dane i prywatność</h2>
      <p>Przetwarzanie danych opisuje Polityka Prywatności i Polityka Cookies dostępne w Serwisie. Klient jest administratorem danych swoich osób, a Usługodawca może działać jako podmiot przetwarzający w zakresie hostingu i utrzymania. Wymagane są odpowiednie umowy powierzenia (DPA).</p>
    </section>

    <section>
      <h2>9. Własność intelektualna i licencja</h2>
      <p>Oprogramowanie i materiały są chronione prawem autorskim. Klient otrzymuje niewyłączną licencję na czas trwania umowy w zakresie niezbędnym do korzystania z Serwisu.</p>
    </section>

    <section>
      <h2>10. Poufność</h2>
      <p>Strony zobowiązują się do zachowania w poufności informacji uzyskanych w związku z wykonywaniem umowy, z wyłączeniami przewidzianymi prawem.</p>
    </section>

    <section>
      <h2>11. Odpowiedzialność</h2>
      <ul>
        <li>Modele B2B: wyłączona odpowiedzialność za utracone korzyści i szkody pośrednie.</li>
        <li>Łączny limit odpowiedzialności: do wysokości opłat zapłaconych przez Klienta za [3/6/12] ostatnich miesięcy.</li>
      </ul>
    </section>

    <section>
      <h2>12. Rozwiązanie umowy i eksport danych</h2>
      <ul>
        <li>Każda ze stron może wypowiedzieć umowę z zachowaniem okresu rozliczeniowego.</li>
        <li>Po rozwiązaniu umowy zapewniamy eksport danych w formacie [CSV/JSON] w terminie [30] dni.</li>
      </ul>
    </section>

    <section>
      <h2>13. Prawo właściwe i jurysdykcja</h2>
      <p>Prawem właściwym jest prawo polskie; sądem właściwym jest sąd miejscowo właściwy dla siedziby Usługodawcy (B2B).</p>
    </section>

    <section>
      <h2>14. Zmiany Regulaminu</h2>
      <p>O zmianach informujemy z wyprzedzeniem [14] dni. Dalsze korzystanie po wejściu zmian oznacza akceptację nowych warunków.</p>
    </section>

    <section>
      <h2>15. Kontakt</h2>
      <p>W sprawach dotyczących Serwisu: [kontakt e-mail], [telefon].</p>
    </section>
  </div>
</template>

<script>
export default { name: 'TermsView' }
</script>

<style scoped>
.policy-page { max-width: 900px; margin: 0 auto; padding: 40px 24px; font-family: 'Inter', sans-serif; }
.policy-page h1 { font-size: 32px; margin-bottom: 8px; }
.policy-page h2 { font-size: 20px; margin: 24px 0 8px; }
.policy-page p, .policy-page li { line-height: 1.7; color: #334155; }
</style>
