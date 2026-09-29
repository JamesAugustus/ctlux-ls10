# Yöntem

İngilizce asıl metin: [METHOD.md](../METHOD.md). İki metin arasında fark olursa
İngilizce metin geçerlidir.

Gösterim: bütün tam sayılar ve kayan noktalı sayılar little-endian'dır
(düşük anlamlı bayt önce yazılır). `u32` işaretsiz 32 bitlik tam sayı, `f32`
IEEE 754 biçiminde 32 bitlik kayan noktalı sayı, `i16` işaretli 16 bitlik tam sayıdır. *Etiket* dört ASCII bayttır.
`p` okunmamış bir sonraki baytın konumu, `N` dosyanın boyutudur. Metinler
UTF-16LE'dir.

## 1. Dosya kapsayıcısı

Temel birim parçadır (chunk):

```
konum p       p+4          p+8                 p+8+n
| etiket (4B) | n (u32)    | veri (n bayt)     | sonraki öğe
```

- Sınır kuralı: önce `0 <= p <= N` koşulunu doğrulayın. Ardından parçayı
  yalnızca `N - p >= 8` ve `n <= N - p - 8` ise kabul edin. Sabit genişlikli tam sayı kullanan kodda, `p + 8 + n` toplamını
  hesaplamadan önce bu sırayla karşılaştırın, böylece toplam hiçbir zaman sınır
  dışında oluşmaz
- Verinin konumu `p + 8`'dir, `p` değil. Konumları kaydederken ikisini ayrı tutun
- Dosya, düz bir parça listesi değildir. Bir parçadan sonra ne geleceği dilbilgisi
  konumuna bağlıdır (bölüm 2-4), bu yüzden dosya etiket etiket yürünerek değil,
  dilbilgisine göre okunmalıdır
- Tür kimlikleri ham 16 baytlık değerlerdir. Bu yöntem onları bayt olarak
  (onaltılık) karşılaştırır ve UUID metin biçimine göre yeniden sıralamaz

"Etiket + uzunluk + veri" kalıbının kendisi iyi bilinir (IFF, RIFF) ve daha önceki
Quest3D kanal grubu biçiminde de kullanılmıştır. Bkz. RELATED_WORK.md.

## 2. Uzunluk taşımayan kontrol sözcükleri

Bazı etiketler *kontrol sözcüğüdür*: dört bayt, başka hiçbir şey yok. Dilbilgisi
konumlarında dört bayt olarak tüketilirler. Ardından uzunluk gelmez.

Çocuk (İng. child): bir alana bağlı alt kanal. Çocuk kayıtları, bölümdeki
bütün değer kayıtlarından sonra aynı alan sırasıyla okunur.

| Kontrol sözcüğü | Görevi |
| --- | --- |
| `ICSI`, `ICIF` | şemanın başı ve sonu |
| `INIT`, `IIIS` | alan tanımının ad bölümünün başı ve sonu |
| `IFSI`, `IFNS` | bir değer ya da çocuk için "var" / "yok" işareti |
| `ENDL` | bir değerin sonu |
| `ENDI` | bir sınıf bölümünün sonu |
| `^EN^` | sonlandırılmış bir instance'ın sonu |
| `CHAC`, `OCHA` | çocuk kanal geliyor / çocuk kanal yok |
| `SKDA` | boş kanal |
| `ISP2` | tek instance'lı kanal gövdesinin başı |
| `NOIS` | o gövdede instance yok |

**Neden önemli.** Her etiketten sonra uzunluk okuyan bir okuyucu, ilk kontrol
sözcüğünde adımını şaşırır: bir sonraki etiketin dört baytını uzunluk sanar ve
yanlış bir yere atlar. Sentetik örnekte (bölüm 9) böyle bir okuyucu 76. konumda
(`ICSI`) durur. Ardından gelen `INIC` etiketinin baytlarını 1128877641 uzunluğu
olarak okumuştur.

## 3. Instance dilbilgisi

Instance, dosyada bir nesnenin (model, yüzey, ışık vb.) kaydıdır.

```
Instance
  ICUD   parça (üstveri)
  ICIC   parça, u32 = sınıf bölümü sayısı (S)
  Bölüm x S
    ICTD   parça, 16 baytlık tür kimliği
    Şema
      ICSI
      INIC   parça, u32 = alan sayısı (F)
      Alan tanımı x F
        INIT
        parçalar ... IINW dahil (alan adı, UTF-16LE)
        IIIS
        IIOM   parça
        IIIT   parça, isteğe bağlı
      ICIF
    Değer x F            (bütün değerler)
      IFNS                                  değer yok
      IFSI  IIOM-parçası  <değer>  ENDL
    Çocuk x F            (sonra bütün çocuklar, aynı alan sırasıyla)
      IFNS                                  çocuk yok
      IFSI  OCHA                            kanal yok
      IFSI  CHAC  <kanal>                   bölüm 4
    ENDI
  ^EN^                   (yalnızca sonlandırılmış instance için)
```

Kurallar:

- **Bütün değerler bütün çocuklardan önce gelir**, aynı alan sırasıyla. Bir alanın
  çocuğunu değerinin hemen ardından okumak bölümü yanlış okur. Yanlış sıra her
  zaman fark edilmez: sentetik örnekte (bölüm 9) iki sıra da aynı baytları verir,
  çünkü ilgili iki işaretin ikisi de `IFNS`'tir. Sıra, deneyerek okumadan değil,
  dilbilgisinden gelmelidir
- Değer biçimleri: `IIVE` (4 bayt, bir f32), `IIV1` (16 bayt, dört f32), `IIM1`
  (64 bayt, on altı f32), `CHIT` ile başlayan bir `Text` kanalı ya da yorumlanmayan
  16 baytlık bir tür başvurusu. Sonlu olmayan sayılar reddedilir
- Tür başvurusu, etiketi ve uzunluğu olmayan 16 ham bayttır. Sıradaki dört bayt
  `IIVE`, `IIV1`, `IIM1` ya da `CHIT` değilse okunur. Yanlış okumaya karşı koruma
  olarak ardından `ENDL` gelmek zorundadır
- Başvuru çeviricisi, `IINW` içindeki alan adını ilk NUL karakterine kadar, NUL
  yoksa verinin sonuna kadar okur. İncelenen projede `IINW` sabit veri
  boyutundaydı. Adın ardında dolgu vardı
- Bir instance'ın bölümleri tek bir alan kümesinde birleştirilir. İki bölümün aynı
  alan adını vermesi hatadır. Bölüm sınırları korunur
- Okuyucunun kabul kotaları şunlardı: 1-16 bölüm, en çok 128 alan, bir alan
  tanımında en çok 12 parça, üstveri parçaları en çok 4096 bayt, bir kanalda en çok
  64 `CHLC` bağ çifti ve en çok 64 `ICLL` liste öğesi. Bunlar
  okuyucunun sınırlarıdır, biçimin bilinen sınırları değildir

## 4. Kanallar

`SKDA`, `CHAC` sonrasında bir kanal beklendiği yerde tek başına gelir. Kanal
başlığının ve gövdesinin tamamının yerini alır.

Kanal başlığı şudur: `CHIT` (u32), `CHNW` (kanal türünün adı, UTF-16LE), ikinci
bir `CHIT` (u32), `CHLC` (u32 = bağ sayısı L), ardından L çift `CHLI` (u32) ve
`CHUL` (u32). Bağ çiftleri okunduğu gibi saklanır. Dosya genelindeki anlamları
çözülmemiştir. İki `CHIT` değeri yorumlanmaz.

| Kanal türü | Gövde |
| --- | --- |
| `Text` | `STWA` (UTF-16LE metin), `STLR` |
| `OO Class Instances List` | `ICSD`, `ICLL` (u32 sayı), ardından o kadar sonlandırılmış instance |
| `OO ClassInstance`, `ClassInstance->...` | `ISP2`, `ICSD`, ardından `NOIS` ya da sonlandırılmamış bir instance |
| `Vertex Data` | köşe özniteliği ve indeks parçaları (aşağıda) |
| `3D ObjectData` | `VRCO` = 0, ardından sabit sırayla `MBCT`, `POCO`, `POTY`, `PONM`, `POTT`, `POSO`, `PUAV`, `PSRV`. Her parça en çok 4096 bayttır ve içeriği yorumlanmaz. Sıfırdan farklı bir sayı (geometri başka yerde) çözülmemiştir ve okuyucuyu durdurur |
| `Texture` | `TEXW`, `TEXH` (u32 genişlik, yükseklik), `TEXS` (u32 boyut), `TEXT` (veri) ve isteğe bağlı alanlar. `TEXS`, `TEXT` uzunluğuna eşit olmalıdır |

Başka herhangi bir kanal türü okuyucuyu hatayla durdurur. Kanallar ve instance'lar
her iç içe düzeyde bir artan tek bir ortak derinlik sayacını paylaşır. Derinliği
12'nin üstündeki bir kanal ya da 16'nın üstündeki bir instance okuyucuyu durdurur.

**Vertex Data (köşe verisi).** `V` = köşe sayısı olmak üzere:

| Etiket | İçerik | Veri uzunluğu |
| --- | --- | --- |
| `VRCO` | köşe sayısı V | u32 |
| `VPPI` | konumlar, köşe başına 3 x f32 | 12 V |
| `VNNI` | normaller, köşe başına 3 x i16 (işaretli, normalize. Yön, normalize edilmiş vektördür) | 6 V |
| `VTD0` | UV kümesi 0, 2 x f32 | 8 V |
| `VTD1` | UV kümesi 1, 2 x f32 | 8 V |
| `PO32` | üçgenler, 3 x u32 indeks | 12'nin katı |
| `VTO0`, `VTO1` | UV dönüşümü, küme başına 6 x f32 (birim `0 0 0 0 1 1`) | 24 |

Ayrıştırıcı her etiketin en çok bir kez bulunmasını denetler. `VRCO`, `VPPI`,
`VNNI`, `VTD0`, `VTD1` ve `PO32` etiketlerini zorunlu tutar ve öznitelik
uzunluklarını V'ye göre doğrular. Yapılandırılmış dışa aktarıcı her indeksin
V'den küçük olduğunu denetler, sonlu olmayan konum, UV0, UV1 ve UV dönüşümü
değerlerini reddeder. Doğrulamadan sonra UV1'i ham baytlar olarak korur. `VTO0`
ve `VTO1` ayrıştırıcı için isteğe bağlıdır, yapılandırılmış OBJ dışa aktarıcısı
ise ikisini de ister. `PO32` uzunluğunun 12'nin katı olması yalnızca verinin
üçgenlere bölündüğünü gösterir. İndekslerin sınır içinde olduğunu kanıtlamaz.

Aynı konumda görülen öbür etiketler (`VTTB`, `MBCT`, `POCO`, `POTY`, `PONM`,
`POTT`, `POSO`, `PUAV`, `PSRV`) kabul edilir ve saklanır, ama burada yorumlanmaz.

**Gövdenin sonu.** `Vertex Data` gövdesinin kendine ait bir sayacı ya da bitiş
işareti yoktur. Okuyucu, sıradaki dört bayt bu bölümde adı geçen köşe
etiketlerinden biri olduğu sürece (yorumlananlar ve yorumlanmayanlar) parça
okumayı sürdürür. Gövde, bu kümenin dışındaki ilk dört baytta biter. Etiketler
herhangi bir sırada gelebilir.

**Texture gövdesi.** Aynı biçimde okunur. Etiket kümesi `TEXM`, `TEXW`, `TEXH`,
`TEPU`, `TEXS`, `TEXT`, `TENT`, `TECM`, `TEGC`, `TEOW`, `TELM`, `RWEN`'dir ve her
biri en çok bir kez bulunur. `TEXW`, `TEXH`, `TEXS` ve `TEXT` zorunludur. Öbürleri
isteğe bağlıdır ve yorumlanmadan saklanır.

## 5. Yüzeyler ve malzemeler

Başvuru çeviricisi dosyayı ilk bayttan başlayarak çözümlemez. Yüzey instance'larını
başlangıç kalıbını arayarak bulur: 32 bayt verili `ICUD`, ardından 4 bayt verili
`ICIC`, ardından yüzey tür kimliğini içeren 16 bayt verili `ICTD`.

Yüzey, sınıf bölümünde belirli bir 16 baytlık tür kimliği bulunan ve `ObjectData`
çocuğu bir `Vertex Data` kanalı olan instance'tır. Alanları arasında `surfaceNr`,
`surfaceName` ve `Diffuse` (dört f32. 1-3. bileşenler temel renk olarak kullanılır)
vardır. Yüzey numaraları tek olmalıdır.

Malzeme süzgeci instance'ları (başka bir tür kimliği), bir yüzey adıyla eşleşen
`materialname` alanını ve `materialInfo` çocuğunu taşır. Bu çocuğun `color` alanı
(dört f32) varsa görüntü rengi olarak kullanılır. Bu rengin dördüncü bileşeni
opaklık olarak **yorumlanmaz**. Anlamı belirlenememiştir. Cam ayarları ve öbür
gölgelendirici parametreleri okunduğu gibi saklanır, yorumlanmaz.

Gözlenen yüzey türü kimliği `fd1c729ffb00b74ea24200c2ba2db89b`,
malzeme filtresi türü kimliği `daf0495380ebbe4497e19680ea2238d9`
değeridir. Çalışan okuyucu bunları
`ctlux-core/core/tools/ls10_surface.py` içinde kullanır.

## 6. Dünya matrisi ve eksenler

**Matris.** `IIM1` 16 adet f32 değer taşır: `M[0..15]`. Bir `v = (x, y, z)` noktası
şuna eşlenir:

```
w_j = v.x * M[j] + v.y * M[j+4] + v.z * M[j+8] + M[j+12]        j = 0, 1, 2
```

Bu, satır vektörü çarpı satır öncelikli matristir. Öteleme son satırdadır (`M[12]`,
`M[13]`, `M[14]`). Aynı 16 sayı sütun öncelikli okununca matrisin devriği elde
edilir ve sütun vektörüyle kullanılır. İki okuma aynı sonucu verir. Matris yalnızca
`M[3]`, `M[7]`, `M[11]` için sıfırdan ve `M[15]` için birden sapma en
fazla `1e-6` ise, bütün değerler sonluysa ve 3 x 3 determinantının mutlak
değeri en az `1e-20` ise kabul edilir.

**Hangi matris.** İçe aktarılmış bir modelin dünya matrisi,
`ClassType->cCustomObject` bölümündeki (bu UTF-16LE metinden bir sonraki
`ClassType->` metnine kadar) 64 baytlık `IIM1` değerinden alındı, o da yalnızca
bölüm `world` UTF-16LE metnini de içeriyorsa. Bu, yalnızca dosyada tam bir tane
böyle bölüm ve tam bir tane `ClassInstance->cImportObject` bulunduğunda yapıldı.
Birden çok modelde köşe tamponları ile model instance'ları arasındaki bağ
çözülmedi ve hiçbir matris tahmin edilmez.

**Normaller**, 3 x 3 kısmın ters devriğiyle (inverse transpose) dönüştürülür ve
sonra normalize edilir. Normallere konum matrisini uygulamak, eşit olmayan
ölçekleme ya da kayma varken yanlıştır.

**Aynalama.** 3 x 3 kısmın determinantı negatifse, yüzlerin yönünü korumak için
her üçgenin ikinci ve üçüncü indeksi yer değiştirir.

**Eksenler.** Lumion® uzayında Y yukarıdır. Z'nin yukarı olduğu bir hedefe (örneğin
Radiance) noktalar, normaller ve yönler `(x, y, z) -> (x, -z, y)` olarak eşlenir.
Bu, dünya matrisinden sonra uygulanır. İncelenen projede birimler metreydi ve
saklanan normaller sağ elli, saat yönünün tersine üçgen sarımıyla uyumluydu.

**Hassasiyet.** Yalnızca tam olarak eşit köşeler birleştirilir: konum, UV ve normal
için ayrı ayrı. Böylece UV dikişleri ve sert kenarlar korunur. Uzaklık eşiği
kullanılmaz. Kaba bir ızgara ince yüzleri silebilir. Koordinatlar 17 anlamlı
basamakla yazılır.

**Daha basit yol.** Yukarıdaki koşullar sağlanmadığında daha dar bir tarama
kullanıldı: `VPPI`'yi bul, sonra bir sonraki `PO32`'yi bul, arada başka bir `VPPI`
varsa çifti atla, uzunlukların 12'nin katı olduğunu, her indeksin köşe sayısından
küçük olduğunu ve konumların sonlu olduğunu denetle. Bu yol normalleri, UV'leri ve
adları okumaz.

## 7. Işık kayıtları

Bir ışık bloğu `cLightObject` UTF-16LE metninde başlar ve bir sonrakine kadar
sürer. Değerler bölüm 3 dilbilgisiyle değil, blok içinde `IIVE` (4 bayt), `IIV1`
(16 bayt) ve `IIM1` (64 bayt) aranarak sırayla toplanır. Uzunluğu yanlış parçalar
ve kabul edilmiş verinin içine düşen eşleşmeler atlanır. Değer parçasına benzeyen
rastgele baytlar da toplanabilir. 37'den az değeri olan bloklar atlanır.

Bloğun şema kısmı da değer içerir, bu yüzden blok başından saymak kararlı değildir.
En baştaki `IIM1` 3. alandır. `n` toplanan değer sayısı, `j` bu çapanın sıfırdan
sayılan sırası ise `k`. alan `j + (k - 3)` sırasındadır ve ancak `j + (k - 3) < n`
ise vardır. Toplam 37 değer bunu garanti etmez.

| Alan | Etiket | Bu yöntemdeki kullanımı |
| --- | --- | --- |
| 3 | `IIM1` | dünya matrisi: konum `M[12..14]`, yön `M[8..10]` (yerel z ekseninin görüntüsü) |
| 26 | `IIVE` | koni değeri, 6.3'ten küçükse radyan, değilse derece sayılır. Tam açı mı yarım açı mı olduğu doğrulanmadı |
| 28 | `IIV1` | vektör: 1-3. bileşenlerin uzunluğu **göreli** şiddet olarak kullanılır |
| 35, 36 | `IIVE` | alan ışığının genişliği ve yüksekliği |
| 37 | `IIVE` | ışık türü: 0, 1 ve 3 değerleri görüldü ve spot, noktasal (omni) ve alan olarak okunuyor |

Açıkça:

- Başvuru çeviricisi okunamayan bir ışık alanında durmaz. Beklenen yerde değer
  yoksa ya da başka etiket taşıyorsa varsayılan kullanır: tür 0, koni 1.0,
  boyut 1.0 x 1.0 ve vektör yerine beyaz `(1, 1, 1)`. Her eksik veya yanlış
  etiketli alan ve kullanılan varsayılan değer bir uyarıyla belirtilir
- **Şiddet görelidir.** Başvuru çeviricisinde varsayılanı 200 olan ve komut
  satırından ayarlanamayan bir ayar sabitine bölünür. Fotometrik bir büyüklük
  değildir. **Fotometri iddiası yoktur**
- **Renk doğrulanmamıştır.** 28. alandaki vektör rengi kodluyor olabilir, ama bu
  doğrulanmadı. Varsayılan olarak nötr beyaz kullanılır
- Tür değerleri, kayıtların öbür alanlarından (koni, boyut, gölge ayarları)
  yorumlandı. Programla karşılaştırılarak doğrulanmadı
- Başvuru çeviricisi 0, 1 ve 3 dışındaki tür değerlerini spot sayar
- Başvuru çeviricisi "radyan mı derece mi" kuralından sonra koni açısını 10 ile 160
  derece aralığıyla sınırlar
- Yakın iki ışık varsayılan olarak hiçbir zaman birleştirilmez. Yakın kayıtlar
  bağımsız ışıklar olabilir

## 8. Gömülü dokular

Yapılandırılmış yolda `Texture` kanalları genişliği, yüksekliği ve ham veriyi
verir. Veri, özet değeriyle birlikte saklanır. Bir dokunun rolü (örneğin temel
renk) çözülmedi ve tahmin edilmez. Yapılandırılmış dışa aktarıcıda dosya uzantısı
verinin imzasına göre seçilir. Daha basit geometri tarama yolu dokuları çıkarmaz.

## 9. Sentetik örnek

Aşağıdaki baytlar kısa bir betikle elle kuruldu. **Hiçbir bayt gerçek bir proje
dosyasından gelmez.** Tür kimliği bir yer tutucudur (`0x11` x 16), gerçek bir
Lumion kimliği değildir. `a` ve `g` alan adları uydurmadır. Örnek, iki alanlı,
sonlandırılmış tek bir instance'tır: `a` alanının dört ondalık sayılık bir değeri
vardır ve çocuğu yoktur. `g` alanının değeri yoktur ve tek üçgenli bir
`Vertex Data` çocuğu vardır.

| Konum | Öğe | Bayt | Onaltılık |
| ---: | --- | ---: | --- |
| 0 | ICUD | 40 | `49 43 55 44 20 00 00 00` + 32 x `00` |
| 40 | ICIC | 12 | `49 43 49 43 04 00 00 00 01 00 00 00` |
| 52 | ICTD | 24 | `49 43 54 44 10 00 00 00` + 16 x `11` |
| 76 | ICSI | 4 | `49 43 53 49` |
| 80 | INIC | 12 | `49 4e 49 43 04 00 00 00 02 00 00 00` |
| 92 | INIT | 4 | `49 4e 49 54` |
| 96 | IINW | 10 | `49 49 4e 57 02 00 00 00 61 00` |
| 106 | IIIS | 4 | `49 49 49 53` |
| 110 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 118 | INIT | 4 | `49 4e 49 54` |
| 122 | IINW | 10 | `49 49 4e 57 02 00 00 00 67 00` |
| 132 | IIIS | 4 | `49 49 49 53` |
| 136 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 144 | ICIF | 4 | `49 43 49 46` |
| 148 | IFSI | 4 | `49 46 53 49` |
| 152 | IIOM | 8 | `49 49 4f 4d 00 00 00 00` |
| 160 | IIV1 | 24 | `49 49 56 31 10 00 00 00 00 00 00 3f 00 00 80 3e 00 00 00 3e 00 00 80 3f` |
| 184 | ENDL | 4 | `45 4e 44 4c` |
| 188 | IFNS | 4 | `49 46 4e 53` |
| 192 | IFNS | 4 | `49 46 4e 53` |
| 196 | IFSI | 4 | `49 46 53 49` |
| 200 | CHAC | 4 | `43 48 41 43` |
| 204 | CHIT | 12 | `43 48 49 54 04 00 00 00 01 00 00 00` |
| 216 | CHNW | 30 | `43 48 4e 57 16 00 00 00` + UTF-16LE `Vertex Data` |
| 246 | CHIT | 12 | `43 48 49 54 04 00 00 00 01 00 00 00` |
| 258 | CHLC | 12 | `43 48 4c 43 04 00 00 00 01 00 00 00` |
| 270 | CHLI | 12 | `43 48 4c 49 04 00 00 00 00 00 00 00` |
| 282 | CHUL | 12 | `43 48 55 4c 04 00 00 00 00 00 00 00` |
| 294 | VRCO | 12 | `56 52 43 4f 04 00 00 00 03 00 00 00` |
| 306 | VPPI | 44 | `56 50 50 49 24 00 00 00` + f32 `0 0 0  1 0 0  0 1 0` |
| 350 | VNNI | 26 | `56 4e 4e 49 12 00 00 00` + i16 `0 0 32767` x 3 |
| 376 | VTD0 | 32 | `56 54 44 30 18 00 00 00` + f32 `0 0  1 0  0 1` |
| 408 | VTD1 | 32 | `56 54 44 31 18 00 00 00` + f32 `0 0  1 0  0 1` |
| 440 | PO32 | 20 | `50 4f 33 32 0c 00 00 00 00 00 00 00 01 00 00 00 02 00 00 00` |
| 460 | ENDI | 4 | `45 4e 44 49` |
| 464 | ^EN^ | 4 | `5e 45 4e 5e` |

Toplam 468 bayt, SHA-256
`5182482876d8004c734360c8b6d196e5ddef7265f56fcb3393b5fc722145465b`.
[example/make_example.py](example/make_example.py) betiği bu baytları kurar ve
SHA-256 özetini denetler, böylece örnek yeniden üretilebilir.
`61 00` ve `67 00`, UTF-16LE'de `a` ve `g` harfleridir. `00 00 00 3f`, f32 0.5'tir.
Örnekteki adlarda NUL karakteri yoktur. Adlar verinin sonunda biter.

Yukarıdaki dilbilgisiyle okunduğunda 468 baytın tamamı tüketilir ve şunlar elde
edilir: alanlar `a = (0.5, 0.25, 0.125, 1.0)` ve `g` = yok, çocuklar `a` = yok ve
`g` = 3 köşeli, tek bağ çifti `(0, 0)` olan, tampon uzunlukları 36, 18, 24, 24 ve
12 olan bir `Vertex Data` kanalı. Daha basit `VPPI` -> `PO32` taraması aynı üçgeni
okur. Bozulmuş üç kopya reddedilmelidir ve reddedilmiştir:

- `ICUD` uzunluğu 468 yapıldı: "parça uzunluğu kaynağın dışında"
- sondaki `^EN^` çıkarıldı: 464. konumda "`^EN^` bekleniyordu"
- `VPPI` iki köşeye kısaltıldı: "köşe özniteliği sayısı uyuşmuyor"

Bir okuyucu, gerçek dosyalarda kullanılmadan önce geçerli örneği kabul etmeli ve
bozulmuş üç kopyanın hepsini reddetmelidir.

## 10. Sınırlar

- Bu notlar tam bir dosya belirtimi değildir. Burada anlatılmayan bir durumla
  karşılaşan okuyucu durmalıdır
- Yalnızca `.ls10` proje dosyaları (Lumion 10) incelendi ve çıkarım tek bir gerçek
  projeye dayandı. `.lsf` dosyaları (Lumion 2023 ve sonrası) ve Lumion 2025 için
  duyurulan yeni dosya yapısı denenmedi
- Dilbilgisi, desteklenen şemaları ve kanal türlerini kapsar. Öbürleri okuyucuyu
  durdurur. Girdinin sonuna ulaşmak, her anlamın çözüldüğü anlamına gelmez
- Birden çok model içeren dosyalarda köşe tamponları ile model instance'ları
  arasındaki eşleme tam çözülmedi. Dünya matrisi yalnızca tek modelli durumda
  kullanılır
- Kanal bağ çiftleri saklanır, ama dosya genelinde çözülmemiştir
- Eksik ya da yanlış etiketli ışık alanları için başvuru çeviricisi varsayılan
  değerler kullanır (bölüm 7) ve dönüşümü durdurmak yerine her varsayımı bildirir
- Işıklar: şiddet görelidir, renk doğrulanmamıştır, koni açısının hangi ölçüye göre
  verildiği doğrulanmamıştır ve fotometri iddiası yoktur. Koni değeri için
  kullanılan "radyan mı derece mi" kuralı, derece olarak saklanmış ve 6.3'ten
  küçük bir koniyi yanlış okur: 5 derecelik bir spot 5 radyan (yaklaşık 286 derece)
  sanılır ve ardından 160 dereceyle sınırlanır
- Başvuru çeviricisi Lumion proje uzantısı olarak yalnızca `.ls10` kabul eder.
  Diğer sürümler ve uzantılar doğrulanmamıştır
- Birimden farklı UV dönüşümleri bildirilir, uygulanmaz. Doku rolleri, cam ve
  gölgelendirici parametreleri yorumlanmaz
- Daha basit geometri tarama yolu gömülü dokuları çıkarmaz
- Alan sıraları ve kotalar gözlenen sürümde belirlenmiştir. Başka sürümler farklı
  olabilir. Beklenmeyen veri, tahmin yürütmek yerine okuyucuyu durdurmalıdır

## Bağımsızlık ve markalar

Bağımsız bir çalışmadır. Act-3D B.V. ile bağlantılı değildir, onun tarafından
onaylanmamıştır ve desteklenmemektedir. Lumion®, Act-3D B.V. şirketinin
markasıdır. Ürün adları yalnızca söz edilen biçimleri ve programları tanımlar.
