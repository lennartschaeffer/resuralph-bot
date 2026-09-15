from enum import Enum


class CommandType(str, Enum):
    UPDATE = "update"
    CLEAR_RESUMES = "clear_resumes"
    GET_ALL_RESUMES = "get_all_resumes"
    UPLOAD = "upload"
    GET_LATEST_RESUME = "get_latest_resume"
    AI_REVIEW = "ai_review"


ASYNC_COMMANDS = {
    CommandType.UPDATE,
    CommandType.CLEAR_RESUMES,
    CommandType.GET_ALL_RESUMES,
    CommandType.UPLOAD,
    CommandType.GET_LATEST_RESUME,
    CommandType.AI_REVIEW,
}


def run_async_command(command_type: CommandType, interaction_data):
    if command_type == CommandType.UPDATE:
        from apps.bot.src.commands.update import handle_update_command
        return handle_update_command(interaction_data)
    elif command_type == CommandType.CLEAR_RESUMES:
        from apps.bot.src.commands.clear_resumes import handle_clear_resumes_command
        return handle_clear_resumes_command(interaction_data)
    elif command_type == CommandType.GET_ALL_RESUMES:
        from apps.bot.src.commands.get_all_resumes import handle_get_all_resumes_command
        return handle_get_all_resumes_command(interaction_data)
    elif command_type == CommandType.UPLOAD:
        from apps.bot.src.commands.upload import handle_upload_command
        return handle_upload_command(interaction_data)
    elif command_type == CommandType.GET_LATEST_RESUME:
        from apps.bot.src.commands.get_latest_resume import handle_get_latest_resume_command
        return handle_get_latest_resume_command(interaction_data)
    elif command_type == CommandType.AI_REVIEW:
        from apps.bot.src.commands.ai_review import handle_ai_review_command
        return handle_ai_review_command(interaction_data)
    else:
        raise ValueError(f"Unknown command type: {command_type}")
