import requests
import json
import time
import logging
from enum import Enum
from typing import Optional, List, Dict

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


class NotifyLevel(Enum):
    SUCCESS = 'green'
    INFO = 'wathet'
    WARNING = 'yellow'
    DANGER = 'red'


class FeiShuTalkChatBot:
    def __init__(self, webhook, secret=None, pc_slide=False, fail_notice=False):
        '''
        机器人初始化
        Reference doc: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

        :param webhook: 飞书群自定义机器人webhook地址
        :param secret: 机器人安全设置页面勾选“加签”时需要传入的密钥
        :param pc_slide: 消息链接打开方式，默认False为浏览器打开，设置为True时为PC端侧边栏打开
        :param fail_notice: 消息发送失败提醒，默认为False不提醒，开发者可以根据返回的消息发送结果自行判断和处理
        '''
        super(FeiShuTalkChatBot, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.webhook = webhook
        self.secret = secret
        self.pc_slide = pc_slide
        self.fail_notice = fail_notice

    def success(self, message, title: str = 'Successfully', ats: Optional[List] = None, action=None):
        self.send_text(title=title, message=message, level=NotifyLevel.SUCCESS.value, ats=ats, action=action)

    def info(self, message, title: str = 'Notification', ats: Optional[List] = None, action=None):
        self.send_text(title=title, message=message, level=NotifyLevel.INFO.value, ats=ats, action=action)

    def warning(self, message, title: str = 'Warning', ats: Optional[List] = None, action=None):
        self.send_text(title=title, message=message, level=NotifyLevel.WARNING.value, ats=ats, action=action)

    def error(self, message, title: str = 'Error', ats: Optional[List] = None, action=None):
        self.send_text(title=title, message=message, level=NotifyLevel.DANGER.value, ats=ats, action=action)

    def send_text(self, title, message, level, ats: Optional[List] = None, action: Optional[Dict] = None):
        """
        :param title:
        :param message:
        :param level:
        :param ats:
        :param action: { "direction": "DOWN", actions: {} }
        :return:
        """
        data = {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": message
                        }
                    }
                ],
                "header": {
                    "title": {
                        "content": title,
                        "tag": "plain_text"
                    },
                    "template": level
                }
            }
        }

        # Put @ people
        if ats:
            if len(ats) == 1 and ats[0] == "all":
                data["card"]["elements"].append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "At <at id=all></at>",
                    }
                })
            elif len(ats) > 0:
                at_list_template = []
                for at in ats:
                    at_list_template.append({
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "At <at id=" + at + "></at>",
                        }
                    })
                data["card"]["elements"].extend(at_list_template)
            else:
                raise Exception("Invalid ats.")

        if action:
            if action["direction"] == "UP":
                direction = "UP"
            else:
                direction = "DOWN"

            if direction == "DOWN":
                data["card"]["elements"].append({"tag": "hr"})
                data["card"]["elements"].append(action["actions"])
            if direction == "UP":
                data["card"]["elements"].insert(0, action["actions"])

        return self.post(data)

    def post(self, data):
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: 返回消息发送结果
        """
        try:
            post_data = json.dumps(data)
            response = requests.post(self.webhook, headers=self.headers, data=post_data, verify=False)

        except requests.exceptions.HTTPError as exc:
            logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            logging.error("消息发送失败，HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            logging.error("消息发送失败，Timeout error!")
            raise
        except requests.exceptions.RequestException:
            logging.error("消息发送失败, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '服务器响应异常'}
            else:
                logging.debug('发送结果：%s' % result)
                # 消息发送失败提醒（errcode 不为 0，表示消息发送异常），默认不提醒，开发者可以根据返回的消息发送结果自行判断和处理
                if self.fail_notice and result.get('errcode', True):
                    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    error_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "[注意-自动通知]飞书机器人消息发送失败，时间：%s，原因：%s，请及时跟进，谢谢!" % (
                                time_now, result['errmsg'] if result.get('errmsg', False) else '未知异常')
                        },
                        "at": {
                            "isAtAll": False
                        }
                    }
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


if __name__ == '__main__':
    pass
