"""
Сервис для создания коллажей из фотографий недвижимости
Использует внешние API для создания коллажей без локального скачивания
"""
import asyncio
import aiohttp
import hashlib
import logging
from typing import List, Optional, Union
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)


class ImageCollageService:
    """
    Сервис для создания коллажей из фотографий недвижимости
    """
    
    def __init__(self):
        # Fallback сервисы для создания коллажей
        self.collage_services = [
            self._create_collage_with_imagekit,
            self._create_collage_with_bannerbear,
            self._create_collage_with_photocollage
        ]
    
    async def create_property_collage(
        self, 
        image_urls: List[str], 
        max_images: int = 3,
        layout: str = "grid"
    ) -> Optional[str]:
        """
        Создает коллаж из фотографий объявления
        
        Args:
            image_urls: Список URL изображений
            max_images: Максимальное количество изображений (2-4)
            layout: Тип коллажа ("grid", "horizontal", "vertical")
            
        Returns:
            URL созданного коллажа или None при ошибке
        """
        if not image_urls or len(image_urls) < 2:
            logger.warning("Недостаточно изображений для создания коллажа")
            return None
        
        # Берем только нужное количество изображений
        selected_images = image_urls[:max_images]
        
        # Пробуем разные сервисы по очереди
        for service_func in self.collage_services:
            try:
                collage_url = await service_func(selected_images, layout)
                if collage_url:
                    logger.info(f"Коллаж создан: {collage_url}")
                    return collage_url
            except Exception as e:
                logger.warning(f"Сервис {service_func.__name__} недоступен: {e}")
                continue
        
        logger.error("Все сервисы коллажей недоступны")
        return None
    
    async def _create_collage_with_imagekit(
        self, 
        image_urls: List[str], 
        layout: str
    ) -> Optional[str]:
        """
        Создание коллажа через ImageKit.io
        Бесплатный сервис с хорошими возможностями
        """
        try:
            # ImageKit позволяет создавать коллажи через URL параметры
            base_url = "https://ik.imagekit.io/demo"
            
            # Параметры для коллажа
            if len(image_urls) == 2:
                # Горизонтальный коллаж 2 изображения
                transform_params = {
                    "tr": "w-800,h-400,c-pad_resize,bg-white",
                    "ot": f"l-image,i-{quote(image_urls[1])},w-400,h-400,x-400,y-0,l-end"
                }
            elif len(image_urls) == 3:
                # Коллаж 3 изображения: 1 большое + 2 маленьких
                transform_params = {
                    "tr": "w-800,h-600,c-pad_resize,bg-white",
                    "ot": f"l-image,i-{quote(image_urls[1])},w-400,h-300,x-400,y-0,l-end"
                         f"l-image,i-{quote(image_urls[2])},w-400,h-300,x-400,y-300,l-end"
                }
            else:
                return None
            
            # Формируем URL коллажа
            query_string = urlencode(transform_params, safe='-,')
            collage_url = f"{base_url}/{quote(image_urls[0])}?{query_string}"
            
            # Проверяем доступность
            async with aiohttp.ClientSession() as session:
                async with session.head(collage_url, timeout=10) as response:
                    if response.status == 200:
                        return collage_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка ImageKit: {e}")
            return None
    
    async def _create_collage_with_bannerbear(
        self, 
        image_urls: List[str], 
        layout: str
    ) -> Optional[str]:
        """
        Создание коллажа через BannerBear API
        Резервный вариант
        """
        try:
            # Bannerbear требует API ключ, пропускаем для MVP
            # В продакшене можно добавить API ключ
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка BannerBear: {e}")
            return None
    
    async def _create_collage_with_photocollage(
        self, 
        image_urls: List[str], 
        layout: str
    ) -> Optional[str]:
        """
        Простой коллаж через CSS/HTML to Image сервис
        Самый надежный fallback
        """
        try:
            # Для MVP создаем простой URL-based коллаж
            # Используем htmlcsstoimage.com или подобный сервис
            
            # Генерируем уникальный ID для кеширования
            images_hash = hashlib.md5(
                ''.join(image_urls).encode()
            ).hexdigest()[:8]
            
            # Создаем HTML для коллажа
            html_content = self._generate_collage_html(image_urls, layout)
            
            # В реальной реализации здесь был бы API вызов к htmlcsstoimage.com
            # Для демо возвращаем None
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка PhotoCollage: {e}")
            return None
    
    def _generate_collage_html(self, image_urls: List[str], layout: str) -> str:
        """
        Генерирует HTML для коллажа
        """
        if len(image_urls) == 2:
            return f"""
            <div style="display: flex; width: 800px; height: 400px; background: white;">
                <img src="{image_urls[0]}" style="width: 50%; height: 100%; object-fit: cover;" />
                <img src="{image_urls[1]}" style="width: 50%; height: 100%; object-fit: cover;" />
            </div>
            """
        elif len(image_urls) == 3:
            return f"""
            <div style="display: flex; width: 800px; height: 600px; background: white;">
                <img src="{image_urls[0]}" style="width: 50%; height: 100%; object-fit: cover;" />
                <div style="width: 50%; display: flex; flex-direction: column;">
                    <img src="{image_urls[1]}" style="width: 100%; height: 50%; object-fit: cover;" />
                    <img src="{image_urls[2]}" style="width: 100%; height: 50%; object-fit: cover;" />
                </div>
            </div>
            """
        else:
            return f'<img src="{image_urls[0]}" style="width: 800px; height: 400px; object-fit: cover;" />'


# Глобальный экземпляр сервиса
collage_service = ImageCollageService()


async def create_listing_collage(
    image_urls: List[str], 
    max_images: int = 3
) -> Optional[str]:
    """
    Удобная функция для создания коллажа объявления
    
    Args:
        image_urls: Список URL изображений
        max_images: Максимальное количество изображений
        
    Returns:
        URL коллажа или None
    """
    return await collage_service.create_property_collage(
        image_urls, 
        max_images=max_images,
        layout="grid"
    ) 