from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser
from datetime import datetime

import requests
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage,
    StickerSendMessage, TemplateSendMessage, PostbackEvent, PostbackAction, ButtonsTemplate,
    CarouselTemplate, CarouselColumn, LocationMessage, URITemplateAction, FlexSendMessage,ConfirmTemplate,
)

from Record import Record
from User import User
from database.DatabaseManager import DatabaseManager
from database.ImageUtil import ImageUtil

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
# channel_secret = '11ea65827bee73807f09630d71bfc0d5'
# channel_access_token = 'bsqUPTQgthfNaPT5KV+2GE2ZgnptBAJd+1a3/aFjGPRL00qaBOSDnxaJQ7XxMphHiXe0Z1NHHGCk5NzJi+mdHhjUTOnTGuaVzpP/T0PCtOqi3VMV08455B5Ze/rxXmgNRxs+kUwITwd5xhQsFYyWzgdB04t89/1O/w1cDnyilFU='

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
# AMAP_API_KEY
AMAP_API_KEY = 'b5b581b926e1a908f35f09094bcf413c'

record = ''


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if isinstance(event, PostbackEvent):
            handle_PostbackEvent(event)
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
            continue
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)
        if isinstance(event.message, LocationMessage):
            handle_LocationMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'


def handle_PostbackEvent(event):
    if event.postback.data == "terms":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='''Personal Information Collection Statement

The Insurance Company respects your privacy and is committed to protecting it through the adoption of this personal information collection statement (“Personal Information Collection Statement”). It guides and governs how we collect, store, transfer, process and use the Personal Data (as defined hereinafter) collected about you. Please read this carefully to understand our policies and practices as set out in this Personal Information Collection Statement regarding your Personal Data and how we will treat it (the “Policy”). If you do not agree with our Policy, do not enter your Personal Data or register to receive communication from us. This Policy may, in our sole discretion, be updated, modified, and changed from time to time. Your continued use of the Website after we make such updates, modifications, and changes is deemed to be acceptance of such, so please check the Policy periodically for updates.

In this document, “we”, “our”, or “us” refers to The Insurance Company.'''))

    elif event.postback.data == "agree":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Please enter the insurance ID'))

    elif event.postback.data == "serious":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='We are now connecting to manual mode...'))

    elif event.postback.data == "slight":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Please send your location to us. And we will recommand 3 nearest car service point to you.'))
    
    elif event.postback.data == "check":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='We will mail to your reserved address in 7 days'))
    
    elif event.postback.data == "e-check":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='We will send you electronic check documents in 7 days'))
    
    elif event.postback.data == "bank transfer":
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Please enter your bank accout'))
    
    else:
        print(1)




# Handler function for Text Message
def handle_TextMessage(event):
    if event.message.text.startswith('#'):
        flag = DatabaseManager().verify_insurance(event.source.user_id, event.message.text)
        if flag:
            #line_bot_api.push_message(event.source.user_id,TextSendMessage(text='Please choose the type of Insurance Claims.'))
            message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='Please choose the type of Insurance Claims.',
                    actions=[
                        PostbackAction(
                            label='Slight',
                            display_text='Slight',
                            data='slight'
                        ),
                        PostbackAction(
                            label='Serious',
                            display_text='Serious',
                            data='serious'
                        )

                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)

            global record
            record.insurance_id = event.message.text
        else:
            line_bot_api.push_message(event.source.user_id,
                                      TextSendMessage(text="Sorry, this insurance ID doesn't exist"))
    elif event.message.text == 'status':
        temp = DatabaseManager().find_record(event.source.user_id)
        receipt = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": temp.image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "http://linecorp.com/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "INSURANCE CLAIMS RECORD",
                        "wrap": True,
                        "weight": "bold",
                        "gravity": "center",
                        "size": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                            },
                            {
                                "type": "text",
                                "text": "4.0",
                                "size": "sm",
                                "color": "#999999",
                                "margin": "md",
                                "flex": 0
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ID",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": temp.insurance_id,
                                        "wrap": True,
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 4
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Place",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": temp.location,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 4
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Time",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": str(temp.create_time),
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 4
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "contents": [
                            {
                                "type": "spacer"
                            },
                            {
                                "type": "image",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/linecorp_code_withborder.png",
                                "aspectMode": "cover",
                                "size": "xl"
                            },
                            {
                                "type": "text",
                                "text": "You can check the insurance claims by using this code",
                                "color": "#aaaaaa",
                                "wrap": True,
                                "margin": "xxl",
                                "size": "xs"
                            }
                        ]
                    }
                ]
            }
        }
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents=receipt
        )
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )
    
    elif event.message.text == 'compensation':
        msg = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url=profile.picture_url,
                title='Compensation',
                text='Please choose compensation way.',
                actions=[
                    PostbackAction(
                        label='check',
                        display_text='Mail a check',
                        data='check'
                    ),
                    PostbackAction(
                        label='e-check',
                        display_text='E-check',
                        data='e-check'
                    ),
                    PostbackAction(
                        label='bank transfer',
                        display_text='Bank Transfer',
                        data='bank transfer'
                    )
                ]
            )
        )
        line_bot_api.reply_message( event.reply_token, msg)

    else:
        profile = line_bot_api.get_profile(event.source.user_id)
        greeting = 'Hi, '
        greeting = greeting + profile.display_name
        line_bot_api.push_message(event.source.user_id,
                                  TextSendMessage(text=greeting))
        line_bot_api.push_message(event.source.user_id,
                                  TextSendMessage(text='Welcome to Insurance Claims Chatbot!'))
        user_record = DatabaseManager().find_user(event.source.user_id)
        if not user_record:
            user = User()
            user.id = event.source.user_id
            user.avatar = profile.picture_url
            user.name = profile.display_name
            DatabaseManager().save_user(user)
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = Record()
        record.user_id = event.source.user_id
        record.create_time = create_time


# Handler function for Location Message
def handle_LocationMessage(event):
    record.location = event.message.address
    location = f'{event.message.longitude},{event.message.latitude}'

    addurl2 = 'https://restapi.amap.com/v3/place/around?key={}&location={}&radius=10000&types=030000&extensions=base&offset=3'.format(
        AMAP_API_KEY, location)
    addressReq = requests.get(addurl2)
    addressDoc = addressReq.json()
    sugName0 = addressDoc['pois'][0]['name']
    sugAddress0 = addressDoc['pois'][0]['address']

    sugName1 = addressDoc['pois'][1]['name']
    sugAddress1 = addressDoc['pois'][1]['address']

    sugName2 = addressDoc['pois'][2]['name']
    sugAddress2 = addressDoc['pois'][2]['address']

    sugtel0 = addressDoc['pois'][0]['tel']
    sugtel1 = addressDoc['pois'][0]['tel']
    sugtel2 = addressDoc['pois'][0]['tel']

    Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(

                    thumbnail_image_url='https://img.51miz.com/preview/element/00/01/08/29/E-1082937-04831968.jpg',
                    title=f'{sugName0}',
                    text='Address: ' + sugAddress0,
                    actions=[
                        URITemplateAction(
                            label=f'Call',
                            uri=f'tel:{sugtel0}'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.51miz.com/preview/element/00/01/08/29/E-1082937-04831968.jpg',
                    title=f'{sugName1}',
                    text='Address: ' + sugAddress1,
                    actions=[
                        URITemplateAction(
                            label=f'Call',
                            uri=f'tel:{sugtel1}'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.51miz.com/preview/element/00/01/08/29/E-1082937-04831968.jpg',
                    title=f'{sugName2}',
                    text='Address: ' + sugAddress2,
                    actions=[
                        URITemplateAction(
                            label=f'Call',
                            uri=f'tel:{sugtel2}'
                        )
                    ]
                )

            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, Carousel_template)


# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Handler function for Image Message
def handle_ImageMessage(event):
    image = line_bot_api.get_message_content(event.message.id)
    image_url = ImageUtil().upload(image.content)
    record.image = image_url
    line_bot_api.push_message(event.source.user_id,
                              TextSendMessage(text='Success！Insurance Claim is reviewing...'))
    line_bot_api.push_message(event.source.user_id,
                              TextSendMessage(text="You can send 'status' to check the status."))
    DatabaseManager().save_record(record)


# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Nice video!")
    )


# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Nice file!")
    )


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
