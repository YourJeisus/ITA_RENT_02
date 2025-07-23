import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
} from '@mui/material';
import {
  LocationOn,
  Home,
  Bathtub,
  SquareFoot,
  Euro,
  OpenInNew,
  Favorite,
  FavoriteBorder,
} from '@mui/icons-material';

interface ListingCardProps {
  listing: {
    listing_id: string;
    title: string;
    price: string | number;
    price_currency: string;
    location_address: string;
    description_short?: string;
    url_details: string;
    image_urls: string[];
    area_sqm?: string | number;
    rooms_count?: string | number;
    bathrooms_count?: string | number;
    property_type?: string;
    agency_name?: string;
    source_site: string;
    raw_features?: string[];
  };
  onFavoriteToggle?: (listingId: string) => void;
  isFavorite?: boolean;
}

const ListingCard: React.FC<ListingCardProps> = ({
  listing,
  onFavoriteToggle,
  isFavorite = false,
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const handleOpenListing = () => {
    window.open(listing.url_details, '_blank', 'noopener,noreferrer');
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onFavoriteToggle) {
      onFavoriteToggle(listing.listing_id);
    }
  };

  // Обработчик движения мыши по изображению
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!listing.image_urls || listing.image_urls.length <= 1) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const width = rect.width;
    const imageIndex = Math.floor((x / width) * listing.image_urls.length);
    const clampedIndex = Math.max(
      0,
      Math.min(imageIndex, listing.image_urls.length - 1)
    );

    if (clampedIndex !== currentImageIndex) {
      setCurrentImageIndex(clampedIndex);
    }
  };

  // Сброс к первому изображению при уходе мыши
  const handleMouseLeave = () => {
    if (listing.image_urls && listing.image_urls.length > 1) {
      setCurrentImageIndex(0);
    }
  };

  const formatPrice = (price: string) => {
    if (!price) return 'Цена не указана';
    return price.replace(/,/g, ' ');
  };

  const getPropertyTypeLabel = (type?: string) => {
    const typeMap: { [key: string]: string } = {
      appartamento: 'Квартира',
      attico: 'Пентхаус',
      villa: 'Вилла',
      villetta: 'Виллетта',
      casa: 'Дом',
      casa_indipendente: 'Отдельный дом',
      monolocale: 'Студия',
      bilocale: '2-комн.',
      trilocale: '3-комн.',
      quadrilocale: '4-комн.',
      loft: 'Квартира',
      mansarda: 'Мансарда',
      palazzo: 'Палаццо',
      castello: 'Замок',
      rustico: 'Рустико',
      casale: 'Казале',
      masseria: 'Массерия',
      trullo: 'Трулло',
      baita: 'Шале',
      duplex: 'Дуплекс',
    };
    return typeMap[type || ''] || type || 'Недвижимость';
  };

  const getSiteLabel = (site: string) => {
    const siteMap: { [key: string]: { name: string; color: string } } = {
      'idealista.it': { name: 'Idealista', color: '#ff6b35' },
      'immobiliare.it': { name: 'Immobiliare', color: '#1976d2' },
      'subito.it': { name: 'Subito', color: '#4caf50' },
    };
    return siteMap[site] || { name: site, color: '#757575' };
  };

  const siteInfo = getSiteLabel(listing.source_site);

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={handleOpenListing}
    >
      {/* Изображение */}
      <Box sx={{ position: 'relative' }}>
        <CardMedia
          component="img"
          height="200"
          image={
            listing.image_urls[currentImageIndex] || '/placeholder-property.jpg'
          }
          alt={listing.title}
          sx={{ objectFit: 'cover' }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        />

        {/* Точки-индикаторы (показываем только если больше 1 фото) */}
        {listing.image_urls && listing.image_urls.length > 1 && (
          <Box
            sx={{
              position: 'absolute',
              bottom: 8,
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              gap: 0.5,
            }}
          >
            {listing.image_urls.map((_, index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor:
                    index === currentImageIndex
                      ? 'rgba(255, 255, 255, 0.9)'
                      : 'rgba(255, 255, 255, 0.4)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    transform: 'scale(1.2)',
                  },
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentImageIndex(index);
                }}
              />
            ))}
          </Box>
        )}

        {/* Кнопка избранного */}
        <IconButton
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            '&:hover': { backgroundColor: 'rgba(255, 255, 255, 1)' },
          }}
          onClick={handleFavoriteClick}
        >
          {isFavorite ? (
            <Favorite sx={{ color: '#ff1744' }} />
          ) : (
            <FavoriteBorder />
          )}
        </IconButton>

        {/* Источник */}
        <Chip
          label={siteInfo.name}
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            left: 8,
            backgroundColor: siteInfo.color,
            color: 'white',
            fontWeight: 'bold',
          }}
        />

        {/* Тип недвижимости */}
        <Chip
          label={getPropertyTypeLabel(listing.property_type)}
          size="small"
          sx={{
            position: 'absolute',
            bottom: 8,
            left: 8,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
          }}
        />
      </Box>

      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        {/* Цена */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Euro sx={{ color: 'primary.main', mr: 0.5 }} />
          <Typography
            variant="h6"
            component="div"
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            {formatPrice(listing.price.toString())}
          </Typography>
        </Box>

        {/* Заголовок */}
        <Typography
          variant="body1"
          component="div"
          sx={{
            fontWeight: 'medium',
            mb: 1,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            lineHeight: 1.3,
          }}
        >
          {listing.title}
        </Typography>

        {/* Адрес */}
        {listing.location_address && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <LocationOn
              sx={{ color: 'text.secondary', fontSize: 16, mr: 0.5 }}
            />
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: '0.875rem' }}
            >
              {listing.location_address}
            </Typography>
          </Box>
        )}

        {/* Характеристики */}
        <Box sx={{ display: 'flex', gap: 2, mb: 1, flexWrap: 'wrap' }}>
          {listing.area_sqm && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SquareFoot
                sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }}
              />
              <Typography variant="body2" color="text.secondary">
                {listing.area_sqm} м²
              </Typography>
            </Box>
          )}

          {listing.rooms_count && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Home sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {listing.rooms_count} комн.
              </Typography>
            </Box>
          )}

          {listing.bathrooms_count && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Bathtub
                sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }}
              />
              <Typography variant="body2" color="text.secondary">
                {listing.bathrooms_count} ванн.
              </Typography>
            </Box>
          )}
        </Box>

        {/* Описание */}
        {listing.description_short && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 1,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              fontSize: '0.8rem',
            }}
          >
            {listing.description_short}
          </Typography>
        )}

        {/* Агентство */}
        {listing.agency_name && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontStyle: 'italic' }}
          >
            {listing.agency_name}
          </Typography>
        )}

        {/* Особенности */}
        {listing.raw_features && listing.raw_features.length > 0 && (
          <Box sx={{ mt: 1 }}>
            {listing.raw_features.slice(0, 2).map((feature, index) => (
              <Chip
                key={index}
                label={feature}
                size="small"
                variant="outlined"
                sx={{ mr: 0.5, mb: 0.5, fontSize: '0.7rem' }}
              />
            ))}
          </Box>
        )}
      </CardContent>

      {/* Кнопка открытия */}
      <Box sx={{ p: 2, pt: 0 }}>
        <Button
          variant="outlined"
          fullWidth
          startIcon={<OpenInNew />}
          onClick={handleOpenListing}
          sx={{ textTransform: 'none' }}
        >
          Открыть объявление
        </Button>
      </Box>
    </Card>
  );
};

export default ListingCard;
