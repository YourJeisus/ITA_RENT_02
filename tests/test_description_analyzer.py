"""
Тесты для DescriptionAnalyzer
"""
import pytest
from src.parsers.description_analyzer import DescriptionAnalyzer


class TestFloorNormalization:
    """Тесты нормализации этажей"""
    
    def test_floor_number_from_dict(self):
        """Тест извлечения номера этажа из dict (Immobiliare формат)"""
        floor_data = {
            'abbreviation': '3',
            'value': '3°, con ascensore',
            'floorOnlyValue': '3'
        }
        result = DescriptionAnalyzer._analyze_floor_normalized("", floor=floor_data)
        assert result['floor_number'] == 3
        assert result['is_first_floor'] == False
    
    def test_floor_piano_terra(self):
        """Тест ground floor (piano terra)"""
        floor_data = {'abbreviation': 'T', 'value': 'Piano terra', 'floorOnlyValue': 'piano terra'}
        result = DescriptionAnalyzer._analyze_floor_normalized("", floor=floor_data)
        assert result['floor_number'] == 0
        assert result['is_first_floor'] == False  # 0 != 1, поэтому False
    
    def test_floor_first(self):
        """Тест первого этажа"""
        floor_data = {'abbreviation': '1', 'value': '1°', 'floorOnlyValue': '1'}
        result = DescriptionAnalyzer._analyze_floor_normalized("", floor=floor_data)
        assert result['floor_number'] == 1
        assert result['is_first_floor'] == True
    
    def test_floor_seminterrato(self):
        """Тест подвала (seminterrato)"""
        floor_data = "seminterrato"
        result = DescriptionAnalyzer._analyze_floor_normalized("", floor=floor_data)
        assert result['floor_number'] == -1
    
    def test_floor_ultimo(self):
        """Тест последнего этажа"""
        # Когда в floor_data есть слово "ultimo"
        floor_data = "5° piano, ultimo"
        result = DescriptionAnalyzer._analyze_floor_normalized("", floor=floor_data)
        # is_top_floor определится только если знаем total_floors или есть явное указание
        assert result['is_top_floor'] == True
        assert result['floor_number'] == 5
    
    def test_floor_with_total_floors(self):
        """Тест определения последнего этажа когда известно total_floors"""
        result = DescriptionAnalyzer._analyze_floor_normalized(
            "", 
            floor="4",
            total_floors=5
        )
        assert result['floor_number'] == 4
        assert result['total_floors'] == 5
        assert result['is_top_floor'] == True


class TestPetsChildren:
    """Тесты анализа политики pets/children"""
    
    def test_pets_explicit_ban(self):
        """Тест явного запрета на животных"""
        description = "Bellissimo appartamento, no animali ammessi"
        result = DescriptionAnalyzer.analyze(description)
        assert result['pets_allowed'] == False
    
    def test_pets_no_info(self):
        """Тест отсутствия информации о животных"""
        description = "Bellissimo appartamento nel centro"
        result = DescriptionAnalyzer.analyze(description)
        assert result['pets_allowed'] == None
    
    def test_pets_explicitly_allowed(self):
        """Тест явного разрешения животных"""
        description = "Appartamento con animali ammessi"
        result = DescriptionAnalyzer.analyze(description)
        assert result['pets_allowed'] == True
    
    def test_children_explicit_ban(self):
        """Тест явного запрета на детей"""
        description = "Affitto solo a single o coppia, no bambini"
        result = DescriptionAnalyzer.analyze(description)
        assert result['children_friendly'] == False
    
    def test_children_no_info(self):
        """Тест отсутствия информации о детях"""
        description = "Appartamento luminoso e spazioso"
        result = DescriptionAnalyzer.analyze(description)
        assert result['children_friendly'] == None
    
    def test_children_family_friendly(self):
        """Тест семейной квартиры"""
        description = "Appartamento adatto a famiglie con bambini"
        result = DescriptionAnalyzer.analyze(description)
        assert result['children_friendly'] == True


class TestCommission:
    """Тесты анализа комиссии"""
    
    def test_no_commission_privato(self):
        """Тест объявления от собственника"""
        description = "Affitto da privato, senza commissioni"
        result = DescriptionAnalyzer.analyze(description)
        assert result['agency_commission'] == False
    
    def test_no_commission_proprietario(self):
        """Тест объявления от proprietario"""
        description = "Affitto direttamente dal proprietario"
        result = DescriptionAnalyzer.analyze(description)
        assert result['agency_commission'] == False
    
    def test_commission_not_specified(self):
        """Тест когда комиссия не указана"""
        description = "Appartamento in affitto nel centro"
        result = DescriptionAnalyzer.analyze(description)
        assert result['agency_commission'] == None


class TestBuildingType:
    """Тесты определения типа здания"""
    
    def test_historic_building(self):
        """Тест исторического здания"""
        description = "Appartamento in palazzo storico del '700"
        result = DescriptionAnalyzer.analyze(description)
        assert result['building_type'] == "historic"
    
    def test_new_construction(self):
        """Тест новостройки"""
        description = "Nuovo edificio appena costruito"
        result = DescriptionAnalyzer.analyze(description)
        assert result['building_type'] == "new_construction"
    
    def test_renovated_building(self):
        """Тест отремонтированного здания"""
        description = "Appartamento in edificio completamente ristrutturato"
        result = DescriptionAnalyzer.analyze(description)
        assert result['building_type'] == "renovated_building"
    
    def test_modern_building(self):
        """Тест современного здания"""
        description = "Appartamento in edificio moderno"
        result = DescriptionAnalyzer.analyze(description)
        assert result['building_type'] == "modern"
    
    def test_building_type_not_specified(self):
        """Тест когда тип здания не указан"""
        description = "Appartamento spazioso e luminoso"
        result = DescriptionAnalyzer.analyze(description)
        assert result['building_type'] == None


class TestYearBuilt:
    """Тесты извлечения года постройки"""
    
    def test_year_costruito_nel(self):
        """Тест паттерна 'costruito nel'"""
        description = "Palazzo costruito nel 1920"
        result = DescriptionAnalyzer.analyze(description)
        assert result['year_built'] == 1920
    
    def test_year_del(self):
        """Тест паттерна 'del'"""
        description = "Edificio del 1950"
        result = DescriptionAnalyzer.analyze(description)
        assert result['year_built'] == 1950
    
    def test_year_built_in(self):
        """Тест паттерна 'built in'"""
        description = "Building built in 2005"
        result = DescriptionAnalyzer.analyze(description)
        assert result['year_built'] == 2005
    
    def test_year_not_found(self):
        """Тест когда год не найден"""
        description = "Bellissimo appartamento ristrutturato"
        result = DescriptionAnalyzer.analyze(description)
        assert result['year_built'] == None
    
    def test_year_invalid_range(self):
        """Тест невалидного года (слишком старый)"""
        description = "Costruito nel 1799"
        result = DescriptionAnalyzer.analyze(description)
        assert result['year_built'] == None


class TestRenovationType:
    """Тесты определения типа ремонта"""
    
    def test_renovated(self):
        """Тест отремонтированной квартиры"""
        description = "Appartamento completamente ristrutturato"
        result = DescriptionAnalyzer.analyze(description)
        assert result['renovation_type'] == "renovated"
    
    def test_luxury_renovated(self):
        """Тест люксового ремонта (теперь классифицируется как 'renovated')"""
        description = "Appartamento di lusso, completamente ristrutturato"
        result = DescriptionAnalyzer.analyze(description)
        assert result['renovation_type'] == "renovated"
    
    def test_not_renovated(self):
        """Тест не отремонтированной квартиры"""
        description = "Appartamento da ristrutturare"
        result = DescriptionAnalyzer.analyze(description)
        assert result['renovation_type'] == "not_renovated"
    
    def test_renovation_not_specified(self):
        """Тест когда ремонт не указан"""
        description = "Appartamento in centro"
        result = DescriptionAnalyzer.analyze(description)
        assert result['renovation_type'] == None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

