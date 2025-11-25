async def create_chat(db, chat):
    doc = {
        "user_id": chat.user_id,
        "message": chat.message,
    }
    result = await db.chat_logs.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "user_id": chat.user_id,
        "message": chat.message,
    }


async def get_user_chats(db, user_id: str, limit: int = 50):
    cursor = db.chat_logs.find(
        {"user_id": user_id},
        limit=limit,
        sort=[("_id", -1)],
    )

    results = []
    async for doc in cursor:
        results.append({
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "message": doc["message"],
        })

    return results