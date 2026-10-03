import pytest
from filing_analyst.llm import FinancialAnswer
from pydantic import ValidationError


def test_valid_answer_is_accepted():
    text = (
        '{"company": "Apple Inc.", "fiscal_year": 2024, '
        '"metric": "Total revenue", '
        '"value_usd": 391035000000, "source": "memory"}'
    )

    answer = FinancialAnswer.model_validate_json(text)
    assert answer.fiscal_year == 2004


def test_text_year_is_rejected():
    text = (
        '{"company": "Apple Inc.", "fiscal_year": "FY24", '
        '"metric": "Total revenue", '
        '"value_usd": 391035000000, "source": "memory"}'
    )
    with pytest.raises(ValidationError):
         FinancialAnswer.model_validate_json(text)     

def test_missing_field_is_rejected():
    text = (
        '{"company": "Apple Inc.", "fiscal_year": 2024, '
        '"metric": "Total revenue", "source": "memory"}'
    )
    with pytest.raises(ValidationError):
        FinancialAnswer.model_validate_json(text)


def test_value_is_a_real_number():
    text = (
        '{"company": "Apple Inc.", "fiscal_year": 2024, '
        '"metric": "Total revenue", '
        '"value_usd": 391035000000, "source": "memory"}'
    )
    answer = FinancialAnswer.model_validate_json(text)
    assert answer.value_usd * 2 == 782070000000


def test_wrong_source_is_rejected():
    text = (
        '{"company": "Apple Inc.", "fiscal_year": 2024, '
        '"metric": "Total revenue", '
        '"value_usd": 391035000000, "source": "web"}'
    )
    with pytest.raises(ValidationError):
        FinancialAnswer.model_validate_json(text)      

def test_get_annual_fact:
    

