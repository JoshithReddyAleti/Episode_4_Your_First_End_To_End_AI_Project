"""
tests/test_tools.py — Tool Unit Tests (Episode 4)
===================================================
Now covering 4 tools: calculator, weather, wikipedia, converter

Run with: pytest tests/test_tools.py -v
"""

import pytest
from app.tools.calculator import run as calc_run
from app.tools.weather_api import run as weather_run
from app.tools.wikipedia_tool import run as wiki_run
from app.tools.unit_converter import run as converter_run


class TestCalculatorTool:

    def test_percentage(self):
        result = calc_run("What is 25% of 480?")
        assert result["error"] is None
        assert result["result"] == pytest.approx(120.0)

    def test_addition(self):
        result = calc_run("What is 100 plus 250?")
        assert result["error"] is None
        assert result["result"] == pytest.approx(350.0)

    def test_division_by_zero(self):
        result = calc_run("What is 100 divided by 0?")
        assert result["error"] is not None

    def test_no_numbers(self):
        result = calc_run("What is the meaning of life?")
        assert result["error"] is not None

    def test_output_keys(self):
        result = calc_run("What is 10 plus 5?")
        for key in ("result", "expression", "query", "error"):
            assert key in result


class TestWeatherTool:

    def test_output_keys(self):
        result = weather_run("Weather in London?")
        for key in ("location", "temperature", "condition", "unit", "error"):
            assert key in result

    def test_nonsense_location(self):
        result = weather_run("Weather in Xyzqwertyville?")
        assert isinstance(result, dict)

    def test_empty_query(self):
        result = weather_run("")
        assert isinstance(result, dict)


class TestWikipediaTool:

    def test_output_keys(self):
        result = wiki_run("Tell me about Python programming")
        for key in ("title", "summary", "url", "error"):
            assert key in result

    @pytest.mark.integration
    def test_known_topic(self):
        result = wiki_run("Tell me about Albert Einstein")
        assert result["error"] is None
        assert result["title"] is not None
        assert len(result["summary"]) > 50

    def test_nonsense_topic(self):
        result = wiki_run("Tell me about Xyzqwertyville123abc")
        assert isinstance(result, dict)

    def test_empty_query(self):
        result = wiki_run("")
        assert result.get("error") is not None or result.get("title") is None


class TestUnitConverterTool:

    def test_fahrenheit_to_celsius(self):
        result = converter_run("Convert 100 F to C")
        assert result["error"] is None
        assert result["result"] == pytest.approx(37.7778, rel=0.01)

    def test_celsius_to_fahrenheit(self):
        result = converter_run("Convert 0 C to F")
        assert result["error"] is None
        assert result["result"] == pytest.approx(32.0)

    def test_km_to_miles(self):
        result = converter_run("100 km to miles")
        assert result["error"] is None
        assert result["result"] == pytest.approx(62.14, rel=0.01)

    def test_kg_to_lbs(self):
        result = converter_run("50 kg to lbs")
        assert result["error"] is None
        assert result["result"] == pytest.approx(110.23, rel=0.01)

    def test_output_keys(self):
        result = converter_run("100 F to C")
        for key in ("value", "from_unit", "to_unit", "result", "error"):
            assert key in result

    def test_unparseable_query(self):
        result = converter_run("What is the meaning of life?")
        assert result["error"] is not None

    def test_expression_in_output(self):
        result = converter_run("5 miles to km")
        assert result["error"] is None
        assert result["expression"] is not None
