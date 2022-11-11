badWordList = "Nigger,Nigga,Faggot,Retard,Tranny,Kike,Kys,Kill Yourself".lower().split(
    ","
)


def checkBadWord(message) -> str:
    message = message.lower()
    if "http" in message or "https" in message:
        return "URLs Are Not Allowed"
    for bword in badWordList:
        if bword in message:
            return "Message Contains Bad Words"
    return None
