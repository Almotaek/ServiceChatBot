# ServiceChatBot
Whatsapp bot for home services where you can chat, send voice notes to order from suppliers without looking for them. These Suppliers can be connected through whatsapp or an independent app and orders will be received in their original language through voice and chat. 

# Goal 
An MVP that has the core functionalities and can be used as a proof of concept to build a more robust system, if needed.
Product Components

# Components

1. WhatsApp API
2. OpenAI
3. Backend (Server, logic...)
4. Integration

# Customer Journey

1. Customer sends text, voice, or image to WhatsApp
2. Agent asks for clarifying questions or none
3. Required information taken from the user: location, time and service specific information 
4. Service options shown to customer with expected time, price, and rating
5. Customer confirms order with and pays through WhatsApp, ApplePay on a link, or cash?
6. Service providers receive order notification and summary
7. Customer receives tracking information, notified when service arrived, and agent answers any update questions
8. After service, customer gives service providers a confirmation PIN, or Scan
9. Customers are asked to rate their experience in terms of time, quality, and cost
10. Repeat 🙂

# How to run it locally

1. Open the MVP File via visual code
2. Open Meta, Glitch, OpenAI, and Ngrok
3. Regenerate access tokens (meta, openai) and update in the env file and glitch
4. Generate a new ngrok link and add it to the glitch code
5. run the ngrok tunnel by ngrok http --domain= newurl 80
6. run echo.py

![alt text](https://github.com/Almotaek/ServiceChatBot/blob/main/InfoFlow.png)
