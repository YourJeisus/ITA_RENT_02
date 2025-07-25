"""
Простой сервис для создания коллажей из фотографий
Использует URL-based подходы без API ключей
"""
import logging
import hashlib
from typing import List, Optional
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)


class SimpleCollageService:
    """
    Простой сервис создания коллажей через URL манипуляции
    """
    
    async def create_property_collage(
        self, 
        image_urls: List[str], 
        max_images: int = 3
    ) -> Optional[str]:
        """
        Создает коллаж из фотографий недвижимости
        
        Args:
            image_urls: Список URL изображений
            max_images: Максимальное количество изображений (2-3)
            
        Returns:
            URL созданного коллажа или None при ошибке
        """
        if not image_urls or len(image_urls) < 2:
            logger.debug("Недостаточно изображений для коллажа")
            return None
        
        # Берем только нужное количество изображений
        selected_images = image_urls[:max_images]
        
        try:
            # Пробуем разные методы создания коллажа
            collage_url = await self._create_collage_via_proxy(selected_images)
            if collage_url:
                return collage_url
            
            # Fallback: возвращаем первое изображение
            logger.info("Коллаж недоступен, используем первое изображение")
            return selected_images[0]
            
        except Exception as e:
            logger.warning(f"Ошибка создания коллажа: {e}")
            return selected_images[0] if selected_images else None
    
    async def _create_collage_via_proxy(self, image_urls: List[str]) -> Optional[str]:
        """
        Создает коллаж через сервис htmlcsstoimage.com
        """
        try:
            import aiohttp
            import json
            import base64
            
            # Создаем HTML для коллажа
            html_content = self._generate_collage_html(image_urls)
            css_content = self._generate_collage_css()
            
            # API htmlcsstoimage.com
            api_url = "https://hcti.io/v1/image"
            
            # Данные для API
            data = {
                'html': html_content,
                'css': css_content,
                'device_scale': 2,
                'format': 'jpg',
                'viewport_width': 800,
                'viewport_height': 600
            }
            
            # Получаем настоящие ключи из конфига
            from src.core.config import settings
            if settings.HTMLCSS_USER_ID and settings.HTMLCSS_API_KEY:
                user_id = settings.HTMLCSS_USER_ID
                api_key = settings.HTMLCSS_API_KEY
                
                logger.info(f"🎨 Создаем коллаж через htmlcsstoimage API...")
                
                # Basic Auth
                credentials = base64.b64encode(f"{user_id}:{api_key}".encode()).decode()
                headers = {
                    'Authorization': f'Basic {credentials}',
                    'Content-Type': 'application/json'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        api_url, 
                        json=data, 
                        headers=headers,
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            image_url = result.get('url')
                            if image_url:
                                logger.info(f"✅ Коллаж создан: {image_url}")
                                return image_url
                        else:
                            logger.warning(f"❌ Ошибка API htmlcsstoimage: {response.status}")
                            # Читаем тело ответа для диагностики
                            error_text = await response.text()
                            logger.warning(f"Ответ API: {error_text}")
            else:
                logger.warning("⚠️ API ключи htmlcsstoimage не настроены")
            
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка создания коллажа: {e}")
            return None
    
    def _generate_collage_html(self, image_urls: List[str]) -> str:
        """
        Генерирует HTML для коллажа в стиле недвижимости
        """
        if len(image_urls) == 2:
            return f"""
            <div class="collage-container">
                <div class="image-main">
                    <img src="{image_urls[0]}" alt="Main photo" />
                </div>
                <div class="image-secondary">
                    <img src="{image_urls[1]}" alt="Secondary photo" />
                </div>
            </div>
            """
        elif len(image_urls) >= 3:
            return f"""
            <div class="collage-container">
                <div class="image-main">
                    <img src="{image_urls[0]}" alt="Main photo" />
                </div>
                <div class="image-sidebar">
                    <div class="image-small">
                        <img src="{image_urls[1]}" alt="Photo 2" />
                    </div>
                    <div class="image-small">
                        <img src="{image_urls[2]}" alt="Photo 3" />
                    </div>
                </div>
            </div>
            """
        else:
            return f'<img src="{image_urls[0]}" class="single-image" alt="Property photo" />'
    
    def _generate_collage_css(self) -> str:
        """
        Генерирует CSS для красивого коллажа
        """
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        .collage-container {
            display: flex;
            width: 800px;
            height: 600px;
            gap: 4px;
            background: #f0f0f0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .image-main {
            flex: 2;
            height: 100%;
        }
        
        .image-main img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .image-secondary {
            flex: 1;
            height: 100%;
        }
        
        .image-secondary img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .image-sidebar {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .image-small {
            flex: 1;
        }
        
        .image-small img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .single-image {
            width: 800px;
            height: 600px;
            object-fit: cover;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        """


# Глобальный экземпляр сервиса
simple_collage_service = SimpleCollageService()


async def create_simple_collage(image_urls: List[str]) -> Optional[str]:
    """
    Простая функция создания коллажа
    """
    return await simple_collage_service.create_property_collage(image_urls) 