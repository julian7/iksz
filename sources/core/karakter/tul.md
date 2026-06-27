## Tulajdonságok

A tulajdonságok a karakter alapvető ismérvei. Az **alaptulajdonságok**
az elemi, míg a **származtatott tulajdonságok** az összetettebb
alapjellemzőket írják le.

### Alaptulajdonságok

Minden alaptulajdonság értéke 1-6-ig (legrosszabbtól legjobbig) terjedhet.
Példákat is írtunk a legkisebbhez és legnagyobbhoz, hogy lásd, mit is
jelentenek az értékek.

::: {.float-right}

| Érték | módosító |
|---|---|
| 1 | -2 |
| 2 | -1 |
| 3 |  |
| 4 |  |
| 5 | 1 |
| 6 | 2 |

Table: alaptulajdonságok {#tab:tul}

:::

**ERŐ**

Fizikai felépítés. **1**: a karakter 30 kiló vasággyal, és nagyon kell erőlködnie, hogy egy erősebb széllökés ne ragadja magával. **6**: Minimum 210 cm magas, többet nyom, mint egy mázsa, és senki sem mer vele szkanderezni.

**OKOSSÁG (OKS)**

Bonyolult feladatok megoldásához elengedhetetlen leleményesség. Modernebb világban talán technikai érzéknek is felfogható. **1**: a karakter nem tud megkülönböztetni egy narancsot a sétapálcától. **6**: rá mondják, hogy mázlista, holott egyszerűen csak kihasználja azokat a lehetőségeket, ami nem mindenkinek nyílvánvaló.

**ÜGYESSÉG (ÜGY)**

Fürgeség, szem-kéz-láb koordináció. **1**: ne adj ilyen karakter kezébe éleset, mert még megvágja magát! **6**: 12 yardról lesöpri a Kemény Joe fejére szállt legyet -- akár baltával is.

**EGÉSZSÉG (EGS)**

Testi kondíció, betegségekkel szembeni ellenállóképesség. **1**: ha más nincs, szénanáthája mindig van. **6**: Ne hidd el neki, hogy "leszaladok kajáért, a bolt úgyis csak egy köpésre van", mert az rendben, hogy gyorsan megfordul, de biztos, hogy legalább 10 km-en belül nincs még egy szatócsbolt se.

**AKARAT (AKA)**

Állhatatosság. **1**: a karaktert mindenki palira tudja venni. **6**: ha fejébe veszi, és adnak neki elég felszerelést, egyedül átússza a Csendes Óceánt (de lehet, hogy azt inkább mégsem…)

**SZERENCSE (SZE)**

Mázli. Vannak olyan dolgok, hogy már csak a szerencse segít. **1**: sosem veszi észre a nyitott csatornafedőket, mert ki akarja kerülni a zuhanó virágcserepet, miközben elcsúszott egy banánhéjon, és belehuppant egy pocsolyába. **6**: még az utcai itt a pirosozó is csak csodálkozik, hogyan került vissza a felemelt gyufásskatulya alá a szivacsdarabka.

> **Megjegyzés:** Ez a tulajdonság opcionális, a mesélő határozza meg, hogy létezik-e. Ha nem, akkor a kötelező **SZE** érték behelyettesítésekkor *1d*-t kell dobni.

A karakter alaptulajdonságainak meghatározására két módszer lehetséges:

- A karakter megalkotásakor kap **20 pontot** (ha nincs **SZE** tulajdonság, akkor 16-ot), amit szabadon elkölthet tulajdonságaira.

- A játékos minden tulajdonságra dob *2d/2*-t.

Minden alaptulajdonságpont meghatározza a tulajdonsághoz tartozó módosítót
is. Ezt az . táblázat tartalmazza.

### Származtatott tulajdonságok

A származtatott tulajdonságok nevükből adódóan az alaptulajdonságokból
származtathatóak. A származtatott tulajdonságok némelyikének két fajta
értéke van, mivel azok szoros kapcsolatban állnak a karakter aktuális
állapotával.

- **Fájdalomtűrés**: **ERŐ+EGS+AKA** alapú. Két értéke van: maximális és aktuális. Ha sérülés éri a karaktert, az aktuális érték lecsökken a maximálisról, amit később pihenéssel, gyógyulással visszaszerezhet. Ha az aktuális érték 0-ra csökken, a karakter elájul.

- **Varázsellenállás**: **AKA+OKS** alapú. Ez segít a karakternek az ellene használt varázslatok hatásának semlegesítésében. Az értékhez hozzáadódik egy harmadik tulajdonság is, attól függően, hogy milyen fajta varázslattal célozták meg.

- **Kezdeményezés**: **ÜGY+SZE** alapú. Harcban, a kezdeményezés dobásnak ez az alapja.
