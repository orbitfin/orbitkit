from orbitkit.lark_send import FeiShuTalkChatBot

webhook = ""
feishu_talk_chat_bot = FeiShuTalkChatBot(webhook=webhook)
feishu_talk_chat_bot.error(message='I am a test!', ats=[], action={
    "direction": "DOWN",
    "actions": {
        "actions": [{
            "tag": "button",
            "text": {
                "content": "More attractions introduction: Rose:",
                "tag": "lark_md"
            },
            "url": "https://www.example.com",
            "type": "default",
            "value": {}
        }],
        "tag": "action"
    }
})
