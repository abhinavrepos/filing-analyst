from typing import Literal
from google import genai

from pydantic import BaseModel, Field


class FinancialAnswer(BaseModel):
    company: str = Field(
        description="Full legal company name, e.g. 'Apple Inc.'"
    )

    fiscal_year: int = Field(
        description="Fiscal year as a 4-digit number, e.g. 2024. "
        "Use the company's own fiscal year, not the calendar year."
    )

    metric: str = Field(
        description="The financial measure, e.g. 'Total revenue' "
        "or 'Operating income'"
    )

    value_usd: float = Field(
        description="The value in US dollars as a plain number, "
        "not abbreviated. Write 391035000000, not '391B'."
    )

    source: Literal["memory", "document"] = Field(
        description="'memory' if from your training data, "
        "'document' if read from a provided filing"
    )

def ask_llm(question:str) -> FinancialAnswer:
    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=question,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": FinancialAnswer.model_json_schema(),
        },
    )
        
    return FinancialAnswer.model_validate_json(interaction.output_text)


if __name__ == "__main__":
    answer = ask_llm(
        "What was Apple's total revenue in "
        "fiscal 2024? Answer from memory."
    )
    print(answer)
   





