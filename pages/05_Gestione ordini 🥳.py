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

st.markdown('# <span style="color: #983C8E;">Gestione Ordini per ricevimenti</span>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(['Gestione degli ordini', 'Gestione dei resi'])

with tab1:
  #Creo la collection relativa agli ordini per feste e ricevimenti
  docs = db.collection(u'vini').stream()
  prodotti = ['']
  for doc in docs:
    if doc.to_dict()['quant'] != 0:
      if doc.to_dict()['nome'] not in prodotti:
        prodotti.append(doc.to_dict()['nome'])


  ord_nome = st.text_input('Nome dell\'ordine')
  ord_data = st.date_input('Data ricevimento ordine')
  ord_id = ord_nome + str(ord_data)
  vino_id = st.multiselect('Che vino prendi?', prodotti)

  vino_q = {}
  for k in range(len(vino_id)):
    vino_quan = st.number_input('Quante bottiglie di {}'.format(vino_id[k]), key=str(vino_id[k]), step=1, min_value=0)
    vino_q[vino_id[k]] = vino_quan 


  if st.button('Invia ordine per ricevimento'):
      db.collection('ordini').document(ord_id).set({
      'nome ordine': ord_nome,
      'data evento': str(ord_data),
      'ordinato': vino_q
      })

      st.success('Ordine per ricevimento registrato')
      time.sleep(1)

with tab2:
  doc_ref = db.collection('ordini')
  docs = doc_ref.get()

  ordini = []
  for doc in docs:
    # st.write(doc.to_dict())
    ordini_dict = {'Nome ordine': doc.to_dict()['nome ordine'], 'Vini ordinati': doc.to_dict()['ordinato']}
    ordini.append(ordini_dict)

  if ordini != []:
    data = pd.DataFrame(ordini)
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gridOptions = gd.build()


    table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=True)
