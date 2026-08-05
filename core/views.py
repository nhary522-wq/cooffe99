import hashlib
import json
import logging
import re
import time

import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from orders.models import Order
from .models import BrewMethod, CoffeeContent, ContentCategory


logger = logging.getLogger(__name__)

STORE_ASSISTANT_INSTRUCTIONS = """
أنت مساعد متجر A23 الإلكتروني. أجب بالعربية الواضحة وبأسلوب ودود ومختصر.
يمكنك الإجابة عن الأسئلة العامة، لكن أعط الأولوية لمعلومات المتجر التالية:
- المحاصيل: شلشلي إثيوبي، مزيج البهاء، بلقيس اليمن، روبي كلومبي، قوجي إثيوبي، سدرة جازان، كينيا نيري، وبرازيلي سانتوس.
- الأدوات: أكواب إسبريسو، مطحنة يدوية، قمع تقطير، ميزان قهوة، فلاتر بمقاسات مختلفة، مطاحن، أدوات تقطير، أباريق وملحقات.
- التوصيل داخل المملكة العربية السعودية، والمدة تختلف حسب المدينة وحالة الطلب.
- التواصل: 0556229463 والبريد nhary522@gmail.com.
- تتبع الطلب يتطلب رقم الطلب ورقم الجوال في صفحة تتبع الطلب.
لا تدّع معرفة حالة طلب محدد أو سعر أو مخزون غير مقدم لك. وجّه المستخدم لصفحة التتبع أو التواصل عند الحاجة.
لا تطلب كلمات المرور أو بيانات البطاقات أو الرموز السرية.
""".strip()


def _local_assistant_answer(message):
    normalized = message.strip().lower()
    if any(word in normalized for word in ("شحن", "توصيل", "يوصل")):
        return "نوصل داخل المملكة العربية السعودية، وتختلف المدة حسب المدينة وحالة الطلب. يمكنك متابعة التحديثات من صفحة تتبع الطلب."
    if any(word in normalized for word in ("تتبع", "طلبي", "طلب")):
        return "لتتبع طلبك افتح صفحة «تتبع الطلب» وأدخل رقم الطلب ورقم الجوال المستخدم عند الشراء."
    if any(word in normalized for word in ("استرجاع", "استبدال", "تالف")):
        return "يمكنك تقديم طلب استبدال أو استرجاع بالتواصل معنا مع رقم الطلب وصورة واضحة للمنتج والعبوة."
    if any(word in normalized for word in ("تواصل", "جوال", "رقم", "ايميل", "بريد")):
        return "تواصل معنا على 0556229463 أو عبر البريد الإلكتروني nhary522@gmail.com."
    if any(word in normalized for word in ("محصول", "محاصيل", "قهوة", "بن")):
        return "نوفر محاصيل متنوعة، منها شلشلي إثيوبي، بلقيس اليمن، روبي كلومبي، قوجي إثيوبي، سدرة جازان، كينيا نيري وبرازيلي سانتوس. أخبرني بالنكهة التي تفضلها لأقترح الأنسب."
    if any(word in normalized for word in ("مطحنة", "أداة", "اداة", "فلتر", "قمع", "ميزان", "كوب")):
        return "قسم الأدوات يضم أكواب إسبريسو، مطاحن يدوية، أقماع تقطير، موازين، فلاتر بمقاسات مختلفة، أباريق وملحقات تحضير."
    return "أستطيع مساعدتك الآن في أسئلة متجر A23 والمحاصيل والأدوات والشحن والتتبع. للإجابة الذكية عن الأسئلة العامة يلزم تفعيل مفتاح OpenAI على الخادم."


def _extract_response_text(payload):
    for output in payload.get("output", []):
        for content in output.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"].strip()
    return ""


@require_POST
def ai_chat(request):
    now = int(time.time())
    recent_requests = [
        timestamp
        for timestamp in request.session.get("ai_chat_requests", [])
        if now - timestamp < 600
    ]
    if len(recent_requests) >= 15:
        return JsonResponse(
            {"error": "تم تجاوز عدد الرسائل المؤقت. حاول مرة أخرى بعد قليل."},
            status=429,
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "تعذر قراءة الرسالة."}, status=400)

    message = str(payload.get("message", "")).strip()
    if not message:
        return JsonResponse({"error": "اكتب سؤالك أولًا."}, status=400)
    if len(message) > 600:
        return JsonResponse({"error": "يجب ألا يتجاوز السؤال 600 حرف."}, status=400)

    recent_requests.append(now)
    request.session["ai_chat_requests"] = recent_requests

    if not settings.OPENAI_API_KEY:
        return JsonResponse(
            {"answer": _local_assistant_answer(message), "mode": "local"}
        )

    conversation = []
    for item in payload.get("history", [])[-6:]:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            continue
        content = str(item.get("content", "")).strip()[:600]
        if content:
            conversation.append({"role": item["role"], "content": content})
    conversation.append({"role": "user", "content": message})

    if not request.session.session_key:
        request.session.create()
    safety_identifier = hashlib.sha256(
        request.session.session_key.encode("utf-8")
    ).hexdigest()[:32]

    try:
        api_response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENAI_CHAT_MODEL,
                "instructions": STORE_ASSISTANT_INSTRUCTIONS,
                "input": conversation,
                "reasoning": {"effort": "low"},
                "text": {"verbosity": "low"},
                "max_output_tokens": 500,
                "safety_identifier": safety_identifier,
                "store": False,
            },
            timeout=25,
        )
        api_response.raise_for_status()
        answer = _extract_response_text(api_response.json())
        if not answer:
            raise ValueError("OpenAI response did not include output text")
    except (requests.RequestException, ValueError):
        logger.exception("A23 assistant request failed")
        return JsonResponse(
            {"error": "تعذر الوصول إلى المساعد الآن. حاول مرة أخرى بعد قليل."},
            status=503,
        )

    return JsonResponse({"answer": answer, "mode": "ai"})


def home(request):
    """عرض الصفحة الرئيسية للمتجر."""
    return render(request, "home.html")


def contact(request):
    return render(request, "core/contact.html")


def faq(request):
    sections = [
        {
            "title": "كيف أطلب من المتجر؟",
            "content": "اختر المنتجات وأضفها إلى السلة، ثم أكمل بيانات الشحن والدفع لتأكيد الطلب.",
        },
        {
            "title": "متى يتم تجهيز طلبي؟",
            "content": "تبدأ معالجة الطلب بعد تأكيده، ويمكنك متابعة حالته من صفحة تتبع الطلب.",
        },
        {
            "title": "هل يمكن تعديل الطلب؟",
            "content": "تواصل معنا سريعًا قبل انتقال الطلب إلى حالة التجهيز، وسنساعدك حسب حالة الطلب.",
        },
        {
            "title": "كيف أحافظ على جودة القهوة؟",
            "content": "احفظ المحصول في عبوة محكمة بعيدًا عن الحرارة والرطوبة والضوء، واطحن الكمية عند الاستخدام.",
        },
    ]
    return render(
        request,
        "core/information_page.html",
        {
            "page_title": "الأسئلة الشائعة",
            "page_description": "إجابات سريعة عن الطلبات والشحن ومنتجات A23.",
            "sections": sections,
        },
    )


def shipping_policy(request):
    sections = [
        {
            "title": "نطاق التوصيل",
            "content": "نوصل الطلبات داخل المملكة العربية السعودية إلى العنوان المدخل عند إتمام الطلب.",
        },
        {
            "title": "مدة التجهيز والتوصيل",
            "content": "تختلف المدة حسب المدينة وحالة المنتج، وتظهر تحديثات الطلب والشحنة في صفحة التتبع.",
        },
        {
            "title": "العنوان الصحيح",
            "content": "يجب إدخال المدينة والحي والشارع ورقم الجوال بدقة. قد يتأخر الطلب إذا كانت البيانات ناقصة.",
        },
        {
            "title": "استلام الشحنة",
            "content": "افحص سلامة العبوة عند الاستلام، وتواصل معنا مباشرة إذا ظهر تلف واضح في الشحنة.",
        },
    ]
    return render(
        request,
        "core/information_page.html",
        {
            "page_title": "سياسة الشحن",
            "page_description": "تفاصيل تجهيز وشحن طلبات متجر A23.",
            "sections": sections,
        },
    )


def return_policy(request):
    sections = [
        {
            "title": "طلب الاستبدال أو الاسترجاع",
            "content": "تواصل معنا مع رقم الطلب وصورة واضحة للمنتج والعبوة، وسيراجع فريقنا الطلب.",
        },
        {
            "title": "المنتجات غير المفتوحة",
            "content": "يجب أن يكون المنتج بحالته الأصلية وغير مستخدم وبكامل ملحقاته حتى يمكن تقييم طلب الإرجاع.",
        },
        {
            "title": "المنتج التالف أو الخاطئ",
            "content": "إذا وصل المنتج تالفًا أو مختلفًا عن الطلب، أبلغنا فورًا وسنتحقق ونوفر الحل المناسب.",
        },
        {
            "title": "المبالغ المستردة",
            "content": "بعد اعتماد الاسترجاع، يعاد المبلغ وفق وسيلة الدفع ومدة المعالجة الخاصة بها.",
        },
    ]
    return render(
        request,
        "core/information_page.html",
        {
            "page_title": "الاستبدال والاسترجاع",
            "page_description": "سياسة واضحة لحماية مشترياتك من A23.",
            "sections": sections,
        },
    )


def _phone_digits(value):
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("00966"):
        digits = digits[2:]
    if digits.startswith("05"):
        digits = "966" + digits[1:]
    return digits


def track_order(request):
    order = None
    searched = request.method == "POST"
    order_number = ""
    phone = ""

    if searched:
        order_number = request.POST.get("order_number", "").strip()
        phone = request.POST.get("phone", "").strip()
        candidate = (
            Order.objects.select_related("shipment")
            .prefetch_related("items")
            .filter(order_number__iexact=order_number)
            .first()
        )
        if (
            candidate
            and _phone_digits(candidate.customer_phone) == _phone_digits(phone)
            and _phone_digits(phone)
        ):
            order = candidate

    return render(
        request,
        "core/track_order.html",
        {
            "order": order,
            "searched": searched,
            "order_number": order_number,
            "phone": phone,
        },
    )


def brew_list(request):
    methods = BrewMethod.objects.filter(is_published=True).prefetch_related("tools")
    query = request.GET.get("q", "")[:100]
    difficulty = request.GET.get("difficulty", "")[:20]
    tool = request.GET.get("tool", "")[:140]
    if query: methods = methods.filter(Q(name__icontains=query) | Q(short_description__icontains=query))
    if difficulty: methods = methods.filter(difficulty=difficulty)
    if tool: methods = methods.filter(tools__slug=tool)
    return render(request, "core/brew_list.html", {"methods": methods.distinct(), "query": query})


def brew_detail(request, slug):
    method = get_object_or_404(BrewMethod.objects.filter(is_published=True).prefetch_related("steps", "tools", "products"), slug=slug)
    return render(request, "core/brew_detail.html", {"method": method})


def knowledge_list(request):
    contents = CoffeeContent.objects.filter(is_published=True).select_related("category", "author")
    query = request.GET.get("q", "")[:100]
    category = request.GET.get("category", "")[:170]
    if query: contents = contents.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query))
    if category: contents = contents.filter(category__slug=category)
    return render(request, "core/knowledge_list.html", {"contents": contents, "categories": ContentCategory.objects.all(), "query": query})


def knowledge_detail(request, slug):
    article = get_object_or_404(CoffeeContent.objects.filter(is_published=True).select_related("category", "author").prefetch_related("related_contents", "products"), slug=slug)
    return render(request, "core/knowledge_detail.html", {"article": article})
