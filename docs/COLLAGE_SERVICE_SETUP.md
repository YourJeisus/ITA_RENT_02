# 🎨 Настройка сервиса коллажей фотографий

Система поддерживает создание красивых коллажей из фотографий недвижимости, как на примере выше.

## 🚀 Варианты реализации

### 1. **HTML/CSS to Image API** (рекомендуемый)

**Сервис:** https://htmlcsstoimage.com/
**Лимиты:** 50 изображений/месяц бесплатно
**Стоимость:** $9/месяц за 1000 изображений

#### Регистрация:

1. Зарегистрируйтесь на https://htmlcsstoimage.com/
2. Получите `User ID` и `API Key`
3. Добавьте в `.env`:
   ```
   HTMLCSS_USER_ID=your_user_id
   HTMLCSS_API_KEY=your_api_key
   ```

### 2. **Vercel Edge Function** (бесплатно)

Создайте простой сервис на Vercel для генерации коллажей.

#### Пример кода для `api/collage.js`:

```javascript
import { ImageResponse } from "@vercel/og";

export const config = {
  runtime: "edge",
};

export default async function handler(request) {
  try {
    const { searchParams } = new URL(request.url);
    const images = [
      searchParams.get("img1"),
      searchParams.get("img2"),
      searchParams.get("img3"),
    ].filter(Boolean);

    if (images.length < 2) {
      return new Response("Need at least 2 images", { status: 400 });
    }

    return new ImageResponse(
      (
        <div
          style={{
            display: "flex",
            width: "800px",
            height: "600px",
            backgroundColor: "#f0f0f0",
            borderRadius: "12px",
            overflow: "hidden",
            gap: "4px",
          }}
        >
          {/* Главное изображение */}
          <img
            src={images[0]}
            style={{
              width: images.length === 2 ? "50%" : "66.66%",
              height: "100%",
              objectFit: "cover",
            }}
          />

          {/* Дополнительные изображения */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              width: images.length === 2 ? "50%" : "33.33%",
              gap: "4px",
            }}
          >
            <img
              src={images[1]}
              style={{
                width: "100%",
                height: images.length > 2 ? "50%" : "100%",
                objectFit: "cover",
              }}
            />
            {images[2] && (
              <img
                src={images[2]}
                style={{
                  width: "100%",
                  height: "50%",
                  objectFit: "cover",
                }}
              />
            )}
          </div>
        </div>
      ),
      {
        width: 800,
        height: 600,
      }
    );
  } catch (e) {
    return new Response(`Failed to generate image: ${e.message}`, {
      status: 500,
    });
  }
}
```

#### Использование Vercel сервиса:

1. Деплойте функцию на Vercel
2. Обновите `src/services/simple_collage_service.py`:

```python
async def _create_collage_via_vercel(self, image_urls: List[str]) -> Optional[str]:
    """Создание коллажа через Vercel Edge Function"""
    try:
        base_url = "https://your-collage-service.vercel.app/api/collage"

        params = {}
        for i, url in enumerate(image_urls[:3]):
            params[f'img{i+1}'] = url

        query_string = urlencode(params)
        collage_url = f"{base_url}?{query_string}"

        # Проверяем доступность
        async with aiohttp.ClientSession() as session:
            async with session.head(collage_url, timeout=10) as response:
                if response.status == 200:
                    return collage_url

        return None
    except Exception as e:
        logger.warning(f"Ошибка Vercel коллажа: {e}")
        return None
```

### 3. **Собственный микросервис** (для высоких нагрузок)

Для больших объемов можно создать отдельный микросервис на Python с PIL/Pillow.

## 📊 Текущий статус

- ✅ **Система коллажей реализована**
- ✅ **Fallback на медиа-группы работает**
- 🔧 **Нужно добавить API ключи для реального создания**

## 🎛️ Управление

```bash
# Включить коллажи
python toggle_photo_collages.py on

# Выключить коллажи
python toggle_photo_collages.py off

# Проверить статус
python toggle_photo_collages.py status
```

## 🎨 Результат

### Без коллажей:

- Telegram MediaGroup (2-3 отдельных фото)

### С коллажами:

- Одно красивое изображение-коллаж
- Лучший UX для пользователей
- Экономия места в чате

## 🚦 Railway деплой

Добавьте в `railway.toml`:

```toml
[services.notification-worker.env]
ENABLE_PHOTO_COLLAGES = "true"
HTMLCSS_USER_ID = "your_user_id"
HTMLCSS_API_KEY = "your_api_key"
```

## 💡 Рекомендации

1. **Для MVP**: Используйте бесплатный лимит htmlcsstoimage.com
2. **Для production**: Создайте Vercel сервис
3. **Для масштаба**: Собственный микросервис с кешированием

Система работает в режиме graceful degradation - если коллажи недоступны, автоматически переключается на обычные медиа-группы.
