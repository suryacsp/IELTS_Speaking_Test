import asyncio
import httpx
import time

# Your local API endpoint
API_URL = "http://127.0.0.1:8000/api/questions/generate-question"

# 10 topics to test
topics = [
    "Technology and Innovation",
    "Urbanization",
    "Globalization",
    "Family and Relationships",
    "Media and Advertising",
    "Climate Change",
    "Work-Life Balance",
    "Consumerism",
    "History and Heritage",
    "Art and Creativity"
]


async def send_post(topic, i):
    async with httpx.AsyncClient() as client:
        payload = {"topic": topic}
        try:
            print(f"[{i}] Sending request for topic: {topic}")
            response = await client.post(API_URL, json=payload, timeout=15.0)
            print(f"[{i}] Status: {response.status_code} | Question: {response.json().get('question')}")
        except Exception as e:
            print(f"[{i}] Error with topic '{topic}': {str(e)}")

async def main():
    start = time.time()
    tasks = [send_post(topic, i+1) for i, topic in enumerate(topics)]
    await asyncio.gather(*tasks)
    end = time.time()
    print(f"\nAll requests completed in {end - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
