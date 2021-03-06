import json

from app import db
from tests import BaseTestCase, DATA_KEY, ERRORS_KEY


class FunctionalTestCase (BaseTestCase):
    """Test case base class that contains db setup and request checking for functional test cases"""

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def save_objects(self, *objects):
        for object in objects:
            db.session.add(object)
        db.session.commit()

    # All global response
    def check_response_code_and_headers(self, response, expected_code):
        self.check_response_code(response, expected_code)
        self.check_response_headers_content_type(response)

    def check_response_headers_content_type(self, response):
        self.assertEquals(response.headers['Content-Type'], 'application/json')

    def check_response_code(self, response, expected_code):
        self.assertEquals(response.status_code, expected_code, "response code not " + str(expected_code))

    # Unpack extant response values
    def unpack_extant_response_data(self, response):
        data_dict = json.loads(response.data)[DATA_KEY]
        self.assertIsNotNone(data_dict)
        return data_dict

    def unpack_extant_response_errors(self, response):
        error_arr = json.loads(response.data)[ERRORS_KEY]
        self.assertIsNotNone(error_arr)
        return error_arr

    # Key extant checks
    def check_data_not_in_response(self, response):
        self.check_key_not_in_response(DATA_KEY, response)

    def check_errors_not_in_response(self, response):
        self.check_key_not_in_response(ERRORS_KEY, response)

    def check_key_not_in_response(self, key, response):
        self.assertNotIn(key, response.data)

    # Convenience checks
    def check_response_contains_only_auth_error(self, response):
        # TODO Define error codes
        self.check_response_contains_only_error(101, response)

    def check_response_contains_only_missing_parameter_error(self, response):
        # TODO Define error codes
        self.check_response_contains_only_error(100, response)

    def check_response_contains_only_error(self, expected_code, response):
        """Validates no data exists, validates errors array does exist and checks for expected error code."""
        self.check_data_not_in_response(response)
        error_arr = self.unpack_extant_response_errors(response)
        self.__check_for_error(expected_code, error_arr)

    def __check_for_error(self, error_code, error_arr):
        self.assertGreater(len(error_arr), 0)
        for error in error_arr:
            code = error['code']
            self.assertIsNotNone(code)
            self.assertEquals(code, error_code)
            self.assertIsNotNone(error['message'])