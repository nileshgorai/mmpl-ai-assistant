import numpy as np

from gpt_engine import generate_ai_answer

def retrieve_answer(
    question,
    csv_path,
    vectorstore,
    chunks
):

    print("\nConverting question into embedding...\n")
    index = vectorstore["index"]

    model = vectorstore["model"]

    # Convert question to embedding
    question_embedding = model.encode([question])

    question_embedding = np.array(question_embedding)

    print("\nSearching relevant chunks...\n")

    # Search top 2 similar chunks
    distances, indices = index.search(
        question_embedding,
        k=5
    )

    print("\n===== MOST RELEVANT CHUNKS =====\n")
    print(f"\nRetrieved {len(indices[0])} relevant engineering records.\n")

    relevant_text = """
    Relevant Industrial Maintenance Report Data:

    The following sections were retrieved
    using semantic similarity search from
    the industrial maintenance dataset.

    Use these records for engineering analysis,
    downtime interpretation, operational insights,
    failure reasoning, and maintenance recommendations.

    """

    for count, i in enumerate(indices[0], start=1):

        relevant_text += (
            f"\n===== ENGINEERING RECORD {count} =====\n"
            f"{chunks[i]}\n\n"
        )

    print("\nSending context to GPT...\n")

    gpt_answer = generate_ai_answer(
        question,
        relevant_text
    )

    return gpt_answer

