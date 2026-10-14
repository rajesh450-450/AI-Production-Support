from src.tools.registry import registry

print("Registered tools:")

for tool in registry.get_all():
    print(tool.name)