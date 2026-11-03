import urllib.request
import json

# 1. Login to get token
login_data = json.dumps({"identifier": "sivatmika0206@gmail.com", "password": "password123"}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        token = res["token"]
        print("[AUTH] Successfully logged in! Token acquired.")
except Exception as e:
    print("[AUTH] Login error:", e)
    exit(1)

auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. Get initial AI Chat conversations and messages count
req = urllib.request.Request("http://127.0.0.1:8000/api/chat/conversations", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    convs = json.loads(resp.read().decode())["conversations"]
    active_conv_id = convs[0]["id"]
    print(f"[CHAT] Active conversation ID: {active_conv_id}")

req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    init_messages = json.loads(resp.read().decode())["messages"]
    init_count = len(init_messages)
    print(f"[CHAT] Initial message count in AI Chat: {init_count}")

# TEST 1: Dashboard Robot Speak "How are you?"
print("\n--- TEST 1: Speaking to Dashboard Robot ('How are you?') ---")
companion_data = json.dumps({"message": "How are you?"}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8000/api/companion/chat", data=companion_data, headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    robot_res = json.loads(resp.read().decode())
    print(f"Robot replied: {robot_res['reply'][:60]}...")

req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    msgs = json.loads(resp.read().decode())["messages"]
    print(f"AI Chat message count after Robot Test 1: {len(msgs)} (Initial was {init_count})")
    assert len(msgs) == init_count, "ERROR: Robot message leaked into AI Chat!"
    print("✓ PASS: Robot speech did NOT appear in AI Chat!")

# TEST 2: Dashboard Robot Speak "I am feeling stressed today."
print("\n--- TEST 2: Speaking to Dashboard Robot ('I am feeling stressed today.') ---")
companion_data = json.dumps({"message": "I am feeling stressed today."}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8000/api/companion/chat", data=companion_data, headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    robot_res = json.loads(resp.read().decode())
    print(f"Robot replied: {robot_res['reply'][:60]}...")

req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    msgs = json.loads(resp.read().decode())["messages"]
    print(f"AI Chat message count after Robot Test 2: {len(msgs)}")
    assert len(msgs) == init_count, "ERROR: Robot message leaked into AI Chat!"
    print("✓ PASS: Robot speech did NOT appear in AI Chat!")

# TEST 3: Regular AI Chat Message "Tell me something about stress."
print("\n--- TEST 3: Sending regular AI Chat message ('Tell me something about stress.') ---")
chat_data = json.dumps({"message": "Tell me something about stress."}).encode('utf-8')
req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", data=chat_data, headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    chat_res = json.loads(resp.read().decode())
    print(f"AI Chat replied: {chat_res['reply'][:60]}...")

req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    msgs = json.loads(resp.read().decode())["messages"]
    print(f"AI Chat message count after Chat Test 3: {len(msgs)} (Increased by 2: user + assistant)")
    assert len(msgs) == init_count + 2, "ERROR: AI Chat message was not recorded in AI Chat!"
    print("✓ PASS: AI Chat works normally and records its own conversation!")

# TEST 4: Dashboard Robot Speak "Can you help me relax?"
print("\n--- TEST 4: Speaking to Dashboard Robot ('Can you help me relax?') ---")
companion_data = json.dumps({"message": "Can you help me relax?"}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8000/api/companion/chat", data=companion_data, headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    robot_res = json.loads(resp.read().decode())
    print(f"Robot replied: {robot_res['reply'][:60]}...")

req = urllib.request.Request(f"http://127.0.0.1:8000/api/chat/conversations/{active_conv_id}/messages", headers=auth_headers)
with urllib.request.urlopen(req) as resp:
    msgs = json.loads(resp.read().decode())["messages"]
    print(f"AI Chat message count after Robot Test 4: {len(msgs)} (Expected: {init_count + 2})")
    assert len(msgs) == init_count + 2, "ERROR: Robot message leaked into AI Chat!"
    print("✓ PASS: Dashboard Robot is completely isolated from AI Chat!")

print("\n🎉 ALL 4 TESTS PASSED PERFECTLY WITH COMPLETE ISOLATION!")
