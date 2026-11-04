

from crawler.retriever import MOSDACRetriever
from llm.llm import MOSDACLLM


class MOSDACRAG:

    def __init__(self):
        print("\nInitializing MOSDAC RAG...")

        self.retriever = MOSDACRetriever()
        self.llm = MOSDACLLM()

        print("MOSDAC RAG initialized successfully.")

    def ask(self, question, history=None):

        history = history or []

        # Build a retrieval query that includes recent context.
        # This helps with follow-ups such as "When was it launched?"
        retrieval_query = question

        if history:
            recent_context = []

            for item in history[-3:]:
                recent_context.append(
                    f"Previous question: {item['question']}"
                )
                recent_context.append(
                    f"Previous answer: {item['answer']}"
                )

            retrieval_query = (
                "\n".join(recent_context)
                + "\nLatest question: "
                + question
            )

        retrieved_data = self.retriever.retrieve_for_llm(
            question=retrieval_query,
            candidate_count=30,
            max_results=8,
        )

        results = retrieved_data["results"]
        context = retrieved_data["context"]

        if not results:
            return {
                "answer": (
                    "The information is not available "
                    "in the MOSDAC knowledge base."
                ),
                "sources": [],
            }

        answer = self.llm.generate_answer(
            question=question,
            context=context,
            history=history,
        )

        sources = []

        for result in results:
            metadata = result["metadata"]

            sources.append({
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page"),
            })

        return {
            "answer": answer,
            "sources": sources,
        }


if __name__ == "__main__":
    rag = MOSDACRAG()

    while True:
        question = input("\nAsk MOSDAC: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        result = rag.ask(question)

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for source in result["sources"]:
            print(source)
