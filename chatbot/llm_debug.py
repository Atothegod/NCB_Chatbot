import dspy
import config


class SimpleQA(dspy.Signature):

    question = dspy.InputField()
    answer = dspy.OutputField()


qa = dspy.Predict(SimpleQA)


result = qa(
    question="What is the capital of Thailand? and how many people live there?"
)

print("RESULT =", result)
print("ANSWER =", result.answer)