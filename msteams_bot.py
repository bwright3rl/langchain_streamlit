!pip install botbuilder-core

from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext

app = Flask(__name__)
adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings("<Microsoft-App-ID>", "<Microsoft-App-Password>"))

async def bot_logic(turn_context: TurnContext):
    await turn_context.send_activity(f"You said: {turn_context.activity.text}")

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        request_body = request.json
    else:
        return Response(status=415)

    async def call_bot_framework_adapter():
        await adapter.process_activity(request_body, "", bot_logic)

    loop.run_until_complete(call_bot_framework_adapter())
    return ""

if __name__ == "__main__":
    app.run(port=3978, debug=True)
