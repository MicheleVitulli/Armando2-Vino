import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date

if not firebase_admin._apps:
	cred = credentials.Certificate('firestore-key.json')
	firebase_admin.initialize_app(cred)
db = firestore.client()


st.set_page_config(page_title='Armando 2.0', layout = 'wide', page_icon = '📦', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown('## 🍷🍷🍷')
st.markdown('# Versione per Le Bon Ton')
st.markdown('## 🍷🍷🍷')

def foo():
    st.write('ciao')
    return

b = st.button('premi')
if b:
    foo()


st.markdown('> 🦈 ⚪️')

# Tenere lontano dalla portata di bambini ed economisti.
