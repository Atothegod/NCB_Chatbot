import chainlit as cl


def get_memory():

    memory = cl.user_session.get("memory")

    if memory is None:

        memory = {
            "kyc_id": None,
            "track_id": None,
            "delivery_method": None,
            "delivery_destination": None
        }

        cl.user_session.set("memory", memory)

    return memory


def reset_request():

    memory = get_memory()

    memory["track_id"] = None
    memory["delivery_method"] = None
    memory["delivery_destination"] = None