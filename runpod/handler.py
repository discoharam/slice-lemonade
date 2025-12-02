import runpod
print("✅ Handler loaded")
runpod.serverless.start({"handler": lambda job: {"status": "ready"}})
