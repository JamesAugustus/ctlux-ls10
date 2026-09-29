# LS10 proje dosyası dilbilgisi: yöntem notları

Bu notlar, Lumion® 10 ile kaydedilmiş tek bir gerçek `.ls10` projesinden
çıkarılan dosya dilbilgisini anlatır: etiketli ikili dosyanın, genel "etiket + uzunluk + veri"
kabının ötesinde nasıl yapılandığını ve geometrinin, yüzeylerin, dünya
dönüşümlerinin ve ışık kayıtlarının bu dosyadan nasıl okunabileceğini. Çalışma,
birlikte çalışabilirlik amaçlı dosya biçimi çözümlemesidir: yalnızca kayıtlı proje
dosyaları incelenmiştir, programın kendisi incelenmemiştir.
Notlar neyin okunabildiğini, neyin okunamadığını ve bu çalışmanın kamuya açık diğer
çalışmalarla ilişkisini açıkça yazar.

Bu bağımsız çalışmanın Act-3D B.V. ile bağlantısı yoktur. Şirket tarafından
onaylanmaz veya desteklenmez. Lumion®, Act-3D B.V. şirketinin markasıdır.
Adı burada kaynak dosyaları kaydeden uygulamayı belirtir.

İngilizce asıl metin: [README.md](../README.md). İki metin arasında fark olursa
İngilizce metin geçerlidir.

## Kapsam

- Girdi: bir Lumion `.ls10` proje dosyası
- Çıktı: üçgen geometri (konumlar, normaller, iki UV kümesi), yüzey adları ve
  temel renkler, içe aktarılmış tek bir modelin dünya dönüşümü ve ışık kayıtları
  (konum, yön, tür, koni değeri, alan ışığı boyutu, göreli şiddet)
- Kapsam dışı: `.lsf` dosyaları (Lumion 2023 ve sonrası), Lumion 2025 ile gelen
  dosya yapısı, kameralar, animasyon, arazi ve fiziksel olarak ayarlanmış ışık ya
  da malzeme değerleri

## Özet

| Konu | Durum |
| --- | --- |
| Kap: 4 baytlık etiket + 32 bitlik little-endian uzunluk + veri | Bilinen bir kalıp (IFF, RIFF. Quest3D için daha önce anlatılmış, bkz. RELATED_WORK.md). Burada yalnızca `.ls10` içindeki kullanımıyla anlatılıyor |
| Uzunluk taşımayan kontrol sözcükleri | Listelenen dilbilgisi konumları için anlatılıyor |
| Instance dilbilgisi (bölümler, şema, değerler, çocuklar) | Desteklenen şemalar için anlatılıyor. Giriş taraması ve sınırlar METHOD.md, bölüm 5 ve 10'da. Bilinmeyen kanal türleri okuyucuyu durdurur |
| Kanal başlığı ve bağ çiftleri | Başlık anlatılıyor. Bağ çiftleri saklanıyor, dosya genelindeki anlamları çözülmedi |
| Köşe tamponu (konumlar, normaller, UV0, UV1, üçgenler) ve uzunluk denetimleri | Anlatılıyor |
| Yüzey adları ve temel renkler | Anlatılıyor. Gölgelendirici, cam ve UV dönüşümleri kısmi |
| Dünya matrisi, eksen dönüşümü, aynalanmış matrisler | İçe aktarılmış tek model için anlatılıyor. Birden çok modelde tampon-instance eşlemesi çözülmedi |
| Işık kayıtları | Kısmi: şiddet yalnızca göreli, renk doğrulanmadı, fotometri yok |
| Gömülü dokular | Yapılandırılmış veri saklanıyor, rolleri çözülmedi. Daha basit geometri taraması dokuları çıkarmaz |
| `.lsf` ve Lumion 2025 dosyaları | Denenmedi |

## Belgeler

- [METHOD.md](METHOD.md): dilbilgisi, kurallar, bayt düzeyinde sentetik örnek
  ve sınırlar (Türkçe)
- [METHOD.md](../METHOD.md): aynı içerik (İngilizce, asıl metin)
- [example/make_example.py](example/make_example.py): Türkçe açıklama ve çıktılarla
  sentetik örneği elle kurar ve SHA-256 özetini denetler
- [İngilizce örnek betik](../example/make_example.py): aynı sentetik baytları
  üretir, açıklamaları ve çıktıları İngilizcedir
- [RELATED_WORK.md](RELATED_WORK.md): bilinen kap kalıbı, Quest3D biçimi üzerine
  daha önceki kamuya açık çalışmalar ve bu notların farkı
- [PROVENANCE.md](PROVENANCE.md): yöntem kapsamı ve kanıt sınırları
- [LICENSE](../LICENSE): özgün notlar ve örnek betik için MIT OR Apache-2.0
- [CITATION.md](CITATION.md): bu notlara atıf bilgisi

## Çevirici

Yalnızca yöntem notlarıdır. Çalışan Python çeviricisi
[ctlux-core](https://github.com/JamesAugustus/ctlux-core) deposundadır
(MIT OR Apache-2.0). Çekirdek deponun kökünden LS10 komutu:
`python3 -B -m core input.ls10 output`. Bu depoda örnek proje dosyası,
doku, model, ekran görüntüsü veya Lumion uygulama dosyası bulunmaz.

## Geliştirme notu

Çözümleme ve bulgular yazara aittir. Yapay zekâ araçları cümle kurmada ve metni
düzenli tutmada yardımcı oldu. Dilbilgisi tek bir gerçek projeden çıkarılmıştır. Sentetik örnek,
belgelenen okuyucu kurallarını sınar (bkz. METHOD.md, bölüm 9 ve 10).

## Lisans kapsamı

Copyright (C) 2026 James Augustus

Bu depodaki özgün yöntem notları, belgeler ve varsa örnek kod dahil tüm özgün içerik **MIT OR Apache-2.0** seçeneğiyle sunulur. [MIT](../LICENSE-MIT) veya [Apache 2.0](../LICENSE-APACHE) lisanslarından birini seçebilirsiniz. Seçilen lisansın koşulları uygulanır. İkisine birden uymak gerekmez

Her iki seçenek ticari kullanıma ve kapalı ürünlerde dağıtıma izin verir. Kaynak kodunun veya özel değişikliklerin yayımlanması zorunlu değildir

- MIT seçeneğinde telif ve izin bildirimi yazılımın tüm kopyalarında veya önemli bölümlerinde korunur
- Apache 2.0 seçeneğinde alıcılara lisans verilir, değiştirilen dosyalar belirgin bildirimlerle işaretlenir ve ilgili kaynak bildirimleri 4. bölüm uyarınca korunur
- Apache 2.0 seçeneğinde ilgili [NOTICE](../NOTICE) atfı dağıtılan NOTICE dosyası veya belgeler gibi 4(d) bölümünün izin verdiği bir yerde sunulur
- MIT seçildiğinde Apache NOTICE koşulları uygulanmaz

Her iki seçenek ilgili telif bildirimlerini korur. Reklam atfı, özel bir kullanıcı arayüzü atfı veya akademik atıf zorunluluğu getirmez

Üçüncü taraf alıntıları, kodları ve markaları kendi koşullarını korur ve bu bildirimle yeniden lisanslanmaz. Yalnız özgün içerikte sahip olunan haklar verilir. Fikirler, yöntemler ve dosya biçimi olguları üzerinde bu lisanslarla münhasır telif hakkı kurulmaz. Yalnız bu fikir veya olgularla hazırlanan bağımsız uygulamalarda bilimsel kaynak gösterme gönüllüdür ve [CITATION.md](CITATION.md) içinde rica edilir
