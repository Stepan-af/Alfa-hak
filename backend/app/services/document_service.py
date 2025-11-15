"""Сервис для работы с документами"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.document import Document, Template
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    GenerateDocumentRequest,
    TemplateCreate,
    TemplateUpdate,
    AIGenerateRequest,
)


class DocumentService:
    """Сервис для работы с документами и шаблонами"""

    # Системные шаблоны (будут созданы при инициализации)
    SYSTEM_TEMPLATES = {
        "contract": {
            "name": "Договор оказания услуг",
            "description": "Стандартный договор на оказание услуг между заказчиком и исполнителем",
            "category": "legal",
            "document_type": "contract",
            "content": """
ДОГОВОР № {{contract_number}}
на оказание услуг

г. {{city}}                                                     {{date}}

{{contractor_name}}, именуемый в дальнейшем "Заказчик", в лице {{contractor_representative}}, действующего на основании {{contractor_authority}}, с одной стороны, и {{executor_name}}, именуемый в дальнейшем "Исполнитель", в лице {{executor_representative}}, действующего на основании {{executor_authority}}, с другой стороны, вместе именуемые "Стороны", заключили настоящий Договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Исполнитель обязуется оказать услуги {{service_description}}, а Заказчик обязуется принять и оплатить эти услуги на условиях настоящего Договора.

2. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЕТОВ

2.1. Стоимость услуг по настоящему Договору составляет {{amount}} ({{amount_words}}) рублей, включая НДС {{vat_rate}}%.

2.2. Оплата производится {{payment_terms}}.

3. ПРАВА И ОБЯЗАННОСТИ СТОРОН

3.1. Заказчик обязуется:
- Своевременно оплачивать услуги Исполнителя;
- Предоставлять информацию, необходимую для оказания услуг.

3.2. Исполнитель обязуется:
- Оказать услуги качественно и в установленные сроки;
- Соблюдать конфиденциальность полученной информации.

4. СРОК ДЕЙСТВИЯ ДОГОВОРА

4.1. Настоящий Договор вступает в силу с момента подписания и действует до {{end_date}}.

5. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

5.1. Все споры разрешаются путем переговоров, а при недостижении согласия - в судебном порядке.

5.2. Договор составлен в двух экземплярах, имеющих одинаковую юридическую силу.


ЗАКАЗЧИК:                                          ИСПОЛНИТЕЛЬ:

{{contractor_name}}                                {{executor_name}}
{{contractor_address}}                             {{executor_address}}
ИНН {{contractor_inn}}                            ИНН {{executor_inn}}

_________________/{{contractor_representative}}/    _________________/{{executor_representative}}/
М.П.                                               М.П.
""",
            "variables": {
                "contract_number": {"type": "string", "required": True, "default": ""},
                "city": {"type": "string", "required": True, "default": "Москва"},
                "date": {"type": "date", "required": True, "default": ""},
                "contractor_name": {"type": "string", "required": True, "default": ""},
                "contractor_representative": {"type": "string", "required": True, "default": ""},
                "contractor_authority": {"type": "string", "required": True, "default": "Устава"},
                "executor_name": {"type": "string", "required": True, "default": ""},
                "executor_representative": {"type": "string", "required": True, "default": ""},
                "executor_authority": {"type": "string", "required": True, "default": "Устава"},
                "service_description": {"type": "text", "required": True, "default": ""},
                "amount": {"type": "number", "required": True, "default": ""},
                "amount_words": {"type": "string", "required": True, "default": ""},
                "vat_rate": {"type": "number", "required": False, "default": "20"},
                "payment_terms": {"type": "string", "required": True, "default": "в течение 3 банковских дней"},
                "end_date": {"type": "date", "required": True, "default": ""},
                "contractor_address": {"type": "string", "required": True, "default": ""},
                "contractor_inn": {"type": "string", "required": True, "default": ""},
                "executor_address": {"type": "string", "required": True, "default": ""},
                "executor_inn": {"type": "string", "required": True, "default": ""},
            }
        },
        "act": {
            "name": "Акт выполненных работ",
            "description": "Акт приема-передачи выполненных работ/оказанных услуг",
            "category": "legal",
            "document_type": "act",
            "content": """
АКТ № {{act_number}}
выполненных работ (оказанных услуг)

г. {{city}}                                                     {{date}}

Мы, нижеподписавшиеся, {{contractor_name}} в лице {{contractor_representative}}, действующего на основании {{contractor_authority}}, именуемый "Заказчик", с одной стороны, и {{executor_name}} в лице {{executor_representative}}, действующего на основании {{executor_authority}}, именуемый "Исполнитель", с другой стороны, составили настоящий Акт о нижеследующем:

1. Исполнитель выполнил, а Заказчик принял следующие работы (услуги) по Договору № {{contract_number}} от {{contract_date}}:

{{services_list}}

2. Стоимость выполненных работ (оказанных услуг) составляет {{amount}} ({{amount_words}}) рублей, включая НДС {{vat_rate}}%.

3. Претензий по объему, качеству и срокам выполнения работ (оказания услуг) Заказчик не имеет.


ЗАКАЗЧИК:                                          ИСПОЛНИТЕЛЬ:

{{contractor_name}}                                {{executor_name}}
ИНН {{contractor_inn}}                            ИНН {{executor_inn}}

_________________/{{contractor_representative}}/    _________________/{{executor_representative}}/
М.П.                                               М.П.
""",
            "variables": {
                "act_number": {"type": "string", "required": True, "default": ""},
                "city": {"type": "string", "required": True, "default": "Москва"},
                "date": {"type": "date", "required": True, "default": ""},
                "contractor_name": {"type": "string", "required": True, "default": ""},
                "contractor_representative": {"type": "string", "required": True, "default": ""},
                "contractor_authority": {"type": "string", "required": True, "default": "Устава"},
                "executor_name": {"type": "string", "required": True, "default": ""},
                "executor_representative": {"type": "string", "required": True, "default": ""},
                "executor_authority": {"type": "string", "required": True, "default": "Устава"},
                "contract_number": {"type": "string", "required": True, "default": ""},
                "contract_date": {"type": "date", "required": True, "default": ""},
                "services_list": {"type": "text", "required": True, "default": ""},
                "amount": {"type": "number", "required": True, "default": ""},
                "amount_words": {"type": "string", "required": True, "default": ""},
                "vat_rate": {"type": "number", "required": False, "default": "20"},
                "contractor_inn": {"type": "string", "required": True, "default": ""},
                "executor_inn": {"type": "string", "required": True, "default": ""},
            }
        },
        "invoice": {
            "name": "Счет на оплату",
            "description": "Счет на оплату товаров или услуг",
            "category": "finance",
            "document_type": "invoice",
            "content": """
СЧЕТ НА ОПЛАТУ № {{invoice_number}} от {{date}}

Поставщик: {{supplier_name}}
ИНН: {{supplier_inn}}
Адрес: {{supplier_address}}
Тел.: {{supplier_phone}}

Покупатель: {{buyer_name}}
ИНН: {{buyer_inn}}
Адрес: {{buyer_address}}

Основание: {{payment_purpose}}

┌────┬──────────────────────────┬──────┬─────┬──────────┬──────────┬──────────┐
│ № │ Наименование товара/услуги│ Кол-во│ Ед. │   Цена   │ НДС {{vat_rate}}% │   Сумма  │
├────┼──────────────────────────┼──────┼─────┼──────────┼──────────┼──────────┤
{{items_list}}
└────┴──────────────────────────┴──────┴─────┴──────────┴──────────┴──────────┘

Итого:                                                              {{total_amount}}
НДС {{vat_rate}}%:                                                           {{vat_amount}}
Всего к оплате:                                                     {{total_with_vat}}

Всего наименований {{items_count}}, на сумму {{total_with_vat}} руб.
{{total_with_vat_words}}

Руководитель: ___________________ {{director_name}}
Главный бухгалтер: ___________________ {{accountant_name}}
М.П.
""",
            "variables": {
                "invoice_number": {"type": "string", "required": True, "default": ""},
                "date": {"type": "date", "required": True, "default": ""},
                "supplier_name": {"type": "string", "required": True, "default": ""},
                "supplier_inn": {"type": "string", "required": True, "default": ""},
                "supplier_address": {"type": "string", "required": True, "default": ""},
                "supplier_phone": {"type": "string", "required": False, "default": ""},
                "buyer_name": {"type": "string", "required": True, "default": ""},
                "buyer_inn": {"type": "string", "required": True, "default": ""},
                "buyer_address": {"type": "string", "required": True, "default": ""},
                "payment_purpose": {"type": "string", "required": True, "default": ""},
                "items_list": {"type": "text", "required": True, "default": ""},
                "vat_rate": {"type": "number", "required": False, "default": "20"},
                "total_amount": {"type": "number", "required": True, "default": ""},
                "vat_amount": {"type": "number", "required": True, "default": ""},
                "total_with_vat": {"type": "number", "required": True, "default": ""},
                "total_with_vat_words": {"type": "string", "required": True, "default": ""},
                "items_count": {"type": "number", "required": True, "default": ""},
                "director_name": {"type": "string", "required": True, "default": ""},
                "accountant_name": {"type": "string", "required": False, "default": ""},
            }
        }
    }

    @staticmethod
    def substitute_variables(template_content: str, variables: Dict[str, Any]) -> str:
        """
        Подстановка переменных в шаблон
        
        Поддерживает формат: {{variable_name}}
        """
        content = template_content
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            # Преобразуем значение в строку
            str_value = str(var_value) if var_value is not None else ""
            content = content.replace(placeholder, str_value)
        
        return content

    @staticmethod
    def extract_variables(template_content: str) -> List[str]:
        """Извлечь список переменных из шаблона"""
        pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(pattern, template_content)
        return list(set(variables))  # Уникальные переменные

    @staticmethod
    async def generate_document(
        db: Session,
        user_id: int,
        request: GenerateDocumentRequest
    ) -> Document:
        """Генерация документа из шаблона"""
        
        # Получаем шаблон
        template = db.query(Template).filter(Template.id == request.template_id).first()
        if not template:
            raise ValueError("Шаблон не найден")
        
        # Подставляем переменные
        content = DocumentService.substitute_variables(str(template.content), request.variables)  # type: ignore
        
        # Создаем документ
        document = Document(
            user_id=user_id,
            title=request.title,
            content=content,
            template_id=request.template_id,
            document_type=request.document_type or template.document_type,
            variables=request.variables,
            counterparty_name=request.counterparty_name,
            counterparty_inn=request.counterparty_inn,
            amount=request.amount,
            status="draft",
        )
        
        db.add(document)
        
        # Увеличиваем счетчик использования шаблона
        template.usage_count += 1  # type: ignore
        
        db.commit()
        db.refresh(document)
        
        return document

    @staticmethod
    def create_system_templates(db: Session) -> int:
        """Создать системные шаблоны (если еще не созданы)"""
        created = 0
        
        for template_key, template_data in DocumentService.SYSTEM_TEMPLATES.items():
            # Проверяем, существует ли уже такой шаблон
            existing = db.query(Template).filter(
                and_(
                    Template.name == template_data["name"],
                    Template.is_system == "true"
                )
            ).first()
            
            if not existing:
                template = Template(
                    name=template_data["name"],
                    description=template_data["description"],
                    content=template_data["content"],
                    category=template_data["category"],
                    document_type=template_data["document_type"],
                    variables=template_data["variables"],
                    is_system="true",
                    user_id=None,
                )
                db.add(template)
                created += 1
        
        if created > 0:
            db.commit()
        
        return created

    @staticmethod
    async def ai_generate_document(
        request: AIGenerateRequest
    ) -> Dict[str, Any]:
        """
        AI-генерация текста документа (заглушка для будущей интеграции с LLM)
        
        В будущем здесь будет вызов Ollama/LiteLLM для генерации
        """
        
        # Заглушка - возвращаем шаблонный ответ
        if request.document_type == "contract":
            content = f"""
ДОГОВОР
на {request.purpose}

Стороны:
Заказчик: {request.parties.get('buyer', 'Не указан')}
Исполнитель: {request.parties.get('seller', 'Не указан')}

[AI будет генерировать детальный текст договора на основе условий]

Дополнительно: {request.additional_info or 'Нет'}
"""
            title = f"Договор на {request.purpose}"
        elif request.document_type == "act":
            content = f"АКТ выполненных работ\n\nЗаказчик: {request.parties.get('buyer', '')}\nИсполнитель: {request.parties.get('seller', '')}"
            title = f"Акт - {request.purpose}"
        else:
            content = f"Документ: {request.document_type}\nЦель: {request.purpose}"
            title = f"{request.document_type} - {request.purpose}"
        
        return {
            "content": content,
            "suggested_title": title,
            "variables": {}
        }

    @staticmethod
    def get_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """Получить статистику по документам пользователя"""
        
        # Общее количество
        total = db.query(func.count(Document.id)).filter(Document.user_id == user_id).scalar()
        
        # По типам
        by_type = db.query(
            Document.document_type,
            func.count(Document.id)
        ).filter(Document.user_id == user_id).group_by(Document.document_type).all()
        
        # По статусам
        by_status = db.query(
            Document.status,
            func.count(Document.id)
        ).filter(Document.user_id == user_id).group_by(Document.status).all()
        
        # Последние документы
        recent = db.query(Document).filter(
            Document.user_id == user_id
        ).order_by(desc(Document.created_at)).limit(5).all()
        
        # Популярные шаблоны
        popular_templates = db.query(Template).filter(
            Template.is_system == "true"
        ).order_by(desc(Template.usage_count)).limit(5).all()
        
        return {
            "total_documents": total,
            "by_type": {k: v for k, v in by_type},  # type: ignore
            "by_status": {k: v for k, v in by_status},  # type: ignore
            "recent_documents": recent,
            "most_used_templates": popular_templates,
        }
