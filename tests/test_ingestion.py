import sys
import os
sys.path.append(".")

from app.services.ingest_service import (
    ensure_dirs,
    ingest_document,
    delete_document,
    PENDING_DIR
)


def test_ingestion():
    """Test 2 — ingest a sample document."""

    # setup
    ensure_dirs()

    # create a sample txt file in pending folder
    sample_file = os.path.join(PENDING_DIR, "test_doc.txt")
    with open(sample_file, "w",encoding="utf-8") as f:
        f.write("""
        Project X — Kubernetes Setup POC

        We deployed a GKE cluster on GCP for client XYZ.
        
        Architecture:
        - 3 node pools: frontend, backend, database
        - Autopilot mode disabled for custom configuration
        - Node pool machine type: e2-standard-4
        
        Issues faced:
        - Pod scheduling issues due to resource limits
        - Fixed by adjusting CPU and memory requests
        
        Commands used:
        gcloud container clusters create project-x-cluster \
            --zone us-central1-a \
            --num-nodes 3 \
            --machine-type e2-standard-4
        """)

    print(f"Created sample file: {sample_file}")

    # test ingestion
    result = ingest_document(
        document_id="test-doc-001",
        file_name="test_doc.txt",
        uploaded_by="test-user"
    )

    print(f"Ingestion result: {result}")
    assert result["status"] == "ingested"
    assert result["chunk_count"] > 0
    print("✅ Ingestion test passed!")

    return result


def test_deletion():
    """Test 3 — delete an ingested document."""
    result = delete_document(
        document_id="test-doc-001",
        file_name="test_doc.txt"
    )
    print(f"Deletion result: {result}")
    assert result["status"] == "deleted"
    print("✅ Deletion test passed!")


if __name__ == "__main__":
    test_ingestion()
    # test_deletion()