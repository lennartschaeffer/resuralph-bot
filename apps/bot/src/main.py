import os
import logging
from flask import Flask, jsonify, request
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
from discord_interactions import verify_key_decorator
from dotenv import load_dotenv
from apps.bot.src.helpers.sqs_publisher import publish_command_to_queue, create_deferred_response
from apps.bot.src.helpers.embed_helper import create_error_embed
from apps.bot.src.helpers.local_async_processor import handle_async_command_local
from apps.bot.src.helpers.environment import is_local_environment
from apps.bot.src.command_dispatch import CommandType, ASYNC_COMMANDS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

DISCORD_PUBLIC_KEY = os.getenv("DEV_DISCORD_PUBLIC_KEY") if is_local_environment() else os.getenv("DISCORD_PUBLIC_KEY")

if is_local_environment():
    logger.info("running in dev mode!")

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app, lifespan="off")

@app.route("/", methods=["POST"])
async def interactions():
    raw_request = request.json
    return interact(raw_request)


@verify_key_decorator(DISCORD_PUBLIC_KEY)
def interact(raw_request):
    try:
        if raw_request["type"] == 1:
            logger.info("Discord health check received")
            return jsonify({"type": 1})
        
        data = raw_request["data"]
        command_name = data["name"]
        user_id = raw_request.get('member', {}).get('user', {}).get('id', 'unknown')
        logger.info(f"Processing command '{command_name}' for user {user_id}")
        
        response_content = handle_command_routing(command_name, raw_request)
        response_data = format_command_response(command_name, response_content)
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error processing Discord interaction: {str(e)}")
        error_embed = create_error_embed(
            "Processing Error",
            "An error occurred while processing your request. 😔"
        )
        return jsonify({
            "type": 4,
            "data": error_embed,
        })

def handle_command_routing(command_name, raw_request):

    try:
        command_type = CommandType(command_name)
    except ValueError:
        logger.warning(f"Unimplemented command: {command_name}")
        return create_error_embed(
            "Command Not Found",
            f"Command '{command_name}' is not implemented yet."
        )

    if is_local_environment():
        # Local development: Use background thread for async processing
        return handle_async_command_local(raw_request, command_type)
    else:
        # Production environment: Use SQS for async processing
        success = publish_command_to_queue(raw_request, command_name)
        if success:
            logger.info(f"Command '{command_name}' queued for async processing")
            return create_deferred_response()
        else:
            logger.error(f"Failed to queue command '{command_name}'")
            return create_error_embed(
                "Processing Error",
                "Failed to queue your request for processing. Please try again."
            )

def format_command_response(command_name, response_content):
    # Async commands return deferred responses that are already formatted
    if command_name in ASYNC_COMMANDS:
        return response_content # deferred response already handled in async processing

    if isinstance(response_content, dict) and "embeds" in response_content:
        return {"type": 4, "data": response_content}
    else:
        return {"type": 4, "data": {"content": response_content}}

if __name__ == "__main__":
    app.run(debug=True, port=8000)