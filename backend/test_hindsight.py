
# from backend.app.memory.hindsight_service import (
#     get_client,
#     hindsight_status,
#     recall_incident_context,
#     retain_verified_lesson,
#     reflect_on_incident,
# )

# print("\n--- RECALLIX HINDSIGHT TEST ---")

# print("\n1. Configuration")
# print(hindsight_status())

# print("\n2. Connection and memory bank access")
# client = get_client()
# print("Hindsight client initialized.")

# print("\n3. Store a test investigation lesson")
# stored = retain_verified_lesson(
#     content=(
#         "TEST MEMORY: Repeated failed login attempts followed by "
#         "a successful login from an unfamiliar IP should trigger "
#         "account compromise investigation. Verify session activity "
#         "and review sensitive resource access."
#     ),
#     incident_id=99999,
#     incident_type="authentication",
# )
# print("Retain result:", stored["success"])

# print("\n4. Recall the stored lesson")
# memories = recall_incident_context(
#     "What should an analyst investigate after repeated failed "
#     "logins followed by a successful login from an unfamiliar IP?"
# )
# for memory in memories:
#     print("-", memory["text"])

# print("\n5. Reflect over investigation memory")
# reflection = reflect_on_incident(
#     "What investigation steps are relevant to repeated failed "
#     "logins followed by a successful unfamiliar login?"
# )
# print(reflection["text"])
# print("\nSources:", reflection["based_on"])

# print("\n--- TEST FINISHED ---")



import asyncio

from backend.app.memory.hindsight_service import (
    get_client,
    hindsight_status,
    recall_incident_context,
    reflect_on_incident,
)


async def main():
    client = get_client()

    try:
        print("\n--- RECALLIX HINDSIGHT TEST ---")

        print("\n1. Configuration")
        print(hindsight_status())

        print("\n2. Client initialized")
        print("Hindsight client ready.")

        print("\n3. Historical memory recall")

        memories = await recall_incident_context(
            "What investigation steps are recommended "
            "for phishing and suspicious login activity?"
        )

        print("Memories returned:", len(memories))

        for index, memory in enumerate(memories, start=1):
            print(f"\nMemory {index}:")
            print("Type:", memory.get("type"))
            print("Text:", memory.get("text"))

        print("\n4. Hindsight reflection")

        try:
            reflection = await reflect_on_incident(
                "What are the most important investigation "
                "steps for phishing and suspicious login incidents?"
            )

            print("\nReflection:")
            print(reflection["text"])

            print("\nSources:", reflection["based_on"])

        except Exception as error:
            print("\nReflection temporarily unavailable.")
            print("Reason:", error)

        print("\n--- TEST COMPLETED ---")

    finally:
        await client.aclose()
        print("\nHindsight client closed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
