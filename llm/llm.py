import os

from dotenv import load_dotenv
from openai import OpenAI


class MOSDACLLM:

    def __init__(self):

        # ==================================================
        # LOAD ENVIRONMENT VARIABLES
        # ==================================================

        load_dotenv()

        self.api_key = os.getenv(
            "NVIDIA_API_KEY"
        )

        if not self.api_key:

            raise ValueError(
                "NVIDIA_API_KEY not found in .env file"
            )

        # ==================================================
        # NVIDIA CLIENT
        # ==================================================

        self.client = OpenAI(

            base_url=(
                "https://integrate.api.nvidia.com/v1"
            ),

            api_key=self.api_key

        )

        # ==================================================
        # MODEL
        # ==================================================

        self.model = (
            "nvidia/nemotron-3.5-lightning-30b-a3b"
        )

        print("NVIDIA LLM connected")

    # ==================================================
    # GENERATE ANSWER
    # ==================================================

    def generate_answer(
        self,
        question,
        context
    ):

        # ==================================================
        # RAG PROMPT
        # ==================================================

        prompt = f"""
You are the MOSDAC information assistant.

Answer the user's question using ONLY the supplied MOSDAC context.

Rules:

1. Do not use information that is not present in the context.
2. Do not invent facts.
3. If the context does not contain the answer, say:
   "The information is not available in the MOSDAC knowledge base."
4. Give only the final answer.
5. Do not describe your reasoning or analysis.
6. Do not repeat the question.
7. Be concise but informative.
8. When the context contains technical specifications, preserve the values exactly.
9. If multiple sources are relevant, combine them carefully.
10. Do not use unrelated information from the context.

---------------- CONTEXT ----------------

{context}

-------------- END CONTEXT --------------

USER QUESTION:

{question}

Provide the answer based on the MOSDAC context.
"""

        # ==================================================
        # SEND TO NVIDIA
        # ==================================================

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are a reliable "
                        "MOSDAC information assistant."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.2,

            max_tokens=1000

        )

        # ==================================================
        # GET ANSWER
        # ==================================================

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        return answer
    