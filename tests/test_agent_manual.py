from app.ai.agent import ask_agent


questions = [
    "Investigate claim 16 and tell me if anything should be reviewed."
]


for question in questions:

    print("\n" + "=" * 70)
    print(f"Question: {question}")

    answer = ask_agent(question)

    print(f"Answer: {answer}")
