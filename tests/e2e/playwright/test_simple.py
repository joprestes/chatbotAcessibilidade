import pytest
from playwright.sync_api import Page
from axe_playwright_python.sync_playwright import Axe


@pytest.fixture
def axe():
    return Axe()


def test_simple_playwright(page: Page):
    page.goto("http://localhost:8000")
    assert page.title() is not None


def test_simple_axe(page: Page, axe):
    page.goto("http://localhost:8000")
    results = axe.run(page)
    assert results is not None
