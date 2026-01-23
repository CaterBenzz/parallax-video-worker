import runpod

def handler(event):
    print("[PARALLAX] Job received:", event)
    return {
        "status": "ok",
        "echo": event.get("input")
    }

if __name__ == "__main__":
    print("[PARALLAX] Starting serverless worker...")
    runpod.serverless.start({"handler": handler})
