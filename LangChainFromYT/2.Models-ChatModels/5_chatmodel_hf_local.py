from langchain_huggingface import ChatHuggingFace,HuggingFacePipeline

llm = HuggingFacePipeline.from_model_id(
    model_id="Qwen/Qwen3.5-0.8B",
    task="text-generation",
    pipeline_kwargs=dict(
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    ),
)



model = ChatHuggingFace(llm=llm)

result = model.invoke("What are the embedding models in langchain?")


print(result.content)