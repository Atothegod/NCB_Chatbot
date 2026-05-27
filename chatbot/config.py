from dotenv import load_dotenv
load_dotenv()

import litellm
import os
import dspy

lm = dspy.LM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("API_KEY_2"),
    temperature=0
)

dspy.settings.configure(lm=lm)


# litellm.ssl_verify = False


# llm = dspy.LM(
#     model="openai/gpt-oss:20b",
#     api_base=os.getenv("LLM_URL"),
#     api_key=os.getenv("API_KEY"),
#     temperature=0
# )

# dspy.configure(lm=llm)
# print("LLM_URL =", os.getenv("LLM_URL"))
# print("API_KEY =", os.getenv("API_KEY"))