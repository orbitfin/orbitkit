from orbitkit.lark_send import FeiShuTalkChatBot

WEBHOOK_FILING = ""
feishu_talk_chat_bot = FeiShuTalkChatBot(webhook=WEBHOOK_FILING)


def sendMessage(task, send_str):
    data = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "elements": [{
                "tag": "div",
                "text": {
                    "content": send_str,
                    "tag": "lark_md"
                }
            }, {
                "actions": [{
                    "tag": "button",
                    "text": {
                        "content": "更多任务地址查看",
                        "tag": "lark_md"
                    },
                    "url": "http://101.34.92.142:7000/meta/notice",
                    "type": "default",
                    "value": {}
                }],
                "tag": "action"
            }],
        }
    }
    feishu_talk_chat_bot.post(data=data)


if __name__ == '__main__':
    sendMessage("Pdf task定时任务执行完成", 'test')
