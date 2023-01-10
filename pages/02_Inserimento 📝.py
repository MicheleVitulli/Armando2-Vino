
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import pandas as pd
import time

# --- Importazione firebase, necessario if per evitare errore streamlit ---
if not firebase_admin._apps:
	cred = credentials.Certificate('firestore-key.json')
	firebase_admin.initialize_app(cred)
db = firestore.client()


# --- Layout comune a tutte le pagine
st.set_page_config(page_title='Armando 2.0', layout = 'wide', page_icon = '📦', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown('📦 Armando 2.0')
st.markdown('# <span style="color: #983C8E;">Inserisci i prodotto/i nel magazzino</span>', unsafe_allow_html=True)

# --- Inserimento campi del prodotto ---
prod_nome = st.text_input('Nome')
prod_quant = st.number_input('Quantità', step=1, min_value=1, value=1)
prod_prezzo = st.number_input('Prezzo unità (euro)', min_value=0.00)
prod_scad = st.date_input("Data di scadenza")
prod_avvertimento = st.number_input('Avvertimi x giorni prima della scadenza', step=1, value=5, min_value=0)

# l'id (chiave univoca) viene creato concatenando il nome e la data di scadenza
prod_id = prod_nome + str(prod_scad)

doc_ref = db.collection("prodotti").document(prod_id)
doc = doc_ref.get()

# controllo se il prodotto (con id) ha già una quantità residua di partenza
try:
	old_prod_quant = doc.to_dict()['quant']
except:
	old_prod_quant = 0

# --- Aggiunta prodotto al database ---
if st.button('Aggiungi'):
	current_date = datetime.now().strftime("%Y-%m-%d")
	if prod_nome == '':
		st.warning('⚠️ Inserisci un nome valido')
	elif current_date > str(prod_scad):
		st.warning('⚠️ Inserisci una data di scadenza valida')
	elif str(datetime.strptime(current_date , "%Y-%m-%d")+ timedelta(days=prod_avvertimento-1)) > str(prod_scad):
		st.warning('⚠️ La coppia avvertimento e data di scadenza non è valida')
	else:
		doc_ref.set({
		'nome': prod_nome,
		'quant': old_prod_quant + prod_quant,
		'scadenza': str(prod_scad),
		'delta_scadenza': prod_avvertimento,
		'prezzo' : prod_prezzo

	})
		# time.sleep(1) serve a bloccare l'applicazione un secondo prima di runnarla nuovamente
		# per permettere di visualizzare il messaggio di successo
		st.success(f'Aggiunte/i {prod_quant} {prod_nome} al magazzino')
		time.sleep(1)
		st.experimental_rerun()








