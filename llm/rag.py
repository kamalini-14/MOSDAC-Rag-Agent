from crawler.retriever import MOSDACRetriever
from llm.llm import MOSDACLLM




class MOSDACRAG:

    def __init__(self):

        print("\n")
        print("=" * 60)
        print("INITIALIZING MOSDAC RAG SYSTEM")
        print("=" * 60)

        print("\nLoading Retriever...")

        self.retriever = MOSDACRetriever()

        print("Retriever loaded successfully")

        print("\nLoading NVIDIA LLM...")

        self.llm = MOSDACLLM()

        print("NVIDIA LLM loaded successfully")

        print("\n" + "=" * 60)
        print("MOSDAC RAG SYSTEM READY")
        print("=" * 60)
    def ask(self, question):

        print("\n")
        print("=" * 60)
        print("STEP 1 : RETRIEVING INFORMATION")
        print("=" * 60)

        print("Question :", question)


        retrieved_data = self.retriever.retrieve_for_llm(

            question=question,

            candidate_count=10,

            max_results=5

        )

        results = retrieved_data["results"]

        context = retrieved_data["context"]


        print("\nRelevant chunks found :", len(results))

        if not results:

            return {
                "answer":
                    "I could not find this information "
                    "in the MOSDAC knowledge base.",

                "sources": []
            }

        print("\n")
        print("=" * 60)
        print("RETRIEVED INFORMATION")
        print("=" * 60)

        for index, result in enumerate(
            results,
            start=1
        ):

            print("\n----------------------------------------")

            print(
                f"RESULT {index}"
            )

            print(
                "Source Type :",
                result["source_type"]
            )

            print(
                "Source      :",
                result["source"]
            )

            print(
                "Page        :",
                result["page"]
            )

            print(
                "Distance    :",
                result["distance"]
            )

        

        print("\n")
        print("=" * 60)
        print("STEP 2 : GENERATING ANSWER")
        print("=" * 60)

        print("Sending retrieved context to NVIDIA LLM...")

        answer = self.llm.generate_answer(

            question=question,

            context=context

        )


       

        sources = []

        for result in results:

            sources.append({

                "source_type":
                    result["source_type"],

                "source":
                    result["source"],

                "page":
                    result["page"],

                "images":
                    result["images"],

                "distance":
                    result["distance"]

            })


        return {

            "answer": answer,

            "sources": sources

        }



if __name__ == "__main__":

    rag = MOSDACRAG()

    print("\n")
    print("=" * 60)
    print("MOSDAC RAG CHATBOT")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk a MOSDAC question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":

            print("\nChatbot stopped.")

            break

        if not question.strip():

            continue

        result = rag.ask(question)

      

        print("\n")
        print("=" * 60)
        print("FINAL MOSDAC ANSWER")
        print("=" * 60)

        print(
            result["answer"]
        )

                                     

        print("\n")
        print("=" * 60)
        print("SOURCES USED")
        print("=" * 60)

        for index, source in enumerate(
            result["sources"],
            start=1
        ):

            print(
                f"\nSource {index}"
            )

            print(
                "Type :",
                source["source_type"]
            )

            print(
                "File :",
                source["source"]
            )

            if source["page"]:

                print(
                    "Page :",
                    source["page"]
                )

            if source["images"]:

                print(
                    "Images :",
                    source["images"]
                )