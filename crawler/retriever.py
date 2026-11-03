'''import os
import re
import math

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb

from sentence_transformers import SentenceTransformer


class MOSDACRetriever:

    def __init__(self):

        # ==================================================
        # PROJECT ROOT
        # ==================================================

        self.project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ==================================================
        # VECTOR DATABASE
        # ==================================================

        self.vector_db_folder = os.path.join(
            self.project_root,
            "knowledge_base",
            "vector_db"
        )

        print("\nVector DB path:")
        print(self.vector_db_folder)

        # ==================================================
        # EMBEDDING MODEL
        # ==================================================

        print("\nLoading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # ==================================================
        # CHROMADB
        # ==================================================

        print("Connecting to ChromaDB...")

        self.client = chromadb.PersistentClient(
            path=self.vector_db_folder
        )

        self.collection = self.client.get_collection(
            name="mosdac_documents"
        )

        print("Connected to ChromaDB")

        print(
            "Total chunks in vector DB :",
            self.collection.count()
        )

    # ==================================================
    # QUESTION CLEANING
    # ==================================================

    def clean_question(self, question):

        question = question.lower().strip()

        # Remove unnecessary punctuation
        question = re.sub(
            r"[^\w\s\-]",
            " ",
            question
        )

        # Remove extra spaces
        question = re.sub(
            r"\s+",
            " ",
            question
        )

        return question

    # ==================================================
    # EXTRACT KEYWORDS
    # ==================================================

    def extract_keywords(self, question):

        question = self.clean_question(
            question
        )

        words = question.split()

        # Common question words that are usually
        # not useful for document matching.
        stop_words = {

            "what",
            "what is",
            "what are",
            "tell",
            "me",
            "about",
            "give",
            "explain",
            "describe",
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "of",
            "for",
            "to",
            "in",
            "on",
            "from",
            "and",
            "or",
            "how",
            "why",
            "when",
            "where",
            "which",
            "can",
            "could",
            "please",
            "available"
        }

        keywords = []

        for word in words:

            if len(word) < 2:
                continue

            if word in stop_words:
                continue

            keywords.append(word)

        # Remove duplicates while preserving order
        keywords = list(
            dict.fromkeys(keywords)
        )

        return keywords

    # ==================================================
    # DETECT IMPORTANT ENTITY
    # ==================================================

    def extract_entities(self, question):

        entities = []

        # Satellite / mission names commonly contain
        # letters + numbers + optional hyphen.
        patterns = [

            r"\b[A-Z]{2,}-?\d+\b",

            r"\b[A-Z]{2,}\d+\b",

            r"\b[A-Z]{2,}-[A-Z0-9]+\b"

        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                question.upper()
            )

            for match in matches:

                if match not in entities:

                    entities.append(match)

        return entities

    # ==================================================
    # VECTOR SEARCH
    # ==================================================

    def vector_search(
        self,
        question,
        candidate_count=30
    ):

        question_embedding = self.model.encode(
            question,
            normalize_embeddings=True
        ).tolist()

        results = self.collection.query(

            query_embeddings=[
                question_embedding
            ],

            n_results=candidate_count,

            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        candidates = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            if not document:
                continue

            candidates.append({

                "content": document,

                "source_type":
                    metadata.get(
                        "source_type",
                        ""
                    ),

                "source":
                    metadata.get(
                        "source",
                        ""
                    ),

                "page":
                    metadata.get(
                        "page",
                        ""
                    ),

                "images":
                    metadata.get(
                        "images",
                        ""
                    ),

                "distance":
                    float(distance)

            })

        return candidates

    # ==================================================
    # KEYWORD SCORE
    # ==================================================

    def calculate_keyword_score(
        self,
        question,
        document
    ):

        question_lower = (
            self.clean_question(
                question
            )
        )

        document_lower = document.lower()

        keywords = self.extract_keywords(
            question
        )

        if not keywords:
            return 0.0

        matched = 0

        for keyword in keywords:

            if keyword in document_lower:

                matched += 1

        score = matched / len(
            keywords
        )

        return score

    # ==================================================
    # ENTITY SCORE
    # ==================================================

    def calculate_entity_score(
        self,
        question,
        document
    ):

        entities = self.extract_entities(
            question
        )

        if not entities:
            return 0.0

        document_upper = document.upper()

        matched = 0

        for entity in entities:

            if entity in document_upper:

                matched += 1

        return matched / len(
            entities
        )

    # ==================================================
    # TITLE / SOURCE SCORE
    # ==================================================

    def calculate_source_score(
        self,
        question,
        source
    ):

        if not source:
            return 0.0

        keywords = self.extract_keywords(
            question
        )

        if not keywords:
            return 0.0

        source_lower = source.lower()

        matched = 0

        for keyword in keywords:

            if keyword in source_lower:

                matched += 1

        return matched / len(
            keywords
        )

    # ==================================================
    # RE-RANK
    # ==================================================

    def rerank(
        self,
        question,
        candidates
    ):

        reranked = []

        for candidate in candidates:

            distance = candidate[
                "distance"
            ]

            # Convert distance to similarity.
            #
            # Chroma distance:
            # smaller = better
            #
            # This gives a normalized value
            # where larger = better.

            semantic_score = 1 / (
                1 + distance
            )

            keyword_score = (
                self.calculate_keyword_score(
                    question,
                    candidate["content"]
                )
            )

            entity_score = (
                self.calculate_entity_score(
                    question,
                    candidate["content"]
                )
            )

            source_score = (
                self.calculate_source_score(
                    question,
                    candidate["source"]
                )
            )

            # ------------------------------------------------
            # Combined score
            # ------------------------------------------------
            #
            # Semantic similarity is important.
            #
            # Exact entities are given stronger weight
            # because questions such as:
            #
            # "Tell me about KALPANA-1"
            #
            # should strongly prefer chunks containing
            # KALPANA-1.
            #
            # ------------------------------------------------

            final_score = (

                0.45 * semantic_score

                +

                0.25 * keyword_score

                +

                0.25 * entity_score

                +

                0.05 * source_score

            )

            candidate["semantic_score"] = (
                semantic_score
            )

            candidate["keyword_score"] = (
                keyword_score
            )

            candidate["entity_score"] = (
                entity_score
            )

            candidate["source_score"] = (
                source_score
            )

            candidate["final_score"] = (
                final_score
            )

            reranked.append(
                candidate
            )

        # Highest score first
        reranked.sort(
            key=lambda x: x[
                "final_score"
            ],
            reverse=True
        )

        return reranked

    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    def remove_duplicates(
        self,
        results
    ):

        unique_results = []

        seen = set()

        for result in results:

            key = (

                result["source"],

                result["page"],

                result["content"][:150]

            )

            if key in seen:

                continue

            seen.add(key)

            unique_results.append(
                result
            )

        return unique_results

    # ==================================================
    # RELEVANCE FILTER
    # ==================================================

    def filter_relevant_results(
        self,
        question,
        results
    ):

        if not results:

            return []

        entities = self.extract_entities(
            question
        )

        filtered = []

        for result in results:

            final_score = result[
                "final_score"
            ]

            keyword_score = result[
                "keyword_score"
            ]

            entity_score = result[
                "entity_score"
            ]

            distance = result[
                "distance"
            ]

            # ------------------------------------------------
            # Entity question
            # ------------------------------------------------

            if entities:

                # If the question contains an entity such
                # as KALPANA-1, strongly prefer documents
                # that actually contain that entity.

                if entity_score > 0:

                    filtered.append(
                        result
                    )

                continue

            # ------------------------------------------------
            # General question
            # ------------------------------------------------

            # Avoid extremely weak results.

            if (

                final_score >= 0.50

                or keyword_score >= 0.50

            ):

                filtered.append(
                    result
                )

        return filtered

    # ==================================================
    # SEARCH
    # ==================================================

    def search(
        self,
        question,
        candidate_count=30,
        max_results=5
    ):

        print("\n========================================")
        print("SEARCHING MOSDAC KNOWLEDGE BASE")
        print("========================================")

        print(
            "Question :",
            question
        )

        # ------------------------------------------------
        # Clean question
        # ------------------------------------------------

        cleaned_question = (
            self.clean_question(
                question
            )
        )

        print(
            "Processed question :",
            cleaned_question
        )

        # ------------------------------------------------
        # Keywords
        # ------------------------------------------------

        keywords = self.extract_keywords(
            question
        )

        print(
            "Keywords :",
            keywords
        )

        # ------------------------------------------------
        # Entities
        # ------------------------------------------------

        entities = self.extract_entities(
            question
        )

        print(
            "Entities :",
            entities
        )

        # ------------------------------------------------
        # Vector search
        # ------------------------------------------------

        candidates = self.vector_search(

            question=question,

            candidate_count=
                candidate_count

        )

        print(
            "\nVector candidates :",
            len(candidates)
        )

        if not candidates:

            return []

        # ------------------------------------------------
        # Re-rank
        # ------------------------------------------------

        reranked = self.rerank(

            question=question,

            candidates=candidates

        )

        # ------------------------------------------------
        # Remove duplicates
        # ------------------------------------------------

        unique_results = (
            self.remove_duplicates(
                reranked
            )
        )

        # ------------------------------------------------
        # Filter weak results
        # ------------------------------------------------

        filtered_results = (
            self.filter_relevant_results(

                question=question,

                results=unique_results

            )
        )

        # ------------------------------------------------
        # Final results
        # ------------------------------------------------

        final_results = (
            filtered_results[
                :max_results
            ]
        )

        print(
            "\nRelevant chunks found :",
            len(final_results)
        )

        # ------------------------------------------------
        # Display ranking
        # ------------------------------------------------

        for index, result in enumerate(
            final_results,
            start=1
        ):

            print(
                "\nRESULT",
                index
            )

            print(
                "Source :",
                result["source"]
            )

            print(
                "Page :",
                result["page"]
            )

            print(
                "Distance :",
                result["distance"]
            )

            print(
                "Semantic score :",
                result["semantic_score"]
            )

            print(
                "Keyword score :",
                result["keyword_score"]
            )

            print(
                "Entity score :",
                result["entity_score"]
            )

            print(
                "Final score :",
                result["final_score"]
            )

        return final_results

    # ==================================================
    # CREATE LLM CONTEXT
    # ==================================================

    def create_context(
        self,
        results
    ):

        if not results:

            return ""

        context_parts = []

        for index, result in enumerate(
            results,
            start=1
        ):

            part = (
                f"--- SOURCE {index} ---\n"
                f"SOURCE TYPE: "
                f"{result['source_type']}\n"
                f"SOURCE: "
                f"{result['source']}\n"
            )

            if result["page"]:

                part += (
                    f"PAGE: "
                    f"{result['page']}\n"
                )

            if result["images"]:

                part += (
                    f"IMAGES: "
                    f"{result['images']}\n"
                )

            part += (
                "CONTENT:\n"
                f"{result['content']}\n"
            )

            context_parts.append(
                part
            )

        return "\n".join(
            context_parts
        )

    # ==================================================
    # RETRIEVE FOR LLM
    # ==================================================

    def retrieve_for_llm(
        self,
        question,
        candidate_count=30,
        max_results=5
    ):

        results = self.search(

            question=question,

            candidate_count=
                candidate_count,

            max_results=
                max_results

        )

        context = self.create_context(
            results
        )

        return {

            "question":
                question,

            "results":
                results,

            "context":
                context

        }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    retriever = MOSDACRetriever()

    print("\n")
    print("=" * 60)
    print("MOSDAC RETRIEVER TEST")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk a MOSDAC question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":

            print(
                "\nRetriever stopped."
            )

            break

        if not question.strip():

            continue

        data = retriever.retrieve_for_llm(

            question=question,

            candidate_count=30,

            max_results=5

        )

        results = data[
            "results"
        ]

        if not results:

            print(
                "\nNo sufficiently relevant "
                "information found in the "
                "MOSDAC knowledge base."
            )

            continue

        # ------------------------------------------------
        # Show retrieved chunks
        # ------------------------------------------------

        print("\n")
        print("=" * 60)
        print("RETRIEVED INFORMATION")
        print("=" * 60)

        for index, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\nRESULT {index}"
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

            print(
                "Semantic    :",
                result["semantic_score"]
            )

            print(
                "Keyword     :",
                result["keyword_score"]
            )

            print(
                "Entity      :",
                result["entity_score"]
            )

            print(
                "Final Score :",
                result["final_score"]
            )

            if result["images"]:

                print(
                    "Images      :",
                    result["images"]
                )

            print("\nContent:")

            print(
                result["content"]
            )

        # ------------------------------------------------
        # Show context for LLM
        # ------------------------------------------------

        print("\n")
        print("=" * 60)
        print("CONTEXT FOR NVIDIA LLM")
        print("=" * 60)

        print(
            data["context"]
        )
        
'''
import os
import re
import chromadb
from sentence_transformers import SentenceTransformer


class MOSDACRetriever:

    def __init__(self):

        BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
        )

        self.vector_db_folder = os.path.join(
        BASE_DIR,
        "knowledge_base",
        "vector_db"
        )

        print("\nLoading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Vector DB path:")
        print(self.vector_db_folder)

        self.client = chromadb.PersistentClient(
            path=self.vector_db_folder
        )

        self.collection = self.client.get_collection(
            name="mosdac_documents"
        )

        print(
            f"Retriever initialized. "
            f"Total chunks: {self.collection.count()}"
        )

    # =====================================================
    # QUERY CLEANING
    # =====================================================

    def clean_query(self, query):

        query = query.lower()

        # Remove punctuation
        query = re.sub(r"[^a-z0-9\s-]", " ", query)

        # Remove extra spaces
        query = re.sub(r"\s+", " ", query).strip()

        return query

    # =====================================================
    # KEYWORD EXTRACTION
    # =====================================================

    def extract_keywords(self, query):

        query = self.clean_query(query)

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "for",
            "to",
            "in",
            "on",
            "and",
            "or",
            "tell",
            "me",
            "about",
            "please",
            "can",
            "you",
            "give",
            "show",
            "list",
            "available",
            "information"
        }

        words = query.split()

        keywords = [
            word
            for word in words
            if word not in stop_words and len(word) > 2
        ]

        return keywords

    # =====================================================
    # KEYWORD SCORE
    # =====================================================

    def keyword_score(self, query, document):

        query_clean = self.clean_query(query)
        document_clean = self.clean_query(document)

        keywords = self.extract_keywords(query)

        if not keywords:
            return 0.0

        matched = 0

        for keyword in keywords:

            if keyword in document_clean:
                matched += 1

        keyword_score = matched / len(keywords)

        # Exact phrase bonus
        if query_clean in document_clean:
            keyword_score += 0.30

        return min(keyword_score, 1.0)

    # =====================================================
    # QUERY TYPE
    # =====================================================

    def is_broad_question(self, query):

        query_lower = query.lower()

        broad_patterns = [
            "what are",
            "which are",
            "list",
            "available",
            "types of",
            "missions",
            "satellites",
            "services",
            "products",
            "what information"
        ]

        return any(
            pattern in query_lower
            for pattern in broad_patterns
        )

    # =====================================================
    # SOURCE / METADATA SCORE
    # =====================================================

    def metadata_score(self, query, metadata):

        if not metadata:
            return 0.0

        query_clean = self.clean_query(query)

        score = 0.0

        source = str(
            metadata.get("source", "")
        ).lower()

        title = str(
            metadata.get("title", "")
        ).lower()

        section = str(
            metadata.get("section", "")
        ).lower()

        # Exact query words in metadata
        keywords = self.extract_keywords(query)

        for keyword in keywords:

            if keyword in title:
                score += 0.20

            if keyword in section:
                score += 0.15

            if keyword in source:
                score += 0.10

        return min(score, 1.0)

    # =====================================================
    # RETRIEVE CANDIDATES FROM CHROMA
    # =====================================================

    def retrieve_candidates(
        self,
        question,
        candidate_count=30
    ):

        query_embedding = self.model.encode(
            [question]
        )[0]

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=candidate_count,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        candidates = []

        for i in range(len(documents)):

            document = documents[i]

            metadata = (
                metadatas[i]
                if i < len(metadatas)
                else {}
            )

            distance = (
                distances[i]
                if i < len(distances)
                else 999
            )

            candidates.append({
                "content": document,
                "metadata": metadata,
                "distance": distance
            })

        return candidates

    # =====================================================
    # RANK RESULTS
    # =====================================================

    def rank_results(
        self,
        question,
        candidates
    ):

        ranked = []

        broad_question = self.is_broad_question(
            question
        )

        for item in candidates:

            distance = item["distance"]

            # Convert distance to similarity-like score.
            # Smaller distance = better.
            semantic_score = 1 / (1 + distance)

            keyword_score = self.keyword_score(
                question,
                item["content"]
            )

            metadata_score = self.metadata_score(
                question,
                item["metadata"]
            )

            # Normal question weighting
            final_score = (
                semantic_score * 0.50
                + keyword_score * 0.35
                + metadata_score * 0.15
            )

            # Broad/list questions need stronger keyword matching.
            if broad_question:

                final_score = (
                    semantic_score * 0.40
                    + keyword_score * 0.45
                    + metadata_score * 0.15
                )

            item["semantic_score"] = semantic_score
            item["keyword_score"] = keyword_score
            item["metadata_score"] = metadata_score
            item["final_score"] = final_score

            ranked.append(item)

        ranked.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return ranked

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    def remove_duplicates(self, results):

        unique_results = []

        seen = set()

        for item in results:

            metadata = item["metadata"]

            source = str(
                metadata.get("source", "")
            )

            page = str(
                metadata.get("page", "")
            )

            content = item["content"]

            key = (
                source,
                page,
                content[:150]
            )

            if key in seen:
                continue

            seen.add(key)

            unique_results.append(item)

        return unique_results

    # =====================================================
    # MAIN RETRIEVAL FUNCTION
    # =====================================================

    def retrieve(
        self,
        question,
        candidate_count=30,
        max_results=8
    ):

        candidates = self.retrieve_candidates(
            question,
            candidate_count
        )

        ranked = self.rank_results(
            question,
            candidates
        )

        ranked = self.remove_duplicates(
            ranked
        )

        final_results = ranked[:max_results]

        return final_results

    # =====================================================
    # BUILD LLM CONTEXT
    # =====================================================

    def build_context(self, results):

        context_parts = []

        for index, result in enumerate(
            results,
            start=1
        ):

            metadata = result["metadata"]

            source = metadata.get(
                "source",
                "Unknown source"
            )

            page = metadata.get(
                "page",
                ""
            )

            title = metadata.get(
                "title",
                ""
            )

            section = metadata.get(
                "section",
                ""
            )

            content = result["content"]

            context_parts.append(
                f"""
SOURCE {index}
-------------------------
Document: {source}
Title: {title}
Section: {section}
Page: {page}

Content:
{content}
"""
            )

        return "\n".join(
            context_parts
        )

    # =====================================================
    # FUNCTION USED BY RAG
    # =====================================================

    def retrieve_for_llm(
        self,
        question,
        candidate_count=30,
        max_results=8
    ):

        results = self.retrieve(
            question=question,
            candidate_count=candidate_count,
            max_results=max_results
        )

        context = self.build_context(
            results
        )

        return {
            "question": question,
            "results": results,
            "context": context
        }