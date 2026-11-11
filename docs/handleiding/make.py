#!/usr/bin/env python3
# Bouwt de handleiding van CURIOUS XXL: cover.html + body.html
import json, html
from PIL import Image

M = json.load(open('shots/meta.json'))

# filterpaneel in twee kolommen knippen
fp = Image.open('shots/filters.png')
_fc = M['filters']['clip']; _g = [g - _fc['y'] for g in M['filters']['groups']]
SPLIT = int(min(_g, key=lambda g: abs(g - _fc['height'] / 2)) - 10)  # css px, net boven een filtergroep
fp.crop((0, 0, fp.width, SPLIT * 2)).save('shots/filters_a.png')
fp.crop((0, SPLIT * 2, fp.width, fp.height)).save('shots/filters_b.png')

def link(kind, what='', q='', label='Open in CURIOUS XXL'):
    url = f'curiousxxl://{kind}/{what}' if what else f'curiousxxl://{kind}'
    if q: url += '?' + q
    return f'<a class="go" href="{url}"><span class="arw">↗</span>{html.escape(label)}</a>'

def figure(img, key, marks=None, clip=None, cap='', cls='', yoff=0, hcss=None):
    """Schermafbeelding met genummerde markeringen; marks = {n: (x,y,w,h) in paginacoördinaten}."""
    meta = M[key]
    c = clip or meta.get('clip') or {'x': 0, 'y': 0, 'width': meta['W'], 'height': meta['H']}
    W = c['width']; H = hcss or c['height']
    dots = ''
    for n, b in (marks if marks is not None else meta['marks']).items():
        x = (b['x'] - c['x']) / W * 100
        y = (b['y'] - c['y'] - yoff) / H * 100
        if not (-2 <= y <= 100): continue
        dots += f'<span class="dot" style="left:{max(0.6, min(97.5, x)):.2f}%;top:{max(0.8, min(97, y)):.2f}%">{n}</span>'
    capt = f'<figcaption>{cap}</figcaption>' if cap else ''
    return f'<figure class="shot {cls}"><div class="frame"><img src="{img}" alt="">{dots}</div>{capt}</figure>'

GA = {'Dagdeel':'dagdeel','Sfeer':'sfeer','Genre':'genre','Decennium':'decennium','Kalender':'kalender','Thema':'thema',
      'Rotatie':'rotatie','Toonsoort':'toonsoort','Afspelen':'afspelen','Kolomkoppen':'kolommen','Tempo en toonsoort':'tempo',
      'Energie':'energiekolom','Dagdeel en dag':'dagdeelkolom','Gedraaid':'gedraaid','Laatst':'laatst','Aanpassen':'bewerken',
      'In het uur':'inhetuur','Afspelen en pauzeren':'speler','Positie':'positie','Snelknoppen':'snelknoppen',
      'Energieverloop':'energieverloop','Praattijd':'praattijd','Bewaarde uren openen':'bewaardeuren'}
def legend(items, sfeer_kolom=False):
    rows = ''
    for n, title, text, lk in items:
        if lk is None and title in GA:
            w = GA[title]
            if sfeer_kolom and title == 'Sfeer': w = 'sfeerkolom'
            lk = link('ga', w)
        rows += f'<li><span class="num">{n}</span><div><b>{title}</b> {text}{(" " + lk) if lk else ""}</div></li>'
    return f'<ol class="legend">{rows}</ol>'

# ---------- inhoud ----------
ov = M['overzicht']['marks']
bal = M['balken']['marks']
flt = M['filters']['marks']
cat = M['catalogus']['marks']
spl = M['speler']['marks']
uur = M['uur']['marks']

fclip = M['filters']['clip']
fa = {k: v for k, v in flt.items() if v['y'] - fclip['y'] < SPLIT}
fb = {k: v for k, v in flt.items() if v['y'] - fclip['y'] >= SPLIT}

body = f'''
<section class="page intro">
  <p class="eyebrow">Handleiding · versie 1.2</p>
  <h1>Welkom bij <span class="acc">CURIOUS XXL</span></h1>
  <p class="lead">CURIOUS XXL is het zendpult voor je eigen muziek. De app leest je hele mp3-bibliotheek in, deelt elk nummer in naar genre, sfeer, dagdeel en speciale dag, en houdt bij wanneer je het voor het laatst hebt gedraaid. Zo stel je in een paar minuten een programma-uur samen dat tot op de minuut klopt.</p>

  <div class="callout">
    <div class="ci">↗</div>
    <div>
      <b>Klikbare links in deze handleiding</b>
      <p>Overal waar je <span class="go sample"><span class="arw">↗</span>Open in CURIOUS XXL</span> ziet, stuurt een klik de app direct naar dat onderdeel, of voert de knop uit. Open deze handleiding daarvoor <b>in de app</b>: met de knop <b>Handleiding ↗</b> rechtsboven, of via <i>Help › Handleiding</i> (Mac: ⌘?, Windows: F1). De handleiding opent dan naast de app en elke klik werkt meteen. In Voorvertoning of een andere pdf-lezer reageren de knoppen vaak niet.</p>
    </div>
  </div>

  <h2>In vijf stappen een uur op de radio</h2>
  <ol class="steps">
    <li><b>Koppel je muziekmap.</b> Kies één keer de map met je mp3's. Daarna doet de app dat bij elke start vanzelf. {link('doe','koppel','','Koppel muziekmap')}</li>
    <li><b>Laat de app indelen.</b> Elk nummer krijgt meteen een eerste indeling. Met <i>Verfijn indeling met Claude</i> wordt die preciezer. {link('doe','verfijn','','Verfijn indeling')}</li>
    <li><b>Kies je filters.</b> Bijvoorbeeld <i>Ochtend</i> en <i>Energiek</i>, of alles van vóór 1970. {link('filter','','dagdeel=Ochtend&sfeer=Energiek','Ochtend + Energiek')}</li>
    <li><b>Vul het uur.</b> Klik op + bij de nummers die je wilt, of laat de app aanvullen met nummers die het langst niet gedraaid zijn, in de opbouw die jij kiest. {link('doe','vul','','Vul aan met filters')}</li>
    <li><b>Kopieer de mp3's.</b> Eén klik zet het draaiboek in een map met de naam van de uitzenddag op je bureaublad. {link('doe','kopieer','',"Kopieer mp3's")}</li>
  </ol>
</section>

<section class="page">
  <p class="eyebrow">1 · Overzicht</p>
  <h2>Het scherm in één oogopslag</h2>
  <p>Het venster is opgebouwd als een zendpult. Bovenaan zitten de balken voor je muziek, het bewaren en het indelen. Daaronder staan van links naar rechts de filters, de catalogus en het programma-uur.</p>
  {figure('shots/overzicht.png','overzicht')}
  {legend([
    (1,'Muziekmap','koppelt je mp3-map en toont de voortgang van het inlezen.',link('ga','muziekmap')),
    (2,'Bewaren','bewaart de catalogus, maakt back-ups en exporteert naar Numbers of Excel.',link('ga','bewaren')),
    (3,'Indelen','laat Claude sfeer, dagdelen en speciale dagen verfijnen.',link('ga','indelen')),
    (4,'Filters','zoek op titel, dagdeel, sfeer, genre, decennium, kalenderdag, thema, duur en energie.',link('ga','filters')),
    (5,'Catalogus','al je nummers met jaar, duur, tempo, toonsoort, energie, sfeer en speelhistorie.',link('ga','catalogus')),
    (6,'Programma-uur','de uurklok, het energieverloop, het draaiboek en de knop om de mp3\'s te kopiëren.',link('ga','uur')),
  ])}
</section>

<section class="page">
  <p class="eyebrow">2 · Muziek</p>
  <h2>Je muziek koppelen en bewaren</h2>
  <p>De eerste keer kies je de map met je mp3's, bijvoorbeeld <span class="mono">Muziek › MP3</span>. De app leest daarna titel, artiest, jaar, genre, duur, tempo en toonsoort uit de tags van elk bestand. Bij een grote bibliotheek duurt dat de eerste keer enkele minuten; daarna gaat het in seconden, want de app herkent elk nummer aan zijn bestandspad.</p>
  {figure('shots/balken.png','balken')}
  {legend([
    (1,'Koppel muziekmap','kies je map. Bij de volgende start koppelt de app hem zelf.',link('doe','koppel')),
    (2,'Bewaar catalogus','bewaart alles direct. De app doet dit ook vanzelf na het inlezen en na elke wijziging.',link('doe','bewaar')),
    (3,'Exporteer voor Numbers of Excel','maakt een overzicht van alle nummers met alle kolommen.',link('doe','export')),
    (4,'Back-up maken','één bestand met je hele catalogus, speelhistorie en bewaarde uren. Daarmee zet je alles ook over naar een andere computer.',link('doe','backup')),
    (5,'Speellijsten importeren','lees oude .m3u-, .txt- of .csv-lijsten in. De datum haalt de app uit de bestandsnaam of uit de regel; zo vult je speelhistorie zich met het verleden.',link('doe','speellijsten')),
    (6,'Verfijn indeling met Claude','zie hoofdstuk 3.',link('doe','verfijn')),
  ])}
  <div class="tip"><b>Goed om te weten</b> De app kopieert en leest je mp3's, maar verplaatst of verandert ze nooit. Elke dag maakt de app bovendien automatisch een reservekopie van de catalogus.</div>
</section>

<section class="page">
  <p class="eyebrow">3 · Indelen</p>
  <h2>Hoe de app je muziek indeelt</h2>
  <p>Elk nummer krijgt een genre, een sfeer, een of meer dagdelen en, waar dat past, speciale dagen en thema's. Dat gebeurt in twee lagen. In de catalogus zie je achter de sfeer welke laag het was.</p>
  <div class="two">
    <div class="card"><div class="sym">≈</div><h3>Eerste indeling</h3><p>Direct na het inlezen, voor alle nummers tegelijk. De app kijkt naar het genre in de tag en naar woorden in de titel. <i>Christmas</i> wordt Kerst, <i>Summer</i> wordt Zomer, <i>Love</i> wordt Liefdesliedjes. Een snel tempo maakt een nummer energieker.</p></div>
    <div class="card"><div class="sym">✦</div><h3>Verfijnd door Claude</h3><p>Claude kent de meeste nummers zelf en vult sfeer, dagdelen, speciale dagen, tempo, energie en toonsoort nauwkeuriger in. Het jaar wordt het jaar van de eerste uitgave, niet dat van een verzamel-cd. Dat gaat in porties van zestig nummers. Je kunt pauzeren; tussendoor bewaart de app alles. {link('doe','verfijn','','Start verfijnen')}</p></div>
  </div>
  <h3>De indeling in cijfers</h3>
  <table class="facts">
    <tr><th>Sferen</th><td>Energiek · Vrolijk · Feestelijk · Zonnig · Stoer · Spannend · Relaxed · Dromerig · Ingetogen · Romantisch · Melancholisch · Nostalgisch</td></tr>
    <tr><th>Dagdelen</th><td>Ochtend 06–10 · Middag 10–14 · Namiddag 14–18 · Avond 18–22 · Nacht 22–06</td></tr>
    <tr><th>Genres</th><td>22 genres, van Pop en Rock tot Levenslied, Chanson en Kinderliedjes. <b>Oldies</b> toont alles van vóór 1970, wat het genre ook is.</td></tr>
    <tr><th>Kalender</th><td>Nieuwjaar · Valentijn · Carnaval · Pasen · Koningsdag · Dodenherdenking · Bevrijdingsdag · Moederdag · Vaderdag · Zomer · Herfst · Halloween · Sinterklaas · Kerst · Oudejaarsavond</td></tr>
    <tr><th>Energie</th><td>1 rustig tot 10 piek · Laag 1–3 · Midden 4–6 · Hoog 7–8 · Piek 9–10</td></tr>
    <tr><th>Duur</th><td>Kort onder 3:00 · 3–4 min · 4–5 min · Lang boven 5:00</td></tr>
    <tr><th>Toonsoort</th><td>In Camelot-notatie: 1 tot 12 met A voor mineur en B voor majeur. 8A is A-mineur, 8B is C-majeur.</td></tr>
    <tr><th>Thema's</th><td>Maandagochtend · Zondagochtend · Vrijdagmiddagborrel · Zomeravond · Regenachtige dag · Haardvuuravond · Diner · Workout · Roadtrip · Feestavond · Liefdesliedjes · Verjaardag · Bruiloft · Afscheid &amp; troost</td></tr>
  </table>
  <div class="tip"><b>Klopt iets niet?</b> Pas het nummer zelf aan met ✎ (hoofdstuk 8). Wat jij instelt, overschrijft Claude niet meer.</div>
</section>

<section class="page">
  <p class="eyebrow">4 · Filters</p>
  <h2>Zoeken met filters</h2>
  <div class="filtgrid">
    <div class="fcols">
      {figure('shots/filters_a.png','filters', fa, clip={'x':fclip['x'],'y':fclip['y'],'width':fclip['width'],'height':SPLIT}, hcss=SPLIT)}
      {figure('shots/filters_b.png','filters', fb, clip={'x':fclip['x'],'y':fclip['y'],'width':fclip['width'],'height':fclip['height']-SPLIT}, yoff=SPLIT, hcss=fclip['height']-SPLIT)}
    </div>
    <div>
      <p>Klik op een filter om het aan te zetten en nog eens om het uit te zetten. Het getal achter elk filter vertelt hoeveel nummers erbij passen.</p>
      <p>Binnen één groep zoekt de app op het een óf het ander: <i>Ochtend</i> en <i>Middag</i> samen geeft beide. Tussen groepen moet alles kloppen: <i>Ochtend</i> plus <i>Energiek</i> geeft alleen energieke ochtendnummers.</p>
      {legend([
        (1,'Zoeken','op titel of artiest.',link('ga','zoeken')),
        (2,'Dagdeel','',None),(3,'Sfeer','met een kleur die je terugziet in de uurklok.',None),
        (4,'Genre','met Oldies bovenaan.',None),(5,'Decennium','',None),
        (6,'Kalender','',None),(7,'Thema','',None),
        (8,'Duur','kort, 3–4, 4–5 of lang.',link('filter','','duur=kort','Korte nummers')),
        (9,'Energie','laag, midden, hoog of piek.',link('filter','','energie=hoog','Hoge energie')),
        (10,'Rotatie','verbergt nummers die de laatste veertien dagen al zijn gedraaid.',None),
        (11,'Toonsoort','toont alleen nummers die harmonisch aansluiten op het laatste nummer in je uur.',None),
      ])}
      <h3>Probeer het meteen</h3>
      <div class="quick">
        {link('filter','','genre=Oldies','Oldies (vóór 1970)')}
        {link('filter','','dag=Kerst','Kerst')}
        {link('filter','','thema=Zondagochtend','Zondagochtend')}
        {link('filter','','dagdeel=Ochtend&sfeer=Energiek','Ochtend + Energiek')}
        {link('filter','','thema=Liefdesliedjes&dagdeel=Avond','Liefde in de avond')}
        {link('filter','','decennium=Jaren%2080','Jaren 80')}
        {link('filter','','thema=Feestavond&rust=1','Feestavond, uitgerust')}
        {link('doe','wis','','Alle filters wissen')}
      </div>
    </div>
  </div>
</section>

<section class="page">
  <p class="eyebrow">5 · Catalogus</p>
  <h2>De catalogus en voorluisteren</h2>
  <p>Elke regel is één nummer. Klik op een kolomkop om daarop te sorteren, en nog eens om de volgorde om te draaien. De catalogus toont tweehonderd nummers tegelijk; onderaan haal je er meer bij.</p>
  {figure('shots/catalogus.png','catalogus')}
  {legend(sfeer_kolom=True,items=[
    (1,'Afspelen','klik op ▶ om het nummer voor te luisteren. Nog een klik pauzeert.',None),
    (2,'Kolomkoppen','sorteer op titel, jaar, duur, tempo, energie, sfeer, gedraaid of laatst gedraaid.',None),
    (3,'Tempo en toonsoort','BPM met daaronder de toonsoort in Camelot-notatie.',None),
    (4,'Energie','van 1 tot 10. Met ≈ is het een schatting uit sfeer en tempo.',None),
    (5,'Sfeer','met ≈ voor de eerste indeling en ✦ als Claude hem verfijnde.',None),
    (6,'Dagdeel en dag','de dagdelen en, eronder, de speciale dagen en thema\'s.',None),
    (7,'Gedraaid','hoe vaak het nummer is uitgezonden; de streepjes groeien mee.',None),
    (8,'Laatst','de laatste uitzenddatum met de rusttijd: <span class="pill red">rood</span> binnen 14 dagen, <span class="pill amber">oranje</span> binnen 30, <span class="pill green">groen</span> daarna of nooit.',None),
    (9,'Aanpassen','open het bewerkvenster voor dit nummer.',None),
    (10,'In het uur','zet het nummer in het programma-uur, of haal het eruit.',None),
  ])}
  <h3>De speler</h3>
  {figure('shots/speler.png','speler', cls='thin')}
  {legend([
    (1,'Afspelen en pauzeren','met de knop of de spatiebalk.',None),
    (2,'Positie','sleep om door het nummer te gaan.',None),
    (3,'Snelknoppen','<i>Begin</i>, <i>Midden</i> en <i>Laatste 20 s</i>. Die laatste is handig om een overgang naar het volgende nummer te beoordelen.',None),
  ])}
</section>

<section class="page">
  <p class="eyebrow">6 · Programma-uur</p>
  <h2>Een uur samenstellen</h2>
  <div class="uurgrid">
    {figure('shots/uur.png','uur')}
    <div>
      <p>Rechts bouw je het uur. De uurklok kleurt per nummer in de kleur van zijn sfeer, zodat je in één blik ziet hoe het uur verloopt. Het grijze stuk is de tijd voor praat, jingles en reclame.</p>
      {legend([
        (1,'Uitzenddag en begintijd','bepalen het dagdeel en de naam van de map met mp3\'s.',link('ga','uur')),
        (2,'Uurklok','gevulde muziektijd, wat er nog over is, het aantal nummers en het gemiddelde tempo.',link('ga','klok')),
        (3,'Energieverloop','de energie van elk nummer, in de volgorde van het uur.',None),
        (4,'Opbouw','kies hoe het uur moet lopen. Zie hoofdstuk 7.',link('ga','opbouw')),
        (5,'Praattijd','schuif tussen 0 en 30 minuten. De klok rekent mee.',None),
        (6,'Vul aan met filters','vult het uur met nummers die passen bij je filters, je opbouw volgen en het langst niet gedraaid zijn.',link('doe','vul')),
        (7,'Draaiboek','met de starttijd, de energie (E) en de toonsoort van elk nummer. ≠ betekent: de toonsoort sluit niet aan op het vorige nummer.',link('ga','draaiboek')),
        (8,"Kopieer mp3's naar een map",'zet kopieën in draaiboekvolgorde op je bureaublad, in een map met de naam van de uitzenddag, met een afspeellijst en een draaiboek erbij.',link('doe','kopieer')),
        (9,'Kopieer draaiboek','als tekst, om te plakken in je presentatie- of uitzendsoftware.',link('doe','draaiboek')),
        (10,'Bewaar dit uur','om het later terug te halen of te hergebruiken.',link('doe','bewaaruur')),
        (11,'Markeer als uitgezonden','schrijft de datum van vandaag bij elk nummer. Klik twee keer om te bevestigen.',link('doe','uitgezonden')),
        (12,'Bewaarde uren openen','haalt een eerder bewaard uur terug.',None),
      ])}
    </div>
  </div>
  <div class="folder">
    <div class="ficon"></div>
    <div><b>Dinsdag 17 november 2026</b><span class="mono">01 - Bill Withers - Lovely Day.mp3 · 02 - Golden Earring - Radar Love.mp3 · … · Dinsdag 17 november 2026.m3u · Draaiboek.txt</span></div>
  </div>
</section>

<section class="page">
  <p class="eyebrow">7 · Opbouw</p>
  <h2>Duur, energie en toonsoort</h2>
  <p class="lead">Een goed radio-uur heeft een vorm. Het begint, bouwt op, piekt en landt precies op tijd. Daarvoor kijkt CURIOUS XXL naar drie dingen: hoe lang een nummer duurt, hoeveel energie het heeft en in welke toonsoort het staat.</p>
  <div class="two">
    <div class="card"><div class="sym">⏱</div><h3>Duur: precies op de minuut</h3><p>Bij <i>Vul aan met filters</i> vult de app eerst het uur. Voor de laatste zes minuten zoekt hij één nummer, of twee samen, dat de muziektijd zo precies mogelijk vult. Na het vullen zie je hoeveel seconden er over zijn. Met het filter <b>Duur</b> kies je zelf korte of lange nummers, bijvoorbeeld kort voor het nieuws. {link('filter','','duur=kort','Korte nummers')}</p></div>
    <div class="card"><div class="sym">↗</div><h3>Energie: de spanningsboog</h3><p>Elk nummer krijgt een energie van 1 (heel rustig) tot 10 (piek). Zonder verfijning schat de app dit uit sfeer en tempo, met het teken ≈. Claude verfijnt het per nummer. Het <b>energieverloop</b> onder de uurklok laat de boog van je uur zien. {link('filter','','energie=piek','Piek-nummers')}</p></div>
  </div>
  <h3>Kies de opbouw van het uur</h3>
  <table class="facts">
    <tr><th>Vrij</th><td>Geen vaste vorm: de nummers die het langst niet gedraaid zijn, gaan voor. {link('doe','vul','opbouw=vrij','Vul vrij')}</td></tr>
    <tr><th>Opbouwen</th><td>Van rustig (3) naar hoog (9). Goed voor de ochtend en het begin van het weekend. {link('doe','vul','opbouw=op','Vul opbouwend')}</td></tr>
    <tr><th>Piek</th><td>Rustig begin, hoogtepunt rond half, rustig einde. {link('doe','vul','opbouw=piek','Vul met piek')}</td></tr>
    <tr><th>Afbouwen</th><td>Hoog beginnen en rustig afsluiten. Goed voor de avond en de nacht. {link('doe','vul','opbouw=af','Vul afbouwend')}</td></tr>
    <tr><th>Gelijkmatig</th><td>Steeds rond energie 6. {link('doe','vul','opbouw=vlak','Vul gelijkmatig')}</td></tr>
  </table>
  <h3>Toonsoort: overgangen die kloppen</h3>
  <p>De toonsoort staat in de <b>Camelot-notatie</b> die dj's gebruiken: een getal van 1 tot 12 en een letter, A voor mineur en B voor majeur. Twee nummers sluiten mooi op elkaar aan als ze hetzelfde getal hebben, als het getal één hoger of lager is met dezelfde letter, of als alleen de letter verschilt. Na 8A passen dus 8A, 7A, 9A en 8B.</p>
  <p>Bij het vullen kiest de app liever een nummer dat aansluit. In het draaiboek zie je per nummer de energie (E) en de toonsoort; ≠ betekent dat de overgang botst. Zet bij de filters <b>Alleen toonsoorten die passen bij het laatste nummer</b> aan om alleen aansluitende nummers te zien. {link('filter','','harmonisch=1','Passende toonsoorten')}</p>
  <div class="tip"><b>Waar komt de toonsoort vandaan?</b> Uit de tag van het mp3-bestand (TKEY), als een programma als Mixed In Key, Rekordbox of DaJent die heeft geschreven. Staat er niets, dan vult Claude hem bij het verfijnen in als hij het nummer goed kent. Je kunt hem ook zelf invullen met ✎.</div>
</section>

<section class="page">
  <p class="eyebrow">8 · Bijwerken</p>
  <h2>Een nummer aanpassen</h2>
  <div class="edgrid">
    {figure('shots/bewerken.png','bewerken')}
    <div>
      <p>Klik in de catalogus op <b>✎</b> om een nummer aan te passen. Je kunt titel, artiest, jaar, tempo, energie en toonsoort verbeteren. De toonsoort mag je typen als <i>Am</i> of als <i>8A</i>; en genre, sfeer, dagdelen, speciale dagen en thema's kiezen.</p>
      <p>Klik op <b>Opslaan</b>. De app bewaart de wijziging vanzelf na een paar seconden. Een nummer dat je zelf hebt aangepast, slaat Claude bij het verfijnen over.</p>
      <h3>Uitzenden en speelhistorie</h3>
      <p>Na elke uitzending klik je op <b>Markeer als uitgezonden</b>. Elk nummer in het uur krijgt dan de datum van vandaag. In de catalogus zie je daarna hoe vaak en wanneer een nummer is gedraaid, en met de rotatieschakelaar houd je recent gedraaide nummers buiten beeld. {link('doe','uitgezonden','','Markeer als uitgezonden')}</p>
      <p>Heb je oude speellijsten van eerdere uitzendingen? Lees ze in met <b>Speellijsten importeren</b>; dan begint de historie niet bij nul. {link('doe','speellijsten','','Speellijsten importeren')}</p>
    </div>
  </div>
</section>

<section class="page">
  <p class="eyebrow">9 · Mac en Windows</p>
  <h2>Installeren en overzetten</h2>
  <div class="two">
    <div class="card"><h3>Mac</h3>
      <p>De app heet <b>CURIOUS XXL</b> en staat in de map <i>Programma's</i>. Bij de eerste start vraagt macOS of de app bij je map Muziek en je bureaublad mag: kies twee keer <b>Sta toe</b>.</p>
      <p>Je catalogus staat in <span class="mono">Bibliotheek › Application Support › CURIOUS XXL</span>. Via <i>Weergave › Toon catalogusmap</i> open je die map.</p>
    </div>
    <div class="card"><h3>Windows 11</h3>
      <p>Pak <b>CURIOUS XXL voor Windows.zip</b> uit en start <b>CURIOUS XXL.exe</b>. Een installatie is niet nodig.</p>
      <p>De eerste keer toont Windows <i>Windows heeft uw pc beschermd</i>. Klik op <b>Meer informatie</b> en dan op <b>Toch uitvoeren</b>. Dat hoeft maar één keer.</p>
      <p>De catalogus staat via <i>Bestand › Toon catalogusmap</i>.</p>
    </div>
  </div>
  <h3>Van de Mac naar Windows</h3>
  <ol class="steps small">
    <li>Klik op de Mac op <b>Back-up maken</b> en bewaar het bestand. {link('doe','backup','','Back-up maken')}</li>
    <li>Zet het bestand op de Windows-computer, bijvoorbeeld met een USB-stick.</li>
    <li>Klik daar op <b>Back-up terugzetten</b> en kies het bestand. {link('doe','terugzetten','','Back-up terugzetten')}</li>
    <li>Koppel op Windows de muziekmap met dezelfde mp3's. Indeling en historie komen dan mee.</li>
  </ol>
  <h3>Vragen en oplossingen</h3>
  <dl class="faq">
    <dt>Een link in deze handleiding doet niets.</dt>
    <dd>Je bekijkt de handleiding dan in Voorvertoning of een andere pdf-lezer. Open hem in de app met de knop <b>Handleiding ↗</b> of via <i>Help › Handleiding</i>; daar werkt elke link.</dd>
    <dt>Een nummer speelt niet af.</dt>
    <dd>Het bestand is verplaatst of beschadigd. Koppel de muziekmap opnieuw; de app zoekt dan alles opnieuw op.</dd>
    <dt>De app stopte tijdens het inlezen.</dt>
    <dd>Open de app gewoon opnieuw. Een bestand dat het inlezen liet stoppen, slaat de app de volgende keer over.</dd>
    <dt>"Verfijn indeling met Claude" werkt niet.</dt>
    <dd>Daarvoor moet Claude Code op deze computer staan. Zonder Claude Code blijft de eerste indeling gewoon werken.</dd>
    <dt>Ik zie de voorbeeldnummers nog.</dt>
    <dd>Die verdwijnen zodra je je eigen muziekmap koppelt.</dd>
  </dl>
</section>


<section class="page">
  <p class="eyebrow">10 · Over</p>
  <h2>Maker, eigenaar en rechten</h2>
  <p>CURIOUS XXL is bedacht, ontworpen en in eigendom van <b>Han Koopman</b>, voor zijn radioprogramma Radio Curious. Onderaan het venster van de app staat dezelfde informatie. {link('ga','over','','Over CURIOUS XXL')}</p>
  {figure('shots/over.png','over')}
  <div class="two">
    <div class="card"><h3>Maker en eigenaar</h3>
      <p><b>Han Koopman</b><br>Radio Curious · Zeewolde</p>
      <p>Website: <a class="ext" href="https://hankoopman.nl">hankoopman.nl</a><br>Broncode: <a class="ext" href="https://github.com/an0n1mu3721-spec/curious-xxl">github.com/an0n1mu3721-spec/curious-xxl</a></p>
      <p class="mono">Versie 1.2 · november 2026 · Mac en Windows 11</p>
    </div>
    <div class="card rights"><h3>Niet verspreiden zonder toestemming</h3>
      <p>© 2026 Han Koopman. Alle rechten voorbehouden.</p>
      <p>De app, de broncode, het icoon en deze handleiding mag je niet kopiëren, doorgeven, aanpassen, publiceren of verkopen zonder schriftelijke toestemming van Han Koopman. Dat de code op GitHub te zien is, geeft geen recht op gebruik of verspreiding.</p>
      <p>Toestemming vragen kan via <a class="ext" href="https://hankoopman.nl">hankoopman.nl</a>.</p>
    </div>
  </div>
  <p class="mono" style="margin-top:4mm">Gebouwd met hulp van Claude. Radio Curious en Curious4ever zijn namen en logo's van Han Koopman.</p>
</section>
<section class="page">
  <p class="eyebrow">11 · Snelkoppelingen</p>
  <h2>Alle links op één pagina</h2>
  <p>Leg deze pagina naast de app. Elke regel stuurt CURIOUS XXL direct naar de plek of de knop.</p>
  <div class="links3">
    <div><h3>Ga naar</h3>
      {link('ga','muziekmap','','Muziekmap')}{link('ga','bewaren','','Bewaren')}{link('ga','indelen','','Indelen')}{link('ga','filters','','Filters')}{link('ga','zoeken','','Zoeken')}{link('ga','catalogus','','Catalogus')}{link('ga','uur','','Programma-uur')}{link('ga','klok','','Uurklok')}{link('ga','draaiboek','','Draaiboek')}{link('ga','opbouw','','Opbouw van het uur')}{link('ga','duur','','Duurfilter')}{link('ga','energie','','Energiefilter')}{link('ga','over','','Over CURIOUS XXL')}
    </div>
    <div><h3>Doe</h3>
      {link('doe','koppel','','Koppel muziekmap')}{link('doe','bewaar','','Bewaar catalogus')}{link('doe','backup','','Back-up maken')}{link('doe','terugzetten','','Back-up terugzetten')}{link('doe','export','','Exporteer voor Excel')}{link('doe','speellijsten','','Speellijsten importeren')}{link('doe','verfijn','','Verfijn indeling')}{link('doe','vul','','Vul aan met filters')}{link('doe','leeg','','Uur leegmaken')}{link('doe','kopieer','',"Kopieer mp3's")}{link('doe','draaiboek','','Kopieer draaiboek')}{link('doe','bewaaruur','','Bewaar dit uur')}{link('doe','uitgezonden','','Markeer als uitgezonden')}{link('doe','vul','opbouw=op','Vul opbouwend')}{link('doe','vul','opbouw=piek','Vul met piek')}{link('doe','vul','opbouw=af','Vul afbouwend')}{link('doe','wis','','Filters wissen')}
    </div>
    <div><h3>Filters</h3>
      {link('filter','','dagdeel=Ochtend','Ochtend')}{link('filter','','dagdeel=Avond','Avond')}{link('filter','','dagdeel=Nacht','Nacht')}{link('filter','','genre=Oldies','Oldies')}{link('filter','','genre=Nederlandstalig','Nederlandstalig')}{link('filter','','sfeer=Feestelijk','Feestelijk')}{link('filter','','sfeer=Relaxed','Relaxed')}{link('filter','','sfeer=Nostalgisch','Nostalgisch')}{link('filter','','dag=Kerst','Kerst')}{link('filter','','dag=Koningsdag','Koningsdag')}{link('filter','','thema=Workout','Workout')}{link('filter','','thema=Regenachtige%20dag','Regenachtige dag')}{link('filter','','decennium=Jaren%2070','Jaren 70')}{link('filter','','decennium=Jaren%2080','Jaren 80')}{link('filter','','duur=kort','Kort')}{link('filter','','duur=lang','Lang')}{link('filter','','energie=laag','Lage energie')}{link('filter','','energie=piek','Piek-energie')}{link('filter','','harmonisch=1','Passende toonsoort')}
    </div>
  </div>
  <p class="sign">CURIOUS XXL · © 2026 Han Koopman · Alle rechten voorbehouden · Niet verspreiden zonder toestemming — <i>Voor eeuwig nieuwsgierig</i></p>
</section>
'''

# markeringen in schermafbeeldingen en legendanummers klikbaar maken
import re
def _clickable(sec):
    figs = list(re.finditer(r'<figure class="shot.*?</figure>', sec, re.S))
    legs = list(re.finditer(r'<ol class="legend">.*?</ol>', sec, re.S))
    if not figs or not legs: return sec
    out = sec
    for fi, f in enumerate(figs):
        # bijbehorende legenda: de eerste legenda na deze figuur, anders de laatste ervoor
        after = [l for l in legs if l.start() > f.end()]
        leg = (after or legs)[0].group(0) if (after or legs) else ''
        hrefs = {}
        for li in re.finditer(r'<li><span class="num">(\d+)</span>(.*?)</li>', leg, re.S):
            m = re.search(r'href="([^"]+)"', li.group(2))
            if m: hrefs[li.group(1)] = m.group(1)
        if not hrefs: continue
        fig = f.group(0)
        new = re.sub(r'<span class="dot" style="([^"]+)">(\d+)</span>',
                     lambda m: f'<a class="dot" style="{m.group(1)}" href="{hrefs[m.group(2)]}">{m.group(2)}</a>' if m.group(2) in hrefs else m.group(0), fig)
        out = out.replace(fig, new, 1)
    for l in legs:
        leg = l.group(0)
        new = re.sub(r'<li><span class="num">(\d+)</span>(.*?)</li>',
                     lambda m: (lambda h: f'<li><a class="num" href="{h.group(1)}">{m.group(1)}</a>{m.group(2)}</li>' if h else m.group(0))(re.search(r'href="([^"]+)"', m.group(2))), leg, flags=re.S)
        out = out.replace(leg, new, 1)
    return out
body = '<section'.join([_clickable(x) for x in body.split('<section')])

CSS = open('doc.css').read()
open('body.html', 'w').write(f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><link rel="stylesheet" href="fonts/fonts.css"><style>{CSS}</style></head><body>{body}</body></html>')

cover = f'''<!doctype html><html lang="nl"><head><meta charset="utf-8"><link rel="stylesheet" href="fonts/fonts.css"><style>{CSS}@page{{margin:0}}html,body{{margin:0}}</style></head><body class="coverbody">
<div class="cover">
  <div class="glow"></div>
  <img class="cicon" src="icon.png" alt="">
  <p class="ceyebrow"><span class="onair">On air</span> Radio Curious</p>
  <h1 class="ctitle">CURIOUS <span>XXL</span></h1>
  <p class="csub">Handleiding</p>
  <p class="clead">Radio-uren samenstellen uit je eigen muziek: indelen, voorluisteren, plannen en uitzenden.</p>
  <div class="cfoot"><span>Versie 1.2 · november 2026</span><span>Mac · Windows 11</span><span>© 2026 Han Koopman</span></div><p class="crights">Maker en eigenaar: Han Koopman · Radio Curious. Alle rechten voorbehouden. Niet verspreiden zonder toestemming.</p>
</div></body></html>'''
open('cover.html', 'w').write(cover)
print('html klaar')
