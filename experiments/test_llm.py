from src.models.llm import llm

response = llm.invoke("Say hello in one sentence.")

print(type(response))
print("\n========== AIMessage ==========")
print(response)

print("\n========== Content ==========")
print(response.content)

print("\n========== Metadata ==========")
print(response.response_metadata)

print("\n========== Usage ==========")
print(response.usage_metadata)

