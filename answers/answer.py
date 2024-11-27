from dataclasses import dataclass, fields
from typing import Any

@dataclass
class Answer:
    """
    Saves an answer from a particular model about a certain question.
    """
    unique_ID: str
    category: str
    sub_category: str
    question_in_Chinese: str
    question_in_English: str
    answer: str
    occurrence: int
    model_output: str
    num_new_tokens: int
    speed: float
    model: str
    mark: int | None = None
    need_rerun: bool = False
    confidence_level: str = ""
    additional_info: str = ""

    def to_markdown(self) -> str:
        """
        Converts the output of the model to Markdown for human inspection
        :return: String in Markdown format
        """
        # Preprocess model output
        adjusted_model_output = self.model_output

        # More than 2 `\n`'s count as one line break
        adjusted_model_output = adjusted_model_output.replace("\n", "\n\n")

        adjusted_model_output = adjusted_model_output.replace("\\(", "$")
        adjusted_model_output = adjusted_model_output.replace("\\)", "$")
        adjusted_model_output = adjusted_model_output.replace("\\[", "$$")
        adjusted_model_output = adjusted_model_output.replace("\\]", "$$")

        return f'''## UID: {self.unique_ID}

<!-- Model: {self.model} -->

Instance {self.occurrence}

{self.category} - {self.sub_category}

**Question in Chinese**: {self.question_in_Chinese}

**Question in English**: {self.question_in_English}

**Model's answer:**

<div style="border: 2px solid red; padding: 10px; width: fit-content;">

{adjusted_model_output}
</div>

**Answer provided by question setter:**

{self.answer}

**Mark (0~100/None):** 

**Needs rerun (Y/N):** 

**Confidence:** 

**Additional Info:** 

---<!-- This is the end of this segment -->\n\n
'''

    def fill_post_info(self, mark: int | None, need_rerun: bool, confidence_level: str, additional_info: str) -> None:
        """
        Fills other info that need human filling in

        :param mark: Whether the answer is correct
        :param need_rerun: Whether the answer needs a rerun
        :param confidence_level: The model's confidence level as it says
        :param additional_info: Any other information need recording
        :return: None
        """
        self.mark = mark
        self.need_rerun = need_rerun
        self.confidence_level = confidence_level
        self.additional_info = additional_info

    def to_dct(self) -> dict[str, Any]:
        """
        Converts `Answer` object to a dictionary

        :return: Dictionary of `Answer` object
        """
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_dct(cls, dct):
        """
        Converts dictionary back into `Answer` object
        :param dct: Dictionary containing data of an `Answer` instance
        :return: `Answer` object
        """
        return cls(**dct)
