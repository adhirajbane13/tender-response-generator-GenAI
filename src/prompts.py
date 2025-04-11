def build_rag_prompt(context_chunks, user_query):
    context = "\n\n".join(
        f"{i+1}. {title}\n{content.strip()}"
        for i, (title, content) in enumerate(context_chunks)
    )

    prompt = f"""
You are a helpful assistant that answers questions about public tenders and RFPs (Requests for Proposals).
Using only the provided context sections from a tender document, answer the question clearly and factually.

- If the answer is not present, say: "The document does not contain this information."
- Be concise and use information from the sections directly.

Question: {user_query}

Context:
{context}
"""
    return prompt

