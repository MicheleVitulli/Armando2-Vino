
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

# --- Prelievo dei dati dal database per poi creare la tabella ---
doc_ref = db.collection("prodotti")

st.markdown('# <span style="color: #983C8E;">Gestione Magazzino</span>', unsafe_allow_html=True)
docs = doc_ref.stream()

# questo è l'array di dizionari che conterrà tutti i prodotti
prodotti = []
for doc in docs:
	current_date = datetime.now().strftime("%Y-%m-%d")
	prod_date = datetime.strptime(doc.to_dict()['scadenza'], "%Y-%m-%d")- timedelta(days=doc.to_dict()['delta_scadenza']+1)
	prod_date = prod_date.strftime("%Y-%m-%d")

	# seleziono il giusto segnalino in base alla scadenza
	if current_date >= doc.to_dict()['scadenza']:
		stato = '⛔ ' + 'Scaduto' 
	elif current_date > prod_date:
		stato = '⚠️ '+'In scadenza' 
	else:
		stato = '✅ '+'In stock'

	if doc.to_dict()['quant'] != 0:
		quant = doc.to_dict()['quant']
		scad = doc.to_dict()['scadenza']
	# e in base alla quantià residua
	else:
		quant = '⛔ ' + 'Esaurito'
		scad = ''
		stato = ''

	# creo il dizionario parziale e lo aggiungo all'array ( di dizionari ) prodotti
	prodotti_dict = {"Nome": doc.to_dict()['nome'], "Prezzo €" : doc.to_dict()['prezzo'], "Quantità": quant, "Scadenza": scad, "Stato": stato} 
	prodotti.append(prodotti_dict)


# --- Creazione tabella con AGGrid ---


# se prodotti non è vuoto i.e se ci sta almeno un prodotto nel database
if prodotti != []:
	data = pd.DataFrame(prodotti)
	gd = GridOptionsBuilder.from_dataframe(data)
	gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
	gd.configure_selection(selection_mode='multiple', use_checkbox=True)
	gridOptions = gd.build()


	table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=True)
	# selected contiene le righe selezionate tramite checkbox
	selected = table['selected_rows']

	# divido la pagina in tre colonne per aggiungere i bottoni
	col1, col2, col3 = st.columns(3)


	# --- INIZIO BOTTONI ---
	elimina_selezionati = col1.button('Elimina selezionati')
	if elimina_selezionati:
		if selected == []:
			st.warning('⚠️ Seleziona almeno un prodotto')
		else:
			for dictionary in selected:
				nome_d = dictionary['Nome'] + dictionary['Scadenza']
				db.collection(u'prodotti').document(nome_d).delete()
			st.success(f'Eliminazione avvenuta')
			time.sleep(1)
			st.experimental_rerun()

	elimina_esauriti = col2.button('Elimina esauriti')
	if elimina_esauriti:
		query = db.collection(u'prodotti').where(u'quant', u'==', 0)
		docs = query.stream()
		for doc in docs:
			db.collection(u'prodotti').document(doc.id).delete()
		st.success(f'Hai eliminato i prodotti esauriti')
		time.sleep(1)
		st.experimental_rerun()

	elimina_scaduti = col3.button('Elimina scaduti')
	if elimina_scaduti:
		current_date = datetime.now().strftime("%Y-%m-%d")
		query = db.collection(u'prodotti').where(u'scadenza', u'<=', current_date)
		docs = query.stream()
		for doc in docs:
			db.collection(u'prodotti').document(doc.id).delete()
		st.success(f'Hai eliminato i prodotti scaduti')
		time.sleep(1)
		st.experimental_rerun()
	# --- FINE BOTTONI --- 

	st.markdown('---')
	# suddivido in due colonne per aggiungere la funzione di aggionra quantità
	nc1, nc2 = st.columns([1,4])
	aggiorna_quant = nc1.button('Aggiorna quantità')
	new_quant = nc2.number_input('Inserisci nuova quantità', step=1, min_value=0)
	if aggiorna_quant:
		if selected == []:
			st.warning('⚠️ Seleziona almeno un prodotto')
		else:
			for dictionary in selected:
				nome_d = dictionary['Nome'] + dictionary['Scadenza']
				db.collection(u'prodotti').document(nome_d).set({
					'nome': doc.to_dict()['nome'],
					'quant': new_quant,
					'scadenza': doc.to_dict()['scadenza'],
					'delta_scadenza': doc.to_dict()['delta_scadenza'],
					'prezzo': doc.to_dict()['prezzo'],
				})
				nome_a = doc.to_dict()['nome']

			st.success(f'Hai aggiornato a {new_quant} {nome_a}')
			time.sleep(1)
			st.experimental_rerun()
else:
	# visualizzo questo se non sono presenti prodotti nel magazzino
	st.markdown('### Non sono presenti prodotti in magazzino')















	