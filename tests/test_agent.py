from app.agents.graph import agent


def main():

    print("=" * 60)
    print("       MULTIMODAL AGENTIC RAG ASSISTANT")
    print("=" * 60)

    print("\nType 'exit' to stop.")

    while True:

        query = input("\nYou: ").strip()

        if query.lower() == "exit":
            print("\nGoodbye!")
            break

        if not query:
            continue

        try:

            result = agent.invoke(
                {
                    "query": query
                }
            )

            route = result.get(
                "route",
                "unknown"
            )

            print(
                f"\n[ROUTE] {route}"
            )

            answer = result.get(
                "answer",
                "No answer generated."
            )

            print("\nAssistant:")
            print(answer)

            sources = result.get(
                "sources",
                []
            )

            if sources:

                print("\nSources:")

                for source in sources:

                    # RAG source
                    if "source" in source:

                        print(
                            f"  • {source['source']} "
                            f"| Page {source['page']} "
                            f"| Score {source['score']}"
                        )

                    # Web source
                    elif "title" in source:

                        print(
                            f"  • {source['title']}"
                        )

                        print(
                            f"    {source.get('url', '')}"
                        )

        except Exception as error:

            print("\nAgent Error:")
            print("-" * 60)
            print(error)


if __name__ == "__main__":
    main()