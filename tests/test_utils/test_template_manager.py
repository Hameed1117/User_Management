import pytest
from app.utils.template_manager import TemplateManager
from unittest.mock import patch, mock_open

@pytest.fixture
def manager():
    return TemplateManager()

def test_read_template_reads_file(manager):
    fake_markdown = "# Hello"
    with patch("builtins.open", mock_open(read_data=fake_markdown)) as mocked_file:
        with patch("pathlib.Path.__truediv__", return_value="fake_path.md"):
            content = manager._read_template("welcome.md")
            mocked_file.assert_called_once_with("fake_path.md", "r", encoding="utf-8")
            assert content == fake_markdown

def test_apply_email_styles_applies_styles(manager):
    input_html = "<h1>Welcome</h1><p>This is a test.</p>"
    output_html = manager._apply_email_styles(input_html)
    assert '<h1 style="' in output_html
    assert '<p style="' in output_html
    assert '<div style="' in output_html

def test_render_template_combines_all(manager):
    fake_header = "# Header"
    fake_footer = "# Footer"
    fake_body = "Hello, {name}!"

    with patch.object(manager, "_read_template", side_effect=[fake_header, fake_footer, fake_body]):
        rendered = manager.render_template("welcome", name="Khadhar")
        assert "Khadhar" in rendered
        assert "<div style=" in rendered
        assert "<h1" in rendered or "<p" in rendered
