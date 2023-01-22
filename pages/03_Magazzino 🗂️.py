
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
doc_ref = db.collection("vini")

st.markdown('# <span style="color: #983C8E;">Gestione Magazzino</span>', unsafe_allow_html=True)
docs = doc_ref.stream()

# questo è l'array di dizionari che conterrà tutti i prodotti
prodotti = []
for doc in docs:
	if doc.to_dict()['quant'] > doc.to_dict()['soglia']:
		quant = doc.to_dict()['quant']
	# e in base alla quantià residua
	elif doc.to_dict()['quant'] <=0:
		quant = '⛔ ' + 'Esaurito'
	else:
		quant = str(doc.to_dict()['quant']) +' ⚠️ ' + 'In esaurimento'
	# creo il dizionario parziale e lo aggiungo all'array ( di dizionari ) prodotti
	prodotti_dict = {"Nome": doc.to_dict()['nome'], "Annata": doc.to_dict()['annata'], "Prezzo privato" : doc.to_dict()['prezzo_vp'], "Prezzo grossista" : doc.to_dict()['prezzo_vg'], "Prezzo di acquiesto" : doc.to_dict()['prezzo_a'], "Quantità": quant} 
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
	col1, col2 = st.columns(2)


	# --- INIZIO BOTTONI ---
	elimina_selezionati = col1.button('Elimina selezionati')
	if elimina_selezionati:
		if selected == []:
			st.warning('⚠️ Seleziona almeno un vino')
		else:
			for dictionary in selected:
				nome_d = dictionary['Nome'] + dictionary['Annata']
				db.collection(u'vini').document(nome_d).delete()
			st.success(f'Eliminazione avvenuta')
			time.sleep(1)
			st.experimental_rerun()

	elimina_esauriti = col2.button('Elimina esauriti')
	if elimina_esauriti:
		query = db.collection(u'vini').where(u'quant', u'==', 0)
		docs = query.stream()
		for doc in docs:
			db.collection(u'vini').document(doc.id).delete()
		st.success(f'Hai eliminato i prodotti esauriti')
		time.sleep(1)
		st.experimental_rerun()

	# --- FINE BOTTONI --- 

	st.markdown('---')
	# suddivido in due colonne per aggiungere la funzione di aggionra quantità
	new_quant = st.number_input('Inserisci nuova quantità', step=1, min_value=0)
	aggiorna_quant = st.button('Aggiorna quantità')
	
	if aggiorna_quant:
		if selected == []:
			st.warning('⚠️ Seleziona almeno un vino')
		else:
			for dictionary in selected:
				nome_d = dictionary['Nome'] + dictionary['Annata']
				db.collection(u'vini').document(nome_d).update({
					
					'quant': new_quant,
					
				})
				nome_a = doc.to_dict()['nome']

			st.success(f'Hai aggiornato a {new_quant} {nome_a}')
			time.sleep(1)
			st.experimental_rerun()
else:
	# visualizzo questo se non sono presenti prodotti nel magazzino
	st.markdown('### Non sono presenti vini in magazzino')















	