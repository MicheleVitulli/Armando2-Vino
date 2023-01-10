
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
doc_ref = db.collection("vendite")

st.markdown('# <span style="color: #983C8E;">Storico vendite</span>', unsafe_allow_html=True)
st.markdown('> Seleziona una riga per effettuare un reso')
docs = doc_ref.stream()

# questo è l'array di dizionari che conterrà tutti i prodotti
prodotti = []
for doc in docs:

	# creo il dizionario parziale e lo aggiungo all'array ( di dizionari ) prodotti
	prodotti_dict = {"Data Vendita" : doc.to_dict()['data'],"Nome": doc.to_dict()['nome'],"Annata" : doc.to_dict()['annata'], "Quantità" : doc.to_dict()['quant'],  "Ricavo" : doc.to_dict()['ricavo'],"Acquirente": doc.to_dict()['acquirente'], 'Reso': doc.to_dict()['reso']} 
	prodotti.append(prodotti_dict)


# --- Creazione tabella con AGGrid ---


# se prodotti non è vuoto i.e se ci sta almeno un prodotto nel database
if prodotti != []:
	data = pd.DataFrame(prodotti)
	gd = GridOptionsBuilder.from_dataframe(data)
	gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
	gd.configure_selection(selection_mode='single', use_checkbox=True)
	gridOptions = gd.build()


	table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=False)
	# selected contiene le righe selezionate tramite checkbox
	selected = table['selected_rows']

	if selected != []:
		for d in selected:
			max_quant = d['Quantità']
		aggiorna_quant = st.button('Effettua reso')
		new_quant = st.number_input('Bottiglie restituite', step=1, min_value=0, max_value=max_quant)
		if aggiorna_quant:
			for dictionary in selected:
				nome_d = dictionary['Nome'] + dictionary['Annata']
				
				doc_ref = db.collection("vini").document(nome_d)
				doc = doc_ref.get()
				db.collection(u'vini').document(nome_d).update({
					'quant': doc.to_dict()['quant'] + new_quant,
				})
				query = db.collection(u'vendite').where(u'nome', u'==', dictionary['Nome']).where(u'annata', u'==', dictionary['Annata']).where(u'data', u'==', dictionary['Data Vendita'])
				docs = query.stream()
				for doc in docs:
					db.collection('vendite').document(doc.id).update({
					'reso': str(new_quant) + ' resi il ' + datetime.now().strftime("%Y-%m-%d"),
					#'ricavo': doc.to_dict()['ricavo'] - (new_quant * doc.to_dict()['ricavo']/doc.to_dict()['quant']),
					#'quant': doc.to_dict()['quant'] - new_quant
					})
					break

				doc_ref = db.collection("resi").document()
				doc_ref.set({
						'annata': dictionary['Annata'],
						'nome' : dictionary['Nome'],
						'quant': new_quant,
						'data' : datetime.now().strftime("%Y-%m-%d")
					})
				st.success(f'Reso effettuato')
				time.sleep(1)
				st.experimental_rerun()
else:
	st.write("Nessuna vendita registrata")


# --- Resi ---
st.markdown('# <span style="color: #983C8E;">Storico resi</span>', unsafe_allow_html=True)
doc_ref = db.collection("resi")
docs = doc_ref.stream()
resi = []
for doc in docs:

	# creo il dizionario parziale e lo aggiungo all'array ( di dizionari ) prodotti
	prodotti_dict = {"Data Reso" : doc.to_dict()['data'],"Nome": doc.to_dict()['nome'],  "Annata": doc.to_dict()['annata'], "Quantità": doc.to_dict()['quant']} 
	resi.append(prodotti_dict)


if resi != []:
	data2 = pd.DataFrame(resi)
	gd2 = GridOptionsBuilder.from_dataframe(data2)
	gd2.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
	gridOptions2 = gd2.build()


	table2 = AgGrid(data2, gridOptions=gridOptions2, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=False)
else:
	st.write("Nessun reso registrato")










