import runpod
import time

def handler(job):
    """
    Minimaler Dummy-Handler zum Verifizieren,
    dass RunPod Jobs korrekt annimmt & ausführt.
    """
    print("Job received:", job)

    # Simuliere kurze Arbeit
    time.sleep(2)

    return {
        "status": "ok",
        "echo": job.get("input", {})
    }

runpod.serverless.start({
    "handler": handler
})
