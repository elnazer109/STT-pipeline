import json
import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


class PromptGeneratorService:

    def __init__(
        self,
        api_key,
        model_name="llama-3.3-70b-versatile",
        output_path="outputs/prompts.json"
    ):

        self.model_name = model_name
        self.output_path = output_path

        self.client = Groq(
            api_key=api_key
        )

    def build_prompt(self, count):

        prompt = f"""
Generate {count} realistic Egyptian Arabic spoken sentences.

Requirements:
- Write ONLY using Arabic letters
- Use Egyptian Arabic dialect only
- Use casual street-style Egyptian speech
- Do NOT use Modern Standard Arabic (MSA)
- Do NOT use formal Arabic expressions
- Do NOT use Franco Arabic
- Do NOT use English words or letters
- The sentences should sound like real conversations between Egyptians
- Use simple everyday language
- Mix short and medium-length sentences
- Output ONLY the sentences
- No numbering
- No introductions
- No explanations

Examples of GOOD style:
- عامل ايه النهارده
- هتيجي امتى
- ابعتلي اللوكيشن
- الاكل وصل ولا لسه
- انا جعان موت

Examples of BAD style:
- كيف حالك يا صديقي
- سوف اذهب الان
- اريد تناول الطعام
- مرحبا كيف يمكنني مساعدتك

Now generate the sentences.
"""

        return prompt

    def generate_prompts(self, count=50):

        prompt = self.build_prompt(count)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        text = response.choices[0].message.content

        prompts = []

        for line in text.split("\n"):

            cleaned = line.strip()

            if cleaned:

                cleaned = cleaned.lstrip(
                    "0123456789.- "
                )

                if len(cleaned) > 2:
                    prompts.append(cleaned)

        return prompts

    def save_prompts(
        self,
        prompts,
        output_path=None
    ):

        if output_path is None:
            output_path = self.output_path

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                prompts,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(
            f"Prompts saved at: {output_path}"
        )