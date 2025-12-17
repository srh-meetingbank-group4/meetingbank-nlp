from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["meetingbank"]
meetings_col = db["meetings"]

# VERIFIED city mapping (documented source: MeetingBank paper)
city_map = {
    1: "Seattle",
    2: "Boston",
    3: "Denver",
    4: "Denver",
    5: "Denver",
    6: "Denver",
    7: "Long Beach",
    8: "Long Beach",
    9: "Long Beach",
    10: "King County",
    11: "Alameda"
}

updated = 0

for meeting_id, city in city_map.items():
    result = meetings_col.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"city": city}}
    )
    if result.modified_count > 0:
        updated += 1

print(f"Updated city for {updated} meetings.")