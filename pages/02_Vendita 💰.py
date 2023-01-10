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
		if doc.to_dict()['nome'] not in prodotti:
			# crea un array di nomi prelevandoli dal database evitando duplicati
			prodotti.append(doc.to_dict()['nome'])
st.markdown('# <span style="color: #983C8E;">Vendi i vini</span>', unsafe_allow_html=True)
option = st.selectbox('Seleziona il vino', prodotti)
if option:
	option_ac = st.selectbox('Vendi a privato o grossista', ['Privato', 'Grossista'])


# --- Selezione del prodotto ---
if option and option != '':
	query = db.collection(u'vini').where(u'nome', u'==', option)
	docs = query.stream()
	# double e double_prodotti servono per verificare la presenza di nomi doppi
	double_prodotti = []
	double = 0
	for doc in docs:
		# questa è la forma dell'array che contiene i campi del prodotto
		arr = [doc.id, doc.to_dict()['annata'], doc.to_dict()['quant'], doc.to_dict()['prezzo_vp'], doc.to_dict()['prezzo_a'], doc.to_dict()['prezzo_vg']]
		double_prodotti.append(arr)
		double += 1 

	# ann_prodotti è una lista delle annate di prodotti con lo stesso nome
	# target_arr è l'array che contiene i campi del prodotto che cerco
	ann_prodotti = []
	target_arr = []
	# se double >= 2 allora ho due o più prodotti con lo stesso nome
	if double >= 2:
		for arr in double_prodotti:
			ann_prodotti.append(arr[1])
		# option_double mi permette di selezionare tramite data di scadenze
		option_double = st.selectbox('Seleziona la data di scadenza del prodotto', ann_prodotti)

		# in questo ciclo seleziono l'array di riferimento in base alla data di scadenza presa in option_double
		for arr in double_prodotti:
			if option_double in arr:
				target_arr = arr
				break

	# in questo caso double < 2, e quindi non ho elementi doppi
	else:
		target_arr = double_prodotti[0]

	if option_ac == 'Grossista':
		vendita = doc.to_dict()['prezzo_vg']
	else:
		vendita = doc.to_dict()['prezzo_vp']
	
	st.markdown(f'> Sono presenti <span style="color: #37519F;">{target_arr[2]}</span>  <span style="color: #983C8E;">{option}</span> del <span style="color: #37519F;">{target_arr[1]}</span> ', unsafe_allow_html=True)
	st.markdown(f'> Il prezzo consigliato di vendita è {vendita} euro')
	vendita= st.number_input('Vendi a questo prezzo', min_value=0.0, value=vendita)


	# seleziono quantità da vendere
	quant_vendita = st.number_input('Quantità da vendere', step=1, min_value=0, max_value=target_arr[2])
	st.write(f'Il ricavo è di {float(quant_vendita) * float(vendita)} euro')

	vendi = st.button('Vendi')


	# --- Vendita del prodotto ---
	if vendi and quant_vendita!=0 and quant_vendita<=target_arr[2]:
		
		# aggiorno il prodotto con la nuova quantità attuale 
		db.collection(u'vini').document(target_arr[0]).update({

		'quant': target_arr[2] - quant_vendita,
		})
		# aggiungo vendita e ricavo alla sezione vendite del database

		db.collection(u'vendite').document().set({

		'annata': target_arr[1],
		'nome': doc.to_dict()['nome'],
		'quant': quant_vendita,
		'data': datetime.now().strftime("%Y-%m-%d"),
		'ricavo' : float(quant_vendita) * float(vendita),
		'guadagno': (float(quant_vendita) * float(vendita)) - (float(quant_vendita) * float(doc.to_dict()['prezzo_a'])),
		'reso' : '',
		'acquirente': option_ac
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
	


