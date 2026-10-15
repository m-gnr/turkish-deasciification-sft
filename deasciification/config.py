"""Model kimliği ve ortak görev yönergesi."""

MODEL = "Qwen/Qwen3-1.7B"
REVISION = "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
YONERGE = (
    "Metindeki eksik Türkçe karakterleri bağlama göre geri yükle. "
    "Yalnızca şu dönüşümlere izin ver: c→ç, C→Ç, g→ğ, G→Ğ, "
    "i→ı, I→İ, o→ö, O→Ö, s→ş, S→Ş, u→ü, U→Ü. "
    "Gerekmeyen harfleri değiştirme. Diğer karakterleri, mevcut Türkçe "
    "harfleri, boşlukları ve noktalama işaretlerini aynen koru. "
    "Yazım hatalarını düzeltme. Yalnızca sonuç metnini yaz; "
    "açıklama veya tırnak ekleme."
)

