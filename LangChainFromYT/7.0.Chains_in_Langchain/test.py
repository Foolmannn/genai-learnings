from huggingface_hub import HfApi

api = HfApi()

models = api.list_models(
    pipeline_tag="text-generation"
)

for model in list(models)[:20]:
    print(model.id)