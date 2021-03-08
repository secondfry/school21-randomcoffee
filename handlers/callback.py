from telegram import Update
from telegram.ext import CallbackContext


def handler_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    print(query)

    query.edit_message_text(text=f"Selected option: {query.data}")
