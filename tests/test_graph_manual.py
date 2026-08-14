from app.ai.graph import run_graph_with_metadata


question = (
    "Does claim 16 have any risk indicators?"
)

result = run_graph_with_metadata(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(result["answer"])

print("\nTools used:")
print(result["tools_used"])