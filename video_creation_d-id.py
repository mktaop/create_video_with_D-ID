#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 14:05:52 2023

@author: avi_patel
"""

import streamlit as st
from streamlit_option_menu import option_menu
import requests, json
from dotenv import load_dotenv
import openai, os
from openai import OpenAI


def generate_video(username, password, input_text, source_url):
    url = "https://api.d-id.com/talks"

    payload = {
        "script": {
            "type": "text",
            "subtitles": "false",
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            },
            "ssml": "false",
            "input": f"{input_text}"
        },
        "config": {
            "fluent": "false",
            "pad_audio": "0.0",
            "driver_expressions": {
                "expressions": [
                    {
                        "start_frame": 0,
                        "expression": "happy",
                        "intensity": 0.75
                    }
                ]
            }
        },
        "source_url": f"{source_url}"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": 'Basic ' + username + ':' + password
    }

    response = requests.post(url, json=payload, headers=headers)


    
    talk_id = json.loads(response.text)['id']

    talk_url = f"{url}/{talk_id}"

    headers = {
        "accept": "application/json",
        "authorization": 'Basic ' + username + ':' + password
    }

    response = requests.get(talk_url, headers=headers)
    video_response = json.loads(response.text)

    while video_response["status"] != "done":
        response = requests.get(talk_url, headers=headers)
        video_response = json.loads(response.text)

    video_url = video_response["result_url"]
    return video_url


def get_response(client, model, temperature, token_limit, streaming, message):
        try:
            response = client.chat.completions.create(model=model,
                                                    messages=message,
                                                    temperature=temperature,
                                                    max_tokens=token_limit,
                                                    stream=streaming)

            output = response.choices[0].message.content
            tokens = response.usage.total_tokens
            yield output, tokens

        except Exception as e:
            print(e)
            yield ""


def main():
    split_key = DID_API_KEY.split(':')
    username = split_key[0]
    password = split_key[1]
    
    text1 = """1. Provide a photo or an image that we will use to animate in the video\n2. Provide a script for the video\n3. Generate a video using the image and script you provide
        """

    st.write("# Create a video in 3 Steps:")
    st.text(f"{text1}")
    
    opt1 = st.radio("How would you like to provide your image?",["Enter Image URL", "Upload Image"])
    if opt1=="Enter Image URL":
        img = st.text_input("Enter URL", "")
        if img:
            st.write("Image URL is retrieved!")
    else:
        img1 = st.file_uploader(label='Upload your picture', type='png')
        if img1:
            
            f_name=img1.name
            url = "https://api.d-id.com/images"

            files = { "image": (f"{f_name}", open(f"{f_name}", "rb"), "image/png") }
            headers = {
                "accept": "application/json",
                "authorization": 'Basic ' + username + ':' + password
            }

            response = requests.post(url, files=files, headers=headers)
            img=(json.loads(response.text)['url'])
            if img:
                st.write("Image URL is retrieved!")
    
    opt2 = st.radio("How would you like to provide your script?", ["Manually enter it", "Use ChatGPT to generate it"])
    if opt2 == "Manually enter it":
        script = st.text_input("Enter or paste your script here:", "")
    else:
        client = OpenAI(api_key=OPEN_AI_API_KEY)
        model='gpt-3.5-turbo-1106'
        temperature=0.2
        token_limit = 75
        streaming=False
        message = st.input_text("Enter your prompt to generate your script:", "")
        for result in get_response(client, model, temperature, token_limit, streaming, message):
            script = result[0]
    if script:
        st.write("We have a Script!")
    
    if st.button("Click to generate video"):
        if img.strip() and script.strip() is not None:
            split_key = DID_API_KEY.split(':')
            username = split_key[0]
            password = split_key[1]
            video_url = generate_video(username, password, script, img)
            st.video(video_url)
        
                

if __name__ == "__main__":
    OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
    DID_API_KEY = "----"
    main()
    
    