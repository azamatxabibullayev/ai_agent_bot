import os
import json
import re
from itertools import cycle
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_keys_str = os.getenv("GEMINI_API_KEYS", "")
if not api_keys_str:
    api_keys_str = os.getenv("GEMINI_API_KEY", "")

API_KEYS_POOL = [key.strip() for key in api_keys_str.split(",") if key.strip()]

if not API_KEYS_POOL:
    raise ValueError("XATOLIK: .env faylida GEMINI_API_KEYS yoki GEMINI_API_KEY topilmadi!")

keys_iterator = cycle(API_KEYS_POOL)


def get_next_client() -> genai.Client:
    current_key = next(keys_iterator)
    print(f"🤖 AI so'rovi uchun kalit almashtirildi: ...{current_key[-8:]}")
    return genai.Client(api_key=current_key)


def build_system_prompt(products_info: str) -> str:
    return f"""Sen "TechShop" telefon do'konining professional sotuvchisisan. Maqsading chalg'imasdan mahsulot sotish va buyurtma olish.

## OMBORDAGI SMARTFONLAR:
{products_info}

## QOIDALAR:
1. FORMATLASH: Hech qanday yulduzchalar (*), panjaralar (#) yoki minus (-) belgilarini ishlatma! Oddiy va abzasli matn bilan yoz.
2. TAKRORIY SALOMLASHISH: Suhbat davomida qayta-qayta salom berma. Faqat boshida bir marta salomlash.
3. TELEFON MAVZUSI: Solishtirish savollariga juda qisqa (2 ta gap) javob ber va darhol gapni ombordagi modellarga bur. 
4. BEGONA MAVZU: Telefonlarga aloqasi yo'q narsalarni so'rasa, faqat telefonlar bo'yicha yordam bera olishingni eslat.

## BUYURTMA JSON:
Barcha ma'lumotlar (Ism, Tel, Manzil) yig'ilganda, javobni AYNAN quyidagi formatda yakunla:
===ORDER_DATA===
{{
  "ready": true,
  "product_name": "mahsulot nomi",
  "product_id": null,
  "quantity": 1,
  "customer_name": "Ism Familiya",
  "customer_phone": "+998901234567",
  "customer_address": "manzil",
  "summary": "Xulosa"
}}
===END_ORDER===
Jarayon to'liq bo'lmasa "ready": false qo'y. Oddiy gaplashganda JSON qo'shma.
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
        self.model_name = "gemini-2.5-flash"

    async def get_response(
            self,
            user_message: str,
            conversation_history: List[Dict[str, str]],
            products_info: str,
    ) -> tuple[str, Optional[Dict[str, Any]]]:

        system_prompt = build_system_prompt(products_info)
        contents = []

        limited_history = conversation_history[-4:] if conversation_history else []

        if limited_history:
            for msg in limited_history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["message"])]
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )

        try:
            current_client = get_next_client()

            response = await current_client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=300,
                    temperature=0.3
                )
            )
            response_text = response.text

            order_data = parse_order_from_response(response_text)
            clean_text = clean_response_text(response_text)

            return clean_text, order_data

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                error_msg = "Hozirda bandman. Iltimos, 30 soniyadan keyin qayta yozing."
            else:
                error_msg = "Tizimda uzilish bo'ldi. Birozdan so'ng qayta yozib ko'ring."

            return error_msg, None

    async def get_simple_response(self, prompt: str) -> str:
        try:
            current_client = get_next_client()
            response = await current_client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Xatolik: {str(e)}"


def format_products_for_ai(products: list) -> str:
    if not products:
        return "Omborda mahsulot yo'q."

    limited_products = products[:5]

    lines = []
    for p in limited_products:
        line = f"- {p.model} | {p.color or ''} | Narx: {p.price:,.0f} so'm | ID: {p.id}"
        lines.append(line)

    return "\n".join(lines)
