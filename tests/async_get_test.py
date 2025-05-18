import asyncio
import httpx
import time

# Target endpoint
API_URL = "http://127.0.0.1:8000/api/questions/get-questions"

# Total number of concurrent requests
NUM_REQUESTS = 5

async def send_get(i):
    async with httpx.AsyncClient() as client:
        try:
            print(f"[{i}] Sending GET request")
            response = await client.get(API_URL, timeout=10.0)
            questions = response.json().get("questions", [])
            print(f"[{i}] Status: {response.status_code} | Questions Returned: {len(questions)}")
        except Exception as e:
            print(f"[{i}] Error: {str(e)}")

async def main():
    start = time.time()
    tasks = [send_get(i+1) for i in range(NUM_REQUESTS)]
    await asyncio.gather(*tasks)
    print(f"\nAll GET requests completed in {time.time() - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
