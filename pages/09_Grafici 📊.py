
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import pandas as pd

# --- firebase ---
if not firebase_admin._apps:
	cred = credentials.Certificate('firestore-key.json')
	firebase_admin.initialize_app(cred)
db = firestore.client()


# --- layout ---
st.set_page_config(page_title='Armando 2.0', layout = 'wide', page_icon = '📦', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown('📦 Armando 2.0')


# input per selezionare mese e anno
current_month = datetime.now().strftime("%m")
current_year =  datetime.now().strftime("%Y")

mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
mese_drop = st.selectbox('Seleziona mese di riferimento', mesi)
sel_mese = mesi.index(mese_drop) + 1
sel_anno = st.number_input('Seleziona anno di riferimento', step=1, min_value=2000, max_value=int(current_year), value=int(current_year))
doc_ref = db.collection("vendite")
docs = doc_ref.stream()


# --- GRAFICO DELLE VENDITE ---
st.markdown('# <span style="color: #983C8E;">Grafico delle vendite</span>', unsafe_allow_html=True)

# preparo un dizionario che contiene due liste: prodotti e quantità
new_data = {'prodotti': [], 'quantità': []}
for doc in docs:
	nome = doc.to_dict()['nome']
	quant = doc.to_dict()['quant']
	data = doc.to_dict()['data']
	mese = data.split('-')[1]
	anno = data.split('-')[0]


	
	if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
		
		if not nome in new_data['prodotti']:
			# aggiungo elementi a new_data se non sono già presenti
			new_data['prodotti'].append(nome)
			new_data['quantità'].append(quant)
		else:
			# altrimenti aggiorno la quantità
			pos = 0
			for i in range(len(new_data['prodotti'])):
				if nome == new_data['prodotti'][i]:
					pos = i
			temp = new_data['quantità'][pos]
			new_quant = temp + quant
			new_data['quantità'][pos] = new_quant
	

# creo il chart con pandas e poi lo disegno con st.bar_chart
chart_newdata = pd.DataFrame(new_data)
st.bar_chart(chart_newdata, x='prodotti', y='quantità')


# --- GRAFICO DEI RICAVI ---
# grafico molto simile al precedente

st.markdown('# <span style="color: #983C8E;">Grafico dei ricavi</span>', unsafe_allow_html=True)

doc_ref2 = db.collection("vendite")
docs2 = doc_ref.stream()

# creo il dizonario, che chiamo new_data2 per evitare collisioni con il precedente
# anche molti prossime variabili avranno la dicitura "2"
new_data2 = {'prodotti': [], 'ricavi': []}
for doc in docs2:
	nome = doc.to_dict()['nome']
	ricavo = doc.to_dict()['ricavo']
	data = doc.to_dict()['data']
	mese = data.split('-')[1]
	anno = data.split('-')[0]

	
	if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
		if not nome in new_data2['prodotti']:
			# aggiungo prodotto e ricavo
			new_data2['prodotti'].append(nome)
			new_data2['ricavi'].append(ricavo)
		else:
			# altrimenti aggiorno il volume dei ricavi
			pos = 0
			for i in range(len(new_data2['prodotti'])):
				if nome == new_data2['prodotti'][i]:
					pos = i
			temp = new_data2['ricavi'][pos]
			new_ricavo = temp + ricavo
			new_data2['ricavi'][pos] = new_ricavo

# creo il chart con pandas e poi lo disegno con st.bar_chart
chart_newdata2 = pd.DataFrame(new_data2)
st.bar_chart(chart_newdata2, x='prodotti', y='ricavi')









