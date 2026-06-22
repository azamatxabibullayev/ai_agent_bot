# 📱 TechShop AI Agent Bot

Ushbu Telegram bot "TechShop" smartfonlar do'koni uchun sun'iy intellekt asosida ishlaydigan virtual sotuvchi hisoblanadi. Bot mijozlar bilan xuddi haqiqiy odamdek muloqot qiladi, do'kondagi telefonlarni tavsiya etadi va buyurtmalarni avtomatik qabul qiladi.

---

## 🛠️ Bot nima ishlar qila oladi?

* **Aqlli Sotuvchi Tizimi:** Mijozlarning "iPhone yoki Samsung yaxshimi?" kabi umumiy savollariga qisqa javob berib, darhol gapni do'kondagi mavjud modellarni sotishga buradi.
* **Avtomatik Buyurtma Qabul Qilish:** Mijoz telefon sotib olishga rozi bo'lsa, uning Ismi, Telefon raqami va Manzilini qisqa qilib so'rab oladi va ma'lumotlarni bazaga saqlaydi.
* **Begona Mavzularni Cheklash:** Agar mijoz do'kondan tashqari (ob-havo, ovqatlar, siyosat va hk) mavzularda yozsa, xushmuomalalik bilan faqat telefonlar bo'yicha yordam bera olishini eslatadi.
* **Token va Limit Tejamkorligi:** Bitta tekin API kalit tezda tugab qolmasligi uchun faqat oxirgi 4 ta xabarni eslab qoladi va bazadagi faqat eng asosiy 5 ta mahsulotni AIga taqdim etadi.
* **Chiroyli Formatlash:** Javoblarda hech qanday yulduzchalar (*), panjaralar (#) yoki minus (-) belgilari ishlatilmaydi. Oddiy va tushunarli abzaslar bilan javob beradi.

---

## 🖼️ Botdan Ko'rinish (Skrinshotlar)

### Foydalanuvchi (User) Interfeysi
> *Bu yerga foydalanuvchi bot bilan muloqot qilayotgani aks etgan skrinshotni joylashtiring.*

*(Skrinshotingizni shu yerga qo'ying)*

---

### Admin Panel Interfeysi
> *Bu yerga do'kon admin paneli yoki buyurtmalar ro'yxati aks etgan skrinshotni joylashtiring.*

*(Skrinshotingizni shu yerga qo'ying)*

---

## 🚀 Botni Ishga Tushirish Qo'llanmasi

Loyihani birinchi marta yoki keshni tozalab muammosiz ishga tushirish uchun quyidagi buyruqlarni terminalda ketma-ket bajaring:

```bash
# 1. Docker keshini tozalash (Extraction snapshot xatoliklarini oldini olish uchun)
docker builder prune -f

# 2. Konteynerlarni to'liq o'chirish
docker-compose down

# 3. Keshsiz (no-cache) yangidan build qilish
docker-compose build --no-cache

# 4. Botni orqa fonda (background) ishga tushirish
docker-compose up -d
⚙️ Foydali Docker Buyruqlari
Botni to'xtatish: docker-compose down

Botni qayta yuklash (Restart): docker-compose restart bot

Xatoliklar va Loglarni kuzatish: docker-compose logs -f bot