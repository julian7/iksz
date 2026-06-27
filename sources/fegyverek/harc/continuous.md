## Harc

Amikor véget ér a szerepjáték, és eljön a harc ideje, a játék folyama
megváltozik, és minden lépést szigorúan rögzített szabályok szerint kell
lejátszani.  Ez természetesen nem azt jelenti, hogy nem térhettek el ezektől
a szabályoktól, csak ha valamiben megállapodtatok, akkor azt következetesen
tartsátok be.

A harc közben nagyon lényeges, hogy tisztában legyetek azzal, hogy pontosan
ki mikor tud cselekedni.  Ezért a harcot szegmensekre bontjuk, méghozzá úgy,
hogy négy szegmens feleljen meg egy másodpercnek.

Mint tudjuk, a verekedés akkor kezdődik, mikor a sógor visszaüt.  Így a harc
is akkor kezdődik, mikor egy karakter (ez lehet játékos vagy nem játékos,
esetleg egy szörny is) bejelenti támadási szándékát.  Ettől a pillanattól
kezdve osztjuk az időt szegmensekre, nullától kezdve.  Hogy miért nullától?
Egyszerű: hiszen nullánál még nem történik semmi, csak a támadó cselekedet
kezdődik meg.

A harcba később is be lehet szállni, ám az időpont (a szegmens száma) teljes
mértékben a mesélőtől függ.  A legtöbbször elég az is, ha a játékos bejelenti
ezt a szándékát, és onnantól kezdve ő is részese lehet a küzdelemnek.

### Harci eszközök

Alapvetően minden fegyver alkalmas védekezésre is.  Így minden fegyvernek
vannak támadási és védekezési értékei.  Ugyanígy a védelmi felszerelések
szintén használhatók támadásra is (például a pajzzsal jókorát lehet sújtani
az ellenfél sisakjára), így ezeket csak az értékeik eloszlásában
különböztetjük meg a fegyverektől.

A fegyvereknek négy alapvető ismérve van: a támadási (T) és védekezési (V)
hatékonyság (H), illetve sebességmódosító (S).   A **TH**-nak támadáskor, a
**VH**-nak védekezéskor, a **TS**-nek és **VS**-nek a cselekedethez
szükséges idő számításában van jelentőségük.

A fegyverek között megkülönböztetjük a távolsági fegyvereket (lő- és dobó
fegyverek), illetve közelharci fegyvereket.  A távolsági fegyverek egyik
fontos tulajdonsága a **hatótáv**, a közelharci fegyvereknek pedig a **méret**.
A közelharci fegyverek így lehetnek 1.: *kisméretűek* (pl. tőr), 2.:
*közepes méretűek* (pl. kard), illetve 3.: *nagyméretűek* (pl. pallos).  A
méretnek a harcnál sok szerepe van.

Más a helyzet a páncélokkal: ezeket nem hárításra, hanem a sebesülés
csökkentésére lehet hatékonyan használni.  Ám a páncélok minél merevebbek
(amik mellesleg megvédenek az ellenség csapásaitól), annál inkább
immobilizálják a karaktert.  Ez leginkább a harci tulajdonságok leromlásához
vezet.  Az előbbi értéket **SF**-nek, azaz sebzésfelfogásnak, az utóbbit
**MT**-nek, azaz megterheltségnek hívjuk.  A **SF**-et a szerzett sebesülésből
lehet levonni, míg a **MT**-t a sebességmódosítókhoz kell hozzáadni, és a
támadási és védekezési hatékonyságból kell levonni (valójában lassítja, és
lanyhítja a cselekedeteket).

### Reakció és meglepetés

Egy cselekedetre többféleképpen lehet reagálni: meglepetésből, vagy
felkészülten.  Meglepni akkor lehet az egyik résztvevőt, ha nem követte
figyelemmel a harci cselekedetet, vagy egyszerűen nem érzékelte (pl. hátulról
suttyomban támadnak).  Ilyenkor a mesélő dönti el, hogy meglepetés volt-e,
és hogy jogosult-e a karakter reakció ellenpróbát dobni.  Ha ugyanis sikerül a
reakció ellenpróba, akkor oda a meglepetés.

> Reakció ellenpróba: támadó **felismerés/veszély** (vagy **orvtámadás**) *vs.*
ellenfelek **felismerés/veszély**

Természetesen egy harc kirobbanása nem csak az áldozatot, de az éppen arra
járó kutyát sétáltató nénit is meglepi, így mindenki, aki érdekelt a
meglepetésben, egyszerre dob reakció ellenpróbát a támadó ellen.

Akinek nem sikerült a reakció ellenpróba, vagy esetleg esélye sem volt
megdobni azt, azt meg lehet lepni a támadással.  Tehát ha a támadás maga
csöndes, akkor csak az áldozat lepődik meg, ám ha az eredmény például egy
nagy csattanás, akkor mindegyikük meglepődik.

Akit sikerült meglepni, az hirtelen abbahagyja a jelenlegi tevékenységét, de
azonnal cselekedhet.

### Cselekedetek

A cselekedetek harci, illetve nem harci tevékenységekre oszthatók.  A harci
cselekedetek közé csakis a támadás és védekezés tartozik. A másikba tartozik
a fegyverrántás, fegyver felhúzása (nyíl az íj húrjára a tegezből,
csőretöltés stb.), de ide tartozik a futás, az elrejtőzés, a beszéd, és a
többi, alapvetően nem harci cselekedet is.

A cselekedeteket másféleképpen is fel lehet bontani: a befejeződő, illetve
kartható tevékenységekre.  Míg az első fajta a cselekedet végrehajtási ideje
lejártakor történik meg (pl. ha a tőrrel támadás két szegmensig tart, akkor
a támadás az akció indítása utáni második szegmensben fog bekövetkezni), a
kitartható cselekedetek onnantól kezdve bármikor kifejthetik hatásukat
(mivel védekező pozíció felvétele után is csak a támadás pillanatában kell
reagálni).

#### Időfüggés

A cselekedetek időigénye nagyban függ az alany ügyességétől, illetve
megterheltségétől.  Így általánosságban elmondhatjuk, hogy

> **CSI** = sebességmódosító + **MT-ÜGY** bónusz

ahol

| **CSI** | = | cselekedet időigénye [szegmens] |
|---|---|---|
| **MT** | = | megterheltség |




**támadás módosítók**

| helyzet | módosító | megjegyzés |
|---|---|---|
| hátulról | +3 | mindenképpen reakció ellenpróba kell! |
| felülről | +2 |  |
| alulról | -2 |  |
| rohamozva | +3 |  |
| láthatatlan | +6 | csökkenthető a felismerés/vakharc szakértelemmel |
| meglepetésből | +2 |  |
| adott testrészre | -4 -- -6 |  |
| létfontosságú szervre | -8 | *x2* sebzés |


| **TÉ** | = | támadási érték |
|---|---|---|
| harci képzettség | = | a harci szakértelem és a megfelelő |
| **TH** | = | fegyver támadási hatékonyság | támadási módosító | = | ld. az alábbi táblázatban, a |
| **MT** | = | megterheltség |


A védekező pozícióból bármikor áttérhetünk támadó pozícióba, a **TS** és a
**VS** különbsége sebességmódosítóval.

Sikeres közelharci védekezés után lehetőség van **riposztra**: ilyenkor
ugyanaz a helyzet, mint az előbbi helyzetben:

> Riposzt **TS**: Fegyver **TS** - Fegyver **VS**



**Védekezési módosítók**

| helyzet | módosító | megjegyzés |
|---|---|---|
| mozdulatlan | -4 |  |
| instabil | -4 | csak közelharcra! |
| folyamatosan mozog | +4 | véletlenszerűen táncol |
| fut | +5 |  |
| cikk-cakkban fut | +7 |  |
| kissé takart | +3 | egy-két testrésze nem látszik |
| félig takart | +5 |  |
| nagyrészt takart | +7 | csak egy-két testrésze látszik |


Amint látható, a támadás és védekezés dobás nagyban hasonlít egymásra.

Hárításkor a védő hátrányban van a támadóhoz képest. Ez abban is
megnyilvánul, hogy a védő **VS** és **VH** romlik a fegyverek
méretkülönbségéből adódóan:

> Hátrányban lévő **VH**-ja: **VH** - 3 x méretkülönbség

A támadás akkor sikeres, ha a **TÉ** nagyobb, mint a **VÉ**.  Ilyenkor a két
eredmény különbsége megadja a sikerek számát, ami befolyásolja a sebzést.

Amennyiben az áldozat nem vett fel védekező állást, de a harcban részt vesz,
akkor a fegyver **VH**-a nem illeti meg.

Ha az áldozat harcképtelen, vagy meglepetésből támadtak, akkor a védekező
értéke 6-os.



**Távolsági módosítók**

| max. távolság | feladat | érték | sebzés |
|---|---|---|---|
| közvetlen közel | könnyű | ~6 | maximális |
| hatótáv/4 | közepes | ~9 |  |
| hatótáv/2 | nehéz | 12 |  |
| hatótáv | nagyon nehéz | 15 |  |
| hatótáv x 2 | közel lehetetlen | 18 | fele |


#### Nem harci cselekedetek

A nem harci cselekedeteket két kategóriára bonthatjuk:

**Sebességmódosítók**

| módosító | cselekedet |
|---|---|
| 3 | futás max. 5m (nem lehet felosztani) |
| 4 | körbepillantás |
| 3 | fegyverrántás (a mesélő felülbírálhatja) |
| 2 | csőretöltés |
| 4 | tárcsere |
| 6 | ugrás (kb. 2m) |

**Szabad cselekedetek**:
Ezek a cselekedetek tulajdonsága, hogy sebességmódosítójuk 3, és végre lehet
hajtani más cselekedetek kitartása közben is.  Ilyenek például a beszéd (egy
kifejezés), hasravágódás, tárgy eldobása, stb.

**Kötött cselekedetek**:
Ezek azok a cselekedetek, amikhez koncentrálásra is szükség van, így nem lehet
más kitartott tevékenység közben végrehajtani.  Ilyenek a körbepillantás,
képzettség használata, futás, stb.

Példa sebességmódosítókat az alábbi táblázatban
találsz.

### Sebzés

Ha a támadás sikeres volt, sebzést dobhatunk:

> sebzés = **méret** x *1d* (+ sebzésmódosító) (+ támadó **ERŐ** bónusz)
- páncél **SF**

ahol minden hatodik siker után +1 sebzésmódosító jár.

Az **ERŐ** bónuszt csak közelharci fegyver sebzésébe szabad belekalkulálni.
Egyes lőfegyverek megengedik az **ERŐ** bónusz használatát (pl. mennyire tudod
felhúzni a 150 fontos íjat), de csak akkor, ha a fegyver leírása ezt
tartalmazza.

A sebzés a **fájdalomtűrés** alapképzettséget csökkenti. Ha ennek az értéke
nullára csökken, a karakter elájul.

### Kifáradás

Senki sem tud éjjel-nappal harcolni.  Előbb vagy utóbb mindenki elfárad. Ez nem
feltétlenül jelent fizikai fáradtságot: ugyanide soroltuk a fegyver
visszarúgását is.  Mindenesetre annyi bizonyos, hogy idő kell, mire az ember
kilihegi magát, vagy ismét stabilan fogja a géppuskát.

A kifáradást egyértelműen a cselekedetek okozzák.  Azt, hogy hány
fáradtságpontba is kerül egy cselekedet, azt vagy a használt fegyver mérete,
vagy az alábbi csoportosítás határozza meg:

**nem fárasztó cselekedetek**:
Ide tartoznak azok a tevékenységek, amik bár nem járnak fáradsággal, közben
mégsem lehet pihenni.  Ilyen például a célzás, tárcsere, vagy védekezés
kitartása.

**fárasztó cselekedetek**:
Ezek többnyire a mozgással járó tevékenységek, pl. hárítás, óvatosan
keresztülvágni a csatatéren.  Minden ilyen tevékenység végzése egyel növeli a
kifáradást.

**nagyon fárasztó cselekedetek**:
Ezek az intenzív izom- vagy agymunkával járó, vagy nagy koncentrációt igénylő
feladatok, mint pl. folyamatos tüzelés, varázslás.  Ilyenkor a
kifáradás kettővel csökken.

Amikor egyiket sem csináljuk (azaz pihenünk), másodpercenként (azaz négy
szegmensenként) visszakapunk egy kifáradás pontot.

A kifáradás tömbökre van osztva, és minden tömb elhasználása után egyet nő az
**MT**.  Az, hogy egy tömbbe hány kifáradás pont fér be, az a karakter **ÉGS**\
bónuszától függ:

> kifáradás tömb mérete = 6 + **ÉGS** bónusz + **ERŐ** bónusz
