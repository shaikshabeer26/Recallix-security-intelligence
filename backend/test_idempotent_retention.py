
import asyncio

from backend.app.memory.hindsight_service import (
    get_client,
    retain_verified_lesson,
)


TEST_ID = 900001

LESSON = (
    "RECALLIX CONTROLLED TEST LESSON. "
    "A suspicious login following repeated failed authentication "
    "attempts should trigger investigation of source IP addresses, "
    "session activity, and sensitive resource access. "
    "This is a synthetic integration test, not a real incident."
)


async def main():
    client = get_client()

    try:
        print("\n--- IDEMPOTENT RETENTION TEST ---")

        print("\n1. First retention")
        first = await retain_verified_lesson(
            content=LESSON,
            incident_id=TEST_ID,
            incident_type="authentication",
        )

        print("Success:", first["success"])
        print("Document ID:", first["document_id"])

        print("\n2. Repeat retention with the same ID")
        second = await retain_verified_lesson(
            content=LESSON,
            incident_id=TEST_ID,
            incident_type="authentication",
        )

        print("Success:", second["success"])
        print("Document ID:", second["document_id"])

        print("\n3. Verify stable document identity")
        print(
            "Same document:",
            first["document_id"] == second["document_id"],
        )

        print("\n--- TEST COMPLETED ---")

    finally:
        await client.aclose()
        print("Hindsight client closed.")


if __name__ == "__main__":
    asyncio.run(main())
