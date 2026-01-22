def handler(event):
    """
    Minimal RunPod Serverless handler.
    """
    return {
        "status": "ok",
        "message": "Parallax worker is alive 🚀",
        "input": event.get("input", {})
    }
