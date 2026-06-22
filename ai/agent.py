import os
import json
import re
from typing import Optional, List, Dict, Any
# 🛠️ Yangi SDK importlari
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 🛠️ Yangi Client yaratish (Chaqiruvlar client orqali bo'ladi)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)


def build_system_prompt(products_info: str) -> str:
    return f"""Sen "TechShop" do'konining aqlli savdo assistentisan. Sening vazifang - mijozlardan telefon va boshqa texnika buyurtmalarini qabul qilish.

## DO'KONDAGI MAVJUD MAHSULOTLAR:
{products_info}

## SENING VAZIFANG:
1. Mijozlarni do'sona munosabat bilan kutib ol
2. Ular nima istayotganini tushun
3. Ombordagi mahsulotlar asosida eng mos variantni taklif qil
4. Agar so'ragan mahsulot bo'lsa - taklif qil, bo'lmasa - o'xshash variantlarni ko'rsat
5. Buyurtmani rasmiylashtirish uchun quyidagilarni yig':
   - Ismi, familiyasi
   - Telefon raqami
   - Yetkazib berish manzili (yoki o'zi olib ketishi)
   - Tanlagan mahsulot va miqdori

## MUHIM QOIDALAR:
- FAQAT omborda bor mahsulotlarni taklif qil
- Narxlarni aniq ayt (so'm hisobida)
- Mijoz ma'lumotlarini to'liq yig'gandan keyin buyurtmani tasdiqlashni so'ra
- Doim o'zbek tilida gaplash
- Samimiy va professional bo'l
- Agar mijoz boshqa tilda yozsa, shu tilda javob ber

## BUYURTMA TASDIQLASH:
Barcha ma'lumotlar yig'ilganda, javobni AYNAN quyidagi JSON formatida yakunla:

===ORDER_DATA===
{{
  "ready": true,
  "product_name": "mahsulot nomi",
  "product_id": null,
  "quantity": 1,
  "customer_name": "Ism Familiya",
  "customer_phone": "+998901234567",
  "customer_address": "manzil yoki 'O'zi olib ketadi'",
  "summary": "Buyurtma xulosasi"
}}
===END_ORDER===

Agar ma'lumotlar to'liq bo'lmasa, "ready": false qo'y va yetishmayotgan ma'lumotni so'ra.
Agar buyurtma yo'q bo'lsa (faqat savol-javob), JSON blokni umuman qo'shma.
"""


def parse_order_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    pattern = r"===ORDER_DATA===\s*(.*?)\s*===END_ORDER==="
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        try:
            order_data = json.loads(match.group(1).strip())
            return order_data
        except json.JSONDecodeError:
            return None
    return None


def clean_response_text(response_text: str) -> str:
    pattern = r"===ORDER_DATA===.*?===END_ORDER==="
    cleaned = re.sub(pattern, "", response_text, flags=re.DOTALL)
    return cleaned.strip()


class AIAgent:
    def __init__(self):
        # Yangi SDKda model nomi string ko'rinishida beriladi
        self.model_name = "gemini-1.5-flash"

    async def get_response(
            self,
            user_message: str,
            conversation_history: List[Dict[str, str]],
            products_info: str,
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        system_prompt = build_system_prompt(products_info)

        # 🛠️ Yangi SDK talab qiladigan tarix (Contents format)
        contents = []
        for msg in conversation_history[:-1]:  # Oxirgi xabardan tashqari hammasi tarixga
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["message"])]
                )
            )

        # 🛠️ Tizimli prompt va joriy foydalanuvchi xabarini birlashtirib oxiriga qo'shamiz
        full_message = f"{system_prompt}\n\n---\nMijoz xabari: {user_message}"
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=full_message)]
            )
        )

        try:
            # 🛠️ Yangi kutubxonaning async so'rov chaqiruvi (client.aio)
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            response_text = response.text

            order_data = parse_order_from_response(response_text)
            clean_text = clean_response_text(response_text)

            return clean_text, order_data

        except Exception as e:
            error_msg = f"AI xizmatida xatolik yuz berdi. Iltimos, qayta urinib ko'ring. ({str(e)[:50]})"
            return error_msg, None

    async def get_simple_response(self, prompt: str) -> str:
        try:
            # 🛠️ Oddiy async matn generatsiyasi
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Xatolik: {str(e)}"


def format_products_for_ai(products: list) -> str:
    if not products:
        return "Hozirda omborda mahsulot yo'q."

    lines = []
    for p in products:
        line = (
            f"- {p.model} | Rang: {p.color or 'ko-rsatilmagan'} | "
            f"Narx: {p.price:,.0f} so'm | Soni: {p.quantity} ta | ID: {p.id}"
        )
        lines.append(line)

    return "\n".join(lines)