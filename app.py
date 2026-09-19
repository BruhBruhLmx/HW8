import streamlit as st
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)    
else:
    client = None

@st.cache_data
def load_data():
    with open('config.json', 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    menu_df = pd.read_csv('menu.csv')
    return config, menu_df
def ask_bot(prompt):
    if client is None: return 'API key hasn\'t been applied'
    try:
        user_content = 'Restaurant Menu:\n' + str(menu_df) + '\nQuestions:\n' + prompt

        sys_inst = config.get("system_instruction", f"Bạn là PhoBot của {config['restaurant_name']}. {config['out_of_scope_message']}")
        response = client.models.generate_content(
            model = 'gemini-3.6-flash',
            contents = user_content,
            config = types.GenerateContentConfig(system_instruction=sys_inst)
        )
        return response.text
    except Exception as e:
        return f'{e}'


config, menu_df = load_data()


st.title(f'PhoBot - {config['restaurant_name']}')

cau_chao = config['initial_bot_message']

if 'lich_su_chat' not in st.session_state:
    st.session_state.lich_su_chat = [{'role':'assistant', 'content': cau_chao}]

for tin_nhan in  st.session_state.lich_su_chat:
    with st.chat_message(tin_nhan['role']):
        st.write(tin_nhan['content'])

prompt = st.chat_input('Ask a question...')

if prompt:
    st.session_state.lich_su_chat.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.write(prompt)

    with st.spinner('PhoBot is thinking...'):
        bot_reply = ask_bot(prompt)

    st.session_state.lich_su_chat.append({'role': 'assistant', 'content': bot_reply})
    with st.chat_message('assistant'):
            st.write(bot_reply)