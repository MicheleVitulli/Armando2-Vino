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
st.markdown('# 📦 Armando 2.0')

st.markdown(''' **Armando 2.0 è l\'innovativa web app** per la gestione del magazzino della tua impresa\n, sviluppata dal team IT di **[JESAP Consulting](https://www.jesap.it/)**,
 Junior Enterprise de **La Sapienza Università di Roma**.

  Se cerchi un assistente che ti aiuti a mettere ordine nella gestione delle scorte,\n ti offra una panoramica completa della merce a magazzino e utili statistiche sui prodotti venduti,\n **Armando 2.0** fa al caso tuo!
Il tutto in maniera semplice e intuitiva, con un layout organizzato e pulito e una grafica accattivante. 





 ##### Team IT 🦈  ''')

# Tenere lontano dalla portata di bambini ed economisti.
