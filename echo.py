from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from dotenv import load_dotenv
import os
import aiohttp
import asyncio
from openai import OpenAI
import logging
import requests
from pydub import AudioSegment
from pydub.playback import play
import pygame
import base64

api_key = ""
orderSummary = []
option = "No"
output = ""
messages = []
client = OpenAI(
        api_key=api_key
    )

print("Starting OpenAI...")

file_content = ""
with open('homesysArab.txt', 'r') as file:
# Read the content of the file
    file_content = file.read()

system = {"role": "system","content":[
        {
                "text": file_content,
                "type": "text"
        }
    
        ]}

messages.append(system)

load_dotenv("example.env")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def get_options_input(recipient,title,timeNprice):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                "text": title,
                },
                "footer": {
                "text": timeNprice
                },
                "action": {
                "buttons": [
                    {
                    "type": "reply",
                    "reply": {
                        "id": "1",
                        "title": "\U0001f44d"
                    }
                    }
                ]
                }
            }
        }
    )

def get_location_input(recipient):
    print("sending locaiton")
    location_data = {
        "latitude": "24.784290",
        "longitude": "46.758298"
    }
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "location",
            "location": location_data
        }
          
    )

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
        return response
    else:
        print(response.status_code)
        print(response.text)
        return response

def dealWithAudio(data):
    print("dealing with audio...")
    media_id =data["audio"]['id']
    print(media_id)
    # URL to download the media
    url = f'https://graph.facebook.com/{VERSION}/{media_id}'

    # Set up headers for the request
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # Send a GET request to download the media
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        media_data = response.json()
        if 'url' in media_data:
            # Download the actual audio file
            audio_url = media_data['url']
            audio_response = requests.get(audio_url, headers=headers)
            
            if audio_response.status_code == 200:
                # Save the audio file to disk
                with open('audio.ogg', 'wb') as file:
                    file.write(audio_response.content)
                print('Audio file downloaded successfully.')
            else:
                print('Failed to download audio file:', audio_response.status_code, audio_response.text)
        else:
            print('Media URL not found in the response')
    else:
        print('Failed to get media information:', response.status_code, response.text)


    audio_file= open("audio.ogg", "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file,
    )
    print(transcription.text)
    return transcription.text
    # audio = AudioSegment.from_file('audio.ogg', format='ogg')
    # audio.export('audio.wav', format='wav')
    # print('Audio file converted to WAV format.')

def dealingWithPics(data):
    print("dealing with pics...")
    media_id =data["image"]['id']
    print(media_id)
    # URL to download the media
    url = f'https://graph.facebook.com/{VERSION}/{media_id}'


    # Set up headers for the request
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # Send a GET request to download the media
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        media_data = response.json()
        if 'url' in media_data:
            # Download the actual image file
            image_url = media_data['url']
            image_response = requests.get(image_url, headers=headers)

            if image_response.status_code == 200:
                # Save the image file to disk
                with open('image.jpg', 'wb') as file:
                    file.write(image_response.content)
                with open("image.jpg", "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                print('Image file downloaded successfully.')

                return f"data:image/jpeg;base64,{encoded_string}"
            else:
                print('Failed to download image file:', image_response.status_code, image_response.text)
        else:
            print('Media URL not found in the response')
    else:
        print('Failed to get media information:', response.status_code, response.text)

def sendSummary():
    global option
    print("sending summary...")
    data = get_text_message_input(recipient=RECIPIENT_WAID,text=orderSummary[2])
    response = send_message(data)

def upload_media(file_path):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    
    with open(file_path, "rb") as file:
        files = {
            "file": (os.path.basename(file_path), file, "audio/mpeg")
        }
        data = {
            "messaging_product": "whatsapp",
            "type": "audio/mpeg"
        }
        
        response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception(f"Media upload failed: {response.text}")

def get_audio_message_input(recipient, media_id):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "audio",
            "audio": {"id": media_id}
        }
    )

def sendLocation():
    location_message = get_location_input(recipient=RECIPIENT_WAID)
    send_message(location_message)


def sendVoiceSummary():
    print("making voice..")
    response = client.audio.speech.create(
      model="tts-1",
      voice="echo",
      input=orderSummary[2]
    )
    response.stream_to_file("summary.wav")
    id = upload_media("summary.wav")
    audio_message = get_audio_message_input(recipient=RECIPIENT_WAID,media_id=id)
    send_message(audio_message)


def sendOrder():
    print("sending order...")
    global orderSummary 
    data = get_options_input(recipient=RECIPIENT_WAID,title=orderSummary[0],timeNprice=orderSummary[1])
    response = send_message(data)

def dealWithOptions(data):
    global messages
    global option
    global output 
    print("dealing with options...")
    if data["interactive"]["title"] == "\U0001f44d":
        option = "Yes"
        output = ""
        messages = []
        sendVoiceSummary()
        sendLocation()
        sendSummary()
        return "ORDER ACCEPTED"
    else:
        option = "No"
        messages = []
        return "ORDER DENIED"

def getOrderSummary():
    global orderSummary
    conversation = ""
    with open('conversation.txt', 'r') as file:
    # Read the content of the file
        conversation = file.read()
    messages = []
    #get summary from openai
    file_content = ""
    language = "Urdu"
    with open('sumInstr.txt', 'r') as file:
    # Read the content of the file
        file_content = file.read()
    system = {"role": "system","content":[
        {
                "text": file_content,
                "type": "text"
        }
    
        ]}
    user = {"role": "system","content":[
        {
                "text": conversation+"\n Language: "+language,
                "type": "text"
        }
    
        ]}
    messages.append(system)
    messages.append(user)
    response = client.chat.completions.create(
                model = "gpt-4o",
                messages = messages,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )
    info = response.choices[0].message.content
    print(info)
    # info = "Title: ائٹس ٹھیک کرنے کا موقع\nTime and Price:  کل دوپہر 136 ریال\nSummary: کلائنٹ اپنے لائٹ بلب ٹھیک کرنا چاہتے ہیں اور سمجھتے ہیں کہ چابی خراب ہے۔ انہیں کل دوپہر مدد درکار ہے اور کام کی کل قیمت 136 ریال ہے"
    title = info.split("Title: ")[1].split("\n")[0]
    timeNprice = info.split("Time and Money: ")[1].split("\n")[0]
    detail = info.split("Summary: ")[1]
    orderSummary = [title,timeNprice,detail]
    open("conversation.txt", 'w').close() 

def saveConvo(conversation):
    with open("conversation.txt", 'a') as file:
        file.write(conversation + "\n")
    
    #

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    global messages
    conversation = ""
    global orderSummary
    global option
    global output
    if request.method == 'POST':
        data = request.json
        logger.info(f"Received message from Glitch: {data}")
        
        message = data.get('message', 'No message content')
        sender = data.get('from', 'Unknown sender')
        location = data.get('location')
        print(data)
        reply = "No reply"
        if 'message' in data:
            logger.info(f"Message: {message}")
            logger.info(f"From: {sender}")
            reply = message
        elif 'location' in data:
            latitude = location['latitude']
            longitude = location['longitude']
            logger.info(f"Latitude: {latitude}")
            logger.info(f"Longitude: {longitude}")
            reply = "Latitude "+str(latitude)+", "+"Longitude "+str(longitude)
            
        elif 'audio' in data:
            reply = dealWithAudio(data)
        elif 'image' in data:
            print("imaging...")
            reply = dealingWithPics(data)
        elif 'interactive' in data:
            reply = dealWithOptions(data)
        else:
            reply = "Thank you!"
            logger.info("No valid message content")

        #openAI here
    
        if "data:image/jpeg;base64" in reply:
            imageQ = {
                        "role": "user",
                        "content": [
                        {"type": "text", "text": "االصوره التاليه تعبر عن الخدمه التي احتاجها"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": reply,
                                            },
                            },
                                ],
                    }
            messages.append(imageQ) 
        elif "Latitude" in reply:
            print("here")
            systemDynamic = {"role": "system","content":[
                 {
                "text": "تم تحديد الموقع. الفريق يحتاج ربع ساعه للوصل الي البيت",
                # "text": "لم يتم تحديد الموقع.",
                "type": "text"
                }
    
                ]}
            messages.append(systemDynamic)
        else:
            user = {"role": "user","content":[
                    {
                        "text": reply,
                        "type": "text"
                    }
                
                    ]}
            messages.append(user)
            conversation = conversation+"\nUser:"+reply

        # output= "ملخص طلبك:"
        if "تم تسجيل طلبك" in output:
            output = "ORDER_DONE"
            if  option == "No":
                getOrderSummary()
                sendOrder()

        if output != "ORDER_DONE":
            print("calling openAI...")  
            response = client.chat.completions.create(
                model = "gpt-4o",
                messages = messages,
                temperature=0.5,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )
            output = response.choices[0].message.content
            data = get_text_message_input(
            recipient=RECIPIENT_WAID, text=output
            )

            response = send_message(data)

        conversation = conversation+"\nAssistant:"+output
        saveConvo(conversation)

        # print(output)
        
        return jsonify({"status": "success"}), 200
    else:
        return "Flask webhook endpoint is working", 200
    

@app.route('/', methods=['GET'])
def home():
    return "Flask app is running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)