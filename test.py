import openai

# List available models
models = openai.Model.list()
print(models)
