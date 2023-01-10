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
docs = db.collection(u'prodotti').stream()
prodotti = ['']
for doc in docs:
	if doc.to_dict()['quant'] != 0:
		if doc.to_dict()['nome'] not in prodotti:
			# crea un array di nomi prelevandoli dal database evitando duplicati
			prodotti.append(doc.to_dict()['nome'])
st.markdown('# <span style="color: #983C8E;">Vendi i prodotti</span>', unsafe_allow_html=True)
option = st.selectbox('Seleziona il prodotto', prodotti)

# --- Selezione del prodotto ---
if option and option != '':
	query = db.collection(u'prodotti').where(u'nome', u'==', option)
	docs = query.stream()
	# double e double_prodotti servono per verificare la presenza di nomi doppi
	double_prodotti = []
	double = 0
	for doc in docs:
		# questa è la forma dell'array che contiene i campi del prodotto
		arr = [doc.id, doc.to_dict()['scadenza'], doc.to_dict()['quant'], doc.to_dict()['prezzo'],doc.to_dict()['delta_scadenza']]
		double_prodotti.append(arr)
		double += 1 

	# scad_prodotti è una lista delle scadenze di prodotti con lo stesso nome
	# target_arr è l'array che contiene i campi del prodotto che cerco
	scad_prodotti = []
	target_arr = []
	# se double >= 2 allora ho due o più prodotti con lo stesso nome
	if double >= 2:
		for arr in double_prodotti:
			scad_prodotti.append(arr[1])
		# option_double mi permette di selezionare tramite data di scadenze
		option_double = st.selectbox('Seleziona la data di scadenza del prodotto', scad_prodotti)

		# in questo ciclo seleziono l'array di riferimento in base alla data di scadenza presa in option_double
		for arr in double_prodotti:
			if option_double in arr:
				target_arr = arr
				break

	# in questo caso double < 2, e quindi non ho elementi doppi
	else:
		target_arr = double_prodotti[0]


	if target_arr[2] == 1:
		st.write(f'È presente {target_arr[2]} {option} che scade il {target_arr[1]}')
	else:
		st.markdown(f'> Sono presenti <span style="color: #37519F;">{target_arr[2]}</span>  <span style="color: #983C8E;">{option}</span> che scadono il <span style="color: #37519F;">{target_arr[1]}</span> ', unsafe_allow_html=True)


	# seleziono quantità da vendere
	quant_vendita = st.number_input('Quantità da vendere', step=1, min_value=0)
	st.write(f'Il ricavo è di {float(quant_vendita) * float(target_arr[3])} euro')
	vendi = st.button('Vendi')


	# --- Vendita del prodotto ---
	if vendi and quant_vendita!=0 and quant_vendita<=target_arr[2]:
		
		# aggiorno il prodotto con la nuova quantità attuale 
		db.collection(u'prodotti').document(target_arr[0]).set({

		'nome': option,
		'quant': target_arr[2] - quant_vendita,
		'scadenza': target_arr[1],
		'delta_scadenza': target_arr[4],
		'prezzo': target_arr[3]

		})
		# aggiungo vendita e ricavo alla sezione vendite del database

		db.collection(u'vendite').document().set({

		'nome': doc.to_dict()['nome'],
		'quant': quant_vendita,
		'data': datetime.now().strftime("%Y-%m-%d"),
		'ricavo' : float(quant_vendita) * float(doc.to_dict()['prezzo'])
		})
		
		nome = doc.to_dict()['nome']
		# time.sleep(1) serve a bloccare l'applicazione un secondo prima di runnarla nuovamente
		# per permettere di visualizzare il messaggio di successo
		st.success(f'Hai venduto con successo {quant_vendita} {nome}')
		time.sleep(1)
		st.experimental_rerun()

	elif vendi:
		# errore se la quantià non è valida
		st.warning('Inserisci una quantità valida', icon="⚠️")
	


