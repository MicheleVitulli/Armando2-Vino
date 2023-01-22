import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date
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

# --- Creazione barra di ricerca per i prodotti ---
docs = db.collection(u'vini').stream()
prodotti = ['']
for doc in docs:
	if doc.to_dict()['quant'] != 0:
		# crea un array di nomi prelevandoli dal database evitando duplicati
		prodotti.append(doc.id)
st.markdown('# <span style="color: #983C8E;">Vendi i vini</span>', unsafe_allow_html=True)
option = st.selectbox('Seleziona il vino', prodotti)
if option:
	option_ac = st.selectbox('Vendi a privato o grossista', ['Privato', 'Grossista'])


# --- Selezione del prodotto ---
if option and option != '':
	info = option.split(' ')
	print(info)
	query = db.collection(u'vini').where(u'nome', u'==', info[0]).where('annata', '==', info[1])
	docs = query.stream()
	for doc in docs:
		nome = doc.to_dict()['nome']
		annata = doc.to_dict()['annata']
		prezzo_vg = doc.to_dict()['prezzo_vg']
		prezzo_a = doc.to_dict()['prezzo_a']
		prezzo_vp = doc.to_dict()['prezzo_vp']
		quant = doc.to_dict()['quant']
	
	
	print(nome, annata)
	if option_ac == 'Grossista':
		vendita = prezzo_vg
	else:
		vendita = prezzo_vp
	
	st.markdown(f'> Sono presenti <span style="color: #37519F;">{quant}</span>  <span style="color: #983C8E;">{option}</span>', unsafe_allow_html=True)
	st.markdown(f'> Il prezzo consigliato di vendita è {vendita} euro')
	vendita= st.number_input('Vendi a questo prezzo', min_value=0.0, value=vendita)


	# seleziono quantità da vendere
	quant_vendita = st.number_input('Quantità da vendere', step=1, min_value=0, max_value=quant)
	st.write(f'Il ricavo è di {float(quant_vendita) * float(vendita)} euro')

	vendi = st.button('Vendi')


	# --- Vendita del prodotto ---
	if vendi and quant_vendita!=0 and quant_vendita<=target_arr[2]:
		
		# aggiorno il prodotto con la nuova quantità attuale 
		db.collection(u'vini').document(target_arr[0]).update({

		'quant': quant - quant_vendita,
		})
		# aggiungo vendita e ricavo alla sezione vendite del database

		db.collection(u'vendite').document().set({

		'annata': annata,
		'nome': nome,
		'quant': quant_vendita,
		'data': datetime.now().strftime("%Y-%m-%d"),
		'ricavo' : float(quant_vendita) * float(vendita),
		'guadagno': (float(quant_vendita) * float(vendita)) - (float(quant_vendita) * float(doc.to_dict()['prezzo_a'])),
		'reso' : '',
		'acquirente': option_ac
		})
		
		# time.sleep(1) serve a bloccare l'applicazione un secondo prima di runnarla nuovamente
		# per permettere di visualizzare il messaggio di successo
		st.success(f'Hai venduto con successo {quant_vendita} {nome}')
		time.sleep(1)
		st.experimental_rerun()

	elif vendi:
		# errore se la quantià non è valida
		st.warning('Inserisci una quantità valida', icon="⚠️")
	


