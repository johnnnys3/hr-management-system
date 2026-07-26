from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.test import APITestCase

from config.exceptions import api_exception_handler


class ApiExceptionHandlerTests(APITestCase):
    def test_preserves_an_already_valid_envelope(self):
        exc = ValidationError({'error': {'code': 'x', 'message': 'm', 'fields': None}})
        response = api_exception_handler(exc, {})

        error = response.data['error']
        self.assertEqual(str(error['code']), 'x')
        self.assertEqual(str(error['message']), 'm')
        self.assertIsNone(error['fields'])

    def test_field_validation_error_is_normalized(self):
        exc = ValidationError({'name': ['This field is required.']})
        response = api_exception_handler(exc, {})

        self.assertEqual(response.data['error']['code'], 'validation_error')
        self.assertEqual(response.data['error']['message'], 'This field is required.')
        self.assertEqual(response.data['error']['fields'], {'name': ['This field is required.']})

    def test_non_validation_exception_keeps_its_own_code(self):
        exc = PermissionDenied('Not allowed.')
        response = api_exception_handler(exc, {})

        self.assertEqual(response.data['error']['code'], 'permission_denied')
        self.assertEqual(response.data['error']['message'], 'Not allowed.')
        self.assertIsNone(response.data['error']['fields'])

    def test_not_found_keeps_its_own_code(self):
        exc = NotFound()
        response = api_exception_handler(exc, {})

        self.assertEqual(response.data['error']['code'], 'not_found')

    def test_empty_validation_detail_does_not_crash(self):
        exc = ValidationError([])
        response = api_exception_handler(exc, {})

        self.assertEqual(response.data['error']['fields'], None)
        self.assertTrue(response.data['error']['message'])

    def test_unhandled_exception_returns_none(self):
        self.assertIsNone(api_exception_handler(Exception('boom'), {}))
