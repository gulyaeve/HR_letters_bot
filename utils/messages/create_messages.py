import json

from loader import messages


async def create_messages():
    with open("templates/messages_template.json", "r", encoding="utf-8") as file:
        new_messages = json.loads(file.read())
    for message_type in new_messages:
        new_message_type = await messages.create_message_type(message_type)
        for description in new_messages[message_type]:
            await messages.create_message(description,
                                          new_message_type['id'],
                                          new_messages[message_type][description])
