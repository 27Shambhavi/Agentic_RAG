"""
Delete ALL vectors/chunks from the configured Pinecone index.

IMPORTANT:
- Deletes vectors only.
- Does NOT delete the Pinecone index.
- Does NOT delete local PDF files.
"""

import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORT AFTER PROJECT ROOT IS ADDED
# =========================================================

from app.rag.pinecone_client import pinecone_client


# =========================================================
# CLEAR PINECONE
# =========================================================

def clear_pinecone():

    index = pinecone_client.index

    print()
    print("=" * 60)
    print("PINECONE CLEANUP")
    print("=" * 60)

    # -----------------------------------------------------
    # INDEX NAME
    # -----------------------------------------------------

    print(
        f"\nIndex: {pinecone_client.index_name}"
    )

    # -----------------------------------------------------
    # GET STATS
    # -----------------------------------------------------

    stats = index.describe_index_stats()

    print("\nCurrent index statistics:")
    print(stats)

    namespaces = stats.get(
        "namespaces",
        {},
    )

    # -----------------------------------------------------
    # NO VECTORS
    # -----------------------------------------------------

    if not namespaces:

        print(
            "\nNo namespaces/vectors found."
        )

        return

    # -----------------------------------------------------
    # DISPLAY NAMESPACES
    # -----------------------------------------------------

    print("\nFound namespaces:")

    total_vectors = 0

    for namespace, namespace_stats in namespaces.items():

        vector_count = namespace_stats.get(
            "vector_count",
            0,
        )

        total_vectors += vector_count

        display_name = (
            namespace
            if namespace
            else "default"
        )

        print(
            f"  {display_name}: "
            f"{vector_count} vectors"
        )

    print(
        f"\nTotal vectors: {total_vectors}"
    )

    # -----------------------------------------------------
    # CONFIRMATION
    # -----------------------------------------------------

    print()
    print(
        "WARNING: This will delete ALL vectors "
        "from this Pinecone index."
    )

    print(
        "The Pinecone index itself will NOT be deleted."
    )

    confirmation = input(
        "\nType DELETE to continue: "
    ).strip()

    if confirmation != "DELETE":

        print(
            "\nCancelled."
        )

        return

    # -----------------------------------------------------
    # DELETE EACH NAMESPACE
    # -----------------------------------------------------

    for namespace in namespaces:

        display_name = (
            namespace
            if namespace
            else "default"
        )

        print(
            f"\nDeleting namespace: "
            f"{display_name}"
        )

        index.delete(
            delete_all=True,
            namespace=namespace,
        )

        print(
            f"✓ Deleted: {display_name}"
        )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("✓ PINECONE CLEANUP COMPLETE")
    print("=" * 60)

    print(
        "\nAll document chunks/vectors have been removed."
    )

    print(
        "Your Pinecone index is still available."
    )

    print(
        "You can now upload and index documents again."
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    clear_pinecone()