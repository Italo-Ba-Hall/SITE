"""
Test script for playground service
"""
from playground_service import playground_service

# Test URLs
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
    "dQw4w9WgXcQ",  # Direct ID
]

print("Testing URL extraction:")
print("-" * 60)

for url in test_urls:
    video_id = playground_service.extract_video_id(url)
    print(f"URL: {url}")
    print(f"Extracted ID: {video_id}")
    print()

# Test transcription with a real video
print("\nTesting transcription:")
print("-" * 60)
# Using a popular tech video that should have captions
test_video = "https://www.youtube.com/watch?v=Mus_vwhTCq0"  # Python tutorial
print(f"Testing with: {test_video}")

try:
    result = playground_service.get_transcript(test_video)
    print(f"Success!")
    print(f"Video ID: {result['video_id']}")
    print(f"Language: {result['language']}")
    print(f"Duration: {result['duration']} seconds")
    print(f"Transcript length: {len(result['transcript'])} chars")
    print(f"First 200 chars: {result['transcript'][:200]}...")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
