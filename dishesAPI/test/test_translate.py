import os
import pytest
from unittest import mock
from rest_framework.test import APIRequestFactory
from django.http import HttpRequest
from dishesAPI import views

# 1. Test: Traducción exitosa
def test_translate_fields_success(monkeypatch):
    data = [{'name': 'Hola'}]
    fields = ['name']
    target_lang = 'EN-GB'

    class FakeTranslation:
        def __init__(self, text):
            self.text = text
    class FakeTranslator:
        def __init__(self, key):
            pass
        def translate_text(self, texts, target_lang=None):
            return [FakeTranslation('Hello') for _ in texts]

    monkeypatch.setenv('DEEPL_AUTH_KEY', 'fake-key')
    monkeypatch.setattr(views.deepl, 'Translator', FakeTranslator)

    views.translate_fields(data, fields, target_lang)
    assert data[0]['name'] == 'Hello'

# 2. Test: Falta de API key
def test_translate_fields_no_api_key(monkeypatch):
    data = [{'name': 'Hola'}]
    fields = ['name']
    target_lang = 'EN-GB'
    monkeypatch.delenv('DEEPL_AUTH_KEY', raising=False)
    with pytest.raises(ValueError) as exc:
        views.translate_fields(data, fields, target_lang)
    assert 'DeepL API key is not configured' in str(exc.value)

# 3. Test: Excepción de DeepL
def test_translate_fields_deepl_exception(monkeypatch):
    data = [{'name': 'Hola'}]
    fields = ['name']
    target_lang = 'EN-GB'
    class FakeDeepLException(Exception):
        pass
    class FakeTranslator:
        def __init__(self, key):
            pass
        def translate_text(self, texts, target_lang=None):
            raise views.deepl.exceptions.DeepLException('DeepL error')
    monkeypatch.setenv('DEEPL_AUTH_KEY', 'fake-key')
    monkeypatch.setattr(views.deepl, 'Translator', FakeTranslator)
    monkeypatch.setattr(views.deepl, 'exceptions', views.deepl.exceptions)
    with pytest.raises(views.deepl.exceptions.DeepLException):
        views.translate_fields(data, fields, target_lang)

# 4. Test: Excepción genérica
def test_translate_fields_generic_exception(monkeypatch):
    data = [{'name': 'Hola'}]
    fields = ['name']
    target_lang = 'EN-GB'
    class FakeTranslator:
        def __init__(self, key):
            pass
        def translate_text(self, texts, target_lang=None):
            raise Exception('Generic error')
    monkeypatch.setenv('DEEPL_AUTH_KEY', 'fake-key')
    monkeypatch.setattr(views.deepl, 'Translator', FakeTranslator)
    with pytest.raises(Exception) as exc:
        views.translate_fields(data, fields, target_lang)
    assert 'Generic error' in str(exc.value)

# 5. Test: Idioma no soportado en la view
def test_translate_response_unsupported_language():
    class DummyRequest:
        query_params = {'lang': 'FR'}
    data = [{'category_name': 'Hola'}]
    view = views.CategoryViewSet()
    with pytest.raises(ValueError) as exc:
        view.translate_response(data, ['category_name'], DummyRequest())
    assert 'not supported' in str(exc.value)

# 6. Test: No se traduce si idioma es ES
def test_translate_response_no_translation(monkeypatch):
    class DummyRequest:
        query_params = {'lang': 'ES'}
    data = [{'category_name': 'Hola'}]
    view = views.CategoryViewSet()
    # Patch translate_fields to fail if called
    monkeypatch.setattr(views, 'translate_fields', lambda *a, **k: (_ for _ in ()).throw(Exception('Should not be called')))
    # Should not raise
    view.translate_response(data, ['category_name'], DummyRequest())
    assert data[0]['category_name'] == 'Hola'
