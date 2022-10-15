class credentials:
    API_ID = 0
    API_HASH = ""
    BOT_TOKEN = ""

class telegram:
    GROUP_ID = 0
    MESSAGE_STRUCTURE = "<b>{}</b>\nby <i>{}</i> on <a href={}>{}</a>"
    LOG_STRUCTURE = "{} | https://redd.it/{} | {} | {}"
    
class reddit:
    COMPRESSED = False
    SUBREDDIT_LIST = [
                        "", ""
                    ]
    FILTERS = {
                "isSponsored": False,
                "isStickied": False
            }
    PARAMETERS = {
                "allow_over18": 1
                }