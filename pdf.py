import os
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.readers.file import PDFReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


DATA_DIR = "data"
embed_model = OpenAIEmbedding()
pdf_engines = {}

llm = OpenAI(
    model="gpt-4o-mini-2024-07-18",
    system_prompt="""
Please always answer in clear, structured Markdown. 
- Begin with a one-sentence summary.
- Then provide a numbered or bulleted list of troubleshooting steps, each on its own line.
- Highlight command names and config in backticks (`).
- Use section headings (## or ###) if helpful.
- Use bold or italics for emphasis where useful.
- Never output only a paragraph; always use lists or structure.
"""
)

def get_index(data, index_name, embed_model=None):
    if not os.path.exists(index_name):
        print("building index", index_name)
        index = VectorStoreIndex.from_documents(
            data, 
            embed_model=embed_model,
            show_progress=True
        )
        index.storage_context.persist(persist_dir=index_name)
    else:
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )
    return index

# Scan all PDFs and build/load an engine for each
for pdf_file in os.listdir(DATA_DIR):
    if pdf_file.lower().endswith(".pdf"):
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        index_name = os.path.splitext(pdf_file)[0] + "_index"
        pdf_data = PDFReader().load_data(file=pdf_path)
        index = get_index(pdf_data, index_name, embed_model=embed_model)
        engine = index.as_query_engine(llm=llm)  # <<-- pass LLM with system prompt here!
        pdf_engines[pdf_file] = engine
        print(f"Loaded {len(pdf_data)} chunks from {pdf_file}")
        print(f"Sample text: {pdf_data[0].text[:200] if pdf_data else 'No text loaded!'}")
