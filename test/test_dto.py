from unittest import TestCase
from pydto import DTO
from typing import Optional, Dict, List
from datetime import datetime


class TestDTO(TestCase):
    def test_dto_simple_class(self):
        class SimpleDTO(DTO):
            attribute = int,

        dictionary = {"attribute": 1}

        simple_dto = SimpleDTO(dictionary)

        self.assertEqual(simple_dto.attribute, 1)

        self.assertEqual(type(simple_dto.attribute), int)

        # Not Mutable
        with self.assertRaises(AttributeError):
            simple_dto.attribute = 2

    def test_dto_simple_class_wrong_validator(self):
        with self.assertRaises(TypeError):
            class SimpleDTO(DTO):
                attribute = int, {"validator": 1}

    def test_dto_simple_class_valid_validator(self):
        class SimpleDTO(DTO):
            attribute = int, {"validator": lambda x: x > 0}

        dictionary = {"attribute": 1}
        simple_dto = SimpleDTO(dictionary)

        self.assertEqual(simple_dto.attribute, 1)

        self.assertEqual(type(simple_dto.attribute), int)

    def test_dto_simple_class_fails_validation(self):
        class SimpleDTO(DTO):
            attribute = int, {"validator": lambda x: x > 0}

        dictionary = {"attribute": 0}
        with self.assertRaises(ValueError):
            simple_dto = SimpleDTO(dictionary)

    def test_dto_simple_class_type_validation(self):
        class SimpleDTO(DTO):
            attribute = float,

        dictionary = {"attribute": 1}

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO(dictionary)

        dictionary = {"attribute": 1.0}

        simple_dto = SimpleDTO(dictionary)

        self.assertEqual(simple_dto.attribute, 1.0)

        self.assertEqual(type(simple_dto.attribute), float)

        # Not Mutable
        with self.assertRaises(AttributeError):
            simple_dto.attribute = 2

    def test_dto_simple_class_mutable(self):
        class SimpleDTO(DTO):
            attribute = float, {"immutable": False}

        dictionary = {"attribute": 1}

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO(dictionary)

        dictionary = {"attribute": 1.0}

        simple_dto = SimpleDTO(dictionary)

        self.assertEqual(simple_dto.attribute, 1.0)

        self.assertEqual(type(simple_dto.attribute), float)

        # Mutable
        with self.assertRaises(TypeError):
            simple_dto.attribute = 2

        simple_dto.attribute = 2.0

        self.assertEqual(simple_dto.attribute, 2.0)

        self.assertEqual(type(simple_dto.attribute), float)

    def test_dto_simple_class_dictionary_mismatch(self):
        class SimpleDTO(DTO):
            attribute1 = float,
            attribute2 = int,

        dictionary = {"attribute": 1.0}

        with self.assertRaises(AssertionError):
            simple_dto = SimpleDTO(dictionary)

        dictionary = {"attribute1": 1.0}

        with self.assertRaises(AssertionError):
            simple_dto = SimpleDTO(dictionary)

        dictionary = {"attribute1": 1.0, "attribute2": 2, "attribute3": 3.0}

        with self.assertRaises(AssertionError):
            simple_dto = SimpleDTO(dictionary)

        dictionary = {"attribute1": 1.0, "attribute2": 2}

        simple_dto = SimpleDTO(dictionary)

        self.assertEqual(simple_dto.attribute1, 1.0)
        self.assertEqual(type(simple_dto.attribute1), float)

        self.assertEqual(simple_dto.attribute2, 2)
        self.assertEqual(type(simple_dto.attribute2), int)

    def test_dtos_equal(self):
        class SimpleDTO(DTO):
            attribute1 = float,
            attribute2 = int,

        dictionary = {"attribute1": 1.0, "attribute2": 2}

        dto1 = SimpleDTO(dictionary)
        dto2 = SimpleDTO(dictionary)

        self.assertEqual(dto1, dto2)

        dictionary = {"attribute1": 1.1, "attribute2": 2}
        dto2 = SimpleDTO(dictionary)
        self.assertNotEqual(dto1, dto2)

        class SimpleDTO2(DTO):
            attribute1 = float,
            attribute2 = int,

        dictionary = {"attribute1": 1.0, "attribute2": 2}
        dto2 = SimpleDTO2(dictionary)

        self.assertNotEqual(dto1, dto2)

    def test_nested_json_parsing(self):
        class CarDTO(DTO):
            year = int, {"validator": lambda value: value > 1980}
            license = str,

        class AddressDTO(DTO):
            city = str,

        class UserDTO(DTO):
            first_name = str,
            middle_name = str,
            last_name = str,
            birth_date = str,
            car = CarDTO,
            address = AddressDTO,
            email = str, {"immutable": False}
            salary = Optional[float],

        json_string = '{"salary": null, "middle_name": "kurt", "address": {"city": "scranton"}, ' \
                      '"first_name": "dwight", ' \
                      '"email": "dshrute@schrutefarms.com", "car": {"license": "4018 JXT", "year": 1987}, ' \
                      '"last_name": "schrute", "birth_date": "January 20, 1974"}'

        user_dto = UserDTO.from_json(json_string)

        self.assertTrue(True)

    def test_coerce(self):
        class SimpleDTO(DTO):
            age = int,
            date = datetime, {"coerce": lambda value: datetime.strptime(value, '%Y-%m-%d')}

        json_string = '{"age": 25, "date": "2011-01-03"}'

        dto = SimpleDTO.from_json(json_string)

        self.assertEqual(dto.age, 25)
        self.assertEqual(type(dto.age), int)

        self.assertEqual(dto.date, datetime(year=2011, month=1, day=3))
        self.assertEqual(type(dto.date), datetime)

    def test_partial_dto(self):
        class SimpleDTO(DTO, partial=True):
            age = int,

        json_string = '{"age": 25, "date": "2011-01-03"}'

        dto = SimpleDTO.from_json(json_string)

        self.assertEqual(dto.age, 25)
        self.assertEqual(type(dto.age), int)

    def test_partial_nested_dto(self):
        class CarDTO(DTO, partial=True):
            year = int, {"validator": lambda value: value > 1980}
            license = str,

        class AddressDTO(DTO):
            city = str,

        class UserDTO(DTO):
            first_name = str,
            middle_name = str,
            last_name = str,
            birth_date = datetime, {"coerce": lambda value: datetime.strptime(value, '%Y-%m-%d')}
            car = CarDTO,
            address = AddressDTO,
            email = str, {"immutable": False}
            salary = Optional[float],

        json_string = '{"salary": null, "middle_name": "kurt", "address": {"city": "scranton"}, ' \
                      '"first_name": "dwight", ' \
                      '"email": "dshrute@schrutefarms.com", "car": {"license": "4018 JXT", "year": 1987, ' \
                      '"color": "red"}, ' \
                      '"last_name": "schrute", "birth_date": "1974-01-20"}'

        user_dto = UserDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_dict_field(self):
        class SimpleDTO(DTO):
            city = dict,

        json_string = '{"city": null}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": 1}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": 1.0}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": []}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": {}}'

        simple_dto = SimpleDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_Dict_field(self):
        class SimpleDTO(DTO):
            city = Dict[str, str],

        json_string = '{"city": null}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": 1}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": 1.0}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": []}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": {"1": 2}}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": {"1": "2"}}'

        simple_dto = SimpleDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_Dict_field_with_no_subtype(self):
        class SimpleDTO(DTO):
            city = Dict,

        json_string = '{"city": {"1": "2"}}'

        simple_dto = SimpleDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_list_field(self):
        class SimpleDTO(DTO):
            city = list,

        json_string = '{"city": []}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, "1"]}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": null}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": "1"}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": {"1": 2}}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_List_field(self):
        class SimpleDTO(DTO):
            city = List[int],

        json_string = '{"city": []}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, 2]}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, "1"]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": "1"}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": {"1": 2}}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        self.assertTrue(True)

    def test_dto_with_optional_List_field(self):
        class SimpleDTO(DTO):
            city = Optional[List],

        json_string = '{"city": []}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, 2]}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, "1"]}'

        simple_dto = SimpleDTO.from_json(json_string)

    def test_dto_with_optional_nested_type_field(self):
        class SimpleDTO(DTO):
            city = Optional[List[int]],

        json_string = '{"city": []}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1, 2]}'

        simple_dto = SimpleDTO.from_json(json_string)

    def test_do_with_nested_type_field(self):
        class SimpleDTO(DTO):
            city = Optional[List[List[Optional[int]]]],

        json_string = '{"city": null}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": []}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [1]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [{}]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [[]]}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [[1]]}'

        simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [[1.0]]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO.from_json(json_string)

        json_string = '{"city": [[null]]}'

        simple_dto = SimpleDTO.from_json(json_string)

    def test_do_with_nested_type_with_DTO_field(self):

        class SimpleDTO1(DTO, partial=True):
            country = str,

        class SimpleDTO2(DTO):
            city = List[SimpleDTO1],

        json_string = '{"city": []}'

        simple_dto = SimpleDTO2.from_json(json_string)

        json_string = '{"city": [{"country": "canada"}]}'

        simple_dto = SimpleDTO2.from_json(json_string)

        json_string = '{"city": [{"country": "canada", "province": "alberta"}]}'

        simple_dto = SimpleDTO2.from_json(json_string)

        json_string = '{"city": [{"province": "alberta"}]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO2.from_json(json_string)

        json_string = '{"city": [{"country": 1}]}'

        with self.assertRaises(TypeError):
            simple_dto = SimpleDTO2.from_json(json_string)




