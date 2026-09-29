# İlgili çalışmalar

İngilizce asıl metin: [RELATED_WORK.md](../RELATED_WORK.md). İki metin arasında
fark olursa İngilizce metin geçerlidir.

Adresler ve yayımlanmış içerik 2026-09-27 tarihinde denetlenmiştir.

## Yerleşik kalıplar ve yöntemin bağlamı

- **EA IFF 85** (Electronic Arts, 1985), dört karakterlik bir tanımlayıcı,
  big-endian uzunluk ve veriden oluşan parçaları tanımlar. Özgün belgenin bir
  kopyası:
  <https://1fish2.github.io/IFF/IFF%20docs%20with%20Commodore%20revisions/EA%20IFF%2085.pdf>
- **RIFF** (Microsoft belgeleri), hizalama kuralları dahil FOURCC
  tanımlayıcılarını, little-endian parça uzunluklarını ve veriyi tanımlar
  <https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff->
- **Conti ve diğerleri (2008), Visual Reverse Engineering of Binary and Data Files**,
  bilinmeyen ikili dosyaların incelenmesini genel bir araştırma yöntemi olarak
  ele alır. Bağlam için kaynak gösterilir, herhangi bir `.ls10` kaydına kanıt
  olarak veya bu çalışmada kullanılan bir araç olarak gösterilmez
  <https://doi.org/10.1007/978-3-540-85933-8_1>

İncelenen `.ls10` dosyaları dört baytlık bir etiket ve birçok kayıtta ardından
gelen little-endian uzunluk ile veriyi kullanır. Bu, IFF ve RIFF için tanımlanan
parça çerçevelemesine benzer. Benzerlik, doğrudan bir köken ilişkisi veya aynı
dilbilgisinin kullanıldığını kanıtlamaz.

## Quest3D biçimi üzerine önceki kamuya açık çalışmalar

Quest3D, Lumion'un geliştiricisi Act-3D B.V. şirketinin daha önceki bir motoruydu.

- **GingerLib** (GitHub kuruluşu AudiosurfResearch), depo oluşturulma tarihi
  2024-01-06, MIT lisansı.
  <https://github.com/AudiosurfResearch/GingerLib>
  Quest3D kanal grubu (`.cgr`) dosyaları için bir Rust paketi. Kaynak kodu dosyayı,
  her biri "4 karakterlik bir ad ve veri" olan etiket dizisi olarak tanımlar.
  Adın ardından 4 baytlık little-endian uzunluk gelir. Veri taşımayan `A3DG`
  etiketini dosya tanıma işareti olarak belirtir. Bu etiketten önce motor
  sürümünü taşıyan bir etiket bulunur. Ayrıca zlib ile sıkıştırılmış ve
  "korumalı" dosyaları da okur. Yayımlanmış kodu, 2026-09-27 tarihindeki
  incelemede, etiketleri bir kapsayıcı olarak okur ve yazar

- **"My Audiosurf/Quest3D reverse engineering journey"**, KC Forums,
  kullanıcı m1nt_, 2023-09-14, 2026'ya kadar yanıtlar içerir.
  <https://forum.mattkc.com/viewtopic.php?t=319>
  Act-3D B.V. tarafından geliştirilen Quest3D motorunu, kanallarını saklayan
  `.cgr` dosyalarını ve sıkıştırılmamış `.cgr` dosyalarının RIFF'e benzediği
  gözlemini anlatır

## Lumion destek sayfaları

- "Can you export 3D models from Lumion?"
  <https://support.lumion.com/hc/en-us/articles/360003475333-Can-you-export-3D-models-from-Lumion>
  Lumion proje ve sahnelerinin, içe aktarılmış modellerin, malzemelerin ve
  dokuların başka 2D veya 3D uygulamalara aktarılamadığını belirtir. Bu notlar,
  birlikte çalışabilirliğe ilişkin bu soru gözetilerek yazılmıştır
- "How do you migrate Projects and Files to Lumion 2025 and newer?"
  <https://support.lumion.com/knowledge-base/api/v2/help_center/en-us/articles/19339275362332.json>
  Lumion 12.5 ve daha eski sürümlerin proje dosyalarında `LS[ana sürüm]`,
  Lumion 2023 ve sonrasında `LSF` uzantısı kullanıldığını, Lumion 2026/2025.0 ile
  "bütün veri/dosya türleri için tamamen yeni bir dosya yapısı" getirildiğini
  belirtir. Bu notlar yalnızca `.ls10` biçimini kapsar

## Bağlam ve kaynaklar

IFF ve RIFF genel parça çerçevelemesini tanımlar. GingerLib ve KC Forums
paylaşımı, Quest3D `.cgr` dosyalarındaki ilişkili etiket yapılarını anlatır.
Bu kaynaklara, gerçekten ele aldıkları kalıplar için atıf verilir. Hiçbiri bu
nottaki `.ls10` kayıtlarının anlamını ortaya koymaz.

Bu notlar, incelenen `.ls10` projesinde gözlenen seçili kontrol sözcüklerinin
konumlarını ve instance, kanal, köşe tamponu, dünya dönüşümü ve ışık kayıtlarını
belgeler. Bayt düzeyindeki kanıtlar ve çözülmemiş alanlar METHOD.md içindeki
2. ile 7. bölümlerde verilir. Bu, gözlemlerin kaydıdır, ilk keşif veya eksiksizlik
iddiası taşımaz.

## Arama kapsamı ve sınırları

Burada listelenen kamuya açık malzemeler 2026-09-27 tarihinde incelenmiştir.
Arama, genel web kaynaklarını ve GitHub'ı kapsar, ancak her forum, Reddit veya
biçim kaydı doğrudan taranmamıştır. Kamuya kapalı çalışmalar da bulunabilir.
Bir yapının bu listede yer almaması, daha önce belgelenmediğini kanıtlamaz.
Önceki bir taslakta atıf verilen arşivlenmiş Quest3D SDK sayfası 2026-09-28
tarihinde doğrulanamadığı için teknik bir iddiada kullanılmaz.

## Kod

Bu çalışmalardan kaynak kod dahil edilmemiştir. Yukarıdaki kısa alıntıların
kaynakları belirtilmiştir.
