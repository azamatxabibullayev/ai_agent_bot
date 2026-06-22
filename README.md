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
<img width="562" height="457" alt="image" src="https://github.com/user-attachments/assets/8b73058f-1033-489c-91ea-1de94735df67" />
<img width="541" height="363" alt="image" src="https://github.com/user-attachments/assets/68fa527b-4b93-436d-a4ac-c3c92251770b" />
<img width="571" height="297" alt="image" src="https://github.com/user-attachments/assets/36a13d08-f9cd-4b4c-ac4b-53f79d9578f7" />


---

### Admin Panel Interfeysi
<img width="527" height="692" alt="image" src="https://github.com/user-attachments/assets/944fdc8f-fd0f-41c5-9235-9775a4591c82" />


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
