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

#     # --- INIZIO BOTTONI ---
#     elimina_selezionati = col1.button('Elimina selezionati')
#     if elimina_selezionati:
#       if selected == []:
#         st.warning('⚠️ Seleziona almeno un ordine')
#       else:
#         for dictionary in selected:
#           db.collection(u'vini').document(dictionary.id).delete()
#         st.success(f'Eliminazione avvenuta')
#         time.sleep(1)
#         # st.experimental_rerun()

#     q_reso = col2.number_input('Aggiorna reso bottiglie', min_value=0)
#     aggiorna_reso = col2.button('Aggiorna il reso in magazzino')

########################################################################################################################################à
  docs = db.collection(u'vini').stream()
  prodotti = ['']
  for doc in docs:
    if doc.to_dict()['quant'] != 0:
      if doc.to_dict()['nome'] not in prodotti:
        prodotti.append(doc.to_dict()['nome'])

  #informazioni evento
  ord_nome = st.text_input('Inserisci nome evento')
  ord_data = st.date_input('Inserisci data evento', value=datetime.now())

  #codice identificativo per ogni singolo evento
  ord_id = ord_nome + str(ord_data)

  #informazioni relative ai vini che si vogliono prendere per l'evento
  option = st.multiselect('Seleziona i vini', prodotti)


  # --- Selezione del prodotto ---
  dict_vino = {}
  if option and option != '':
    for vino in option:
      query = db.collection(u'vini').where(u'nome', u'==', vino)
      docs = query.stream()
      double_prodotti = []
      double = 0
      for doc in docs:
        arr = [doc.id, doc.to_dict()['annata'], doc.to_dict()['quant'], doc.to_dict()['prezzo_vp'], doc.to_dict()['prezzo_a'], doc.to_dict()['prezzo_vg']]
        double_prodotti.append(arr)
        double += 1 

      ann_prodotti = []
      target_arr = []
    
      if double >= 2:
        for arr in double_prodotti:
          ann_prodotti.append(arr[1])
      
        option_double = st.selectbox('Seleziona l\'annata', ann_prodotti)

      
        for arr in double_prodotti:
          if option_double in arr:
            target_arr = arr
            break

      else:
        target_arr = double_prodotti[0]

      q_vino = st.number_input('Quante bottiglie di {}'.format(vino), key=str(vino), step=1, min_value=0)

      dict_vino[vino]=[target_arr[1], target_arr[2], q_vino]
    

  ordine = st.button('Registra ordine per ricevimento')

  if ordine and option!=[]:
    db.collection(u'ordini').document(ord_id).set({
      'nome ordine': ord_nome,
      'data evento': str(ord_data),
      'ordinato': dict_vino
      })
    
    for i in dict_vino:
      q_iniziale = dict_vino[i][1]
      q_evento = dict_vino[i][2]
      vino_id = i+dict_vino[i][0]

      db.collection(u'vini').document(vino_id).update({'quant': q_iniziale - q_evento})

    st.success('Ordine registrato con successo')
    time.sleep(1)

with tab2:
  doc_ref = db.collection('ordini')
  docs = doc_ref.get()

  ordini = []
  for doc in docs:
    ordinato = doc.to_dict()['ordinato']
    for i in ordinato:
      ordini_dict = {'Nome ordine': doc.to_dict()['nome ordine'], 'Vini ordinati': i, 'Quantità': ordinato[i][2]}
      ordini.append(ordini_dict)

  if ordini != []:
    data = pd.DataFrame(ordini)
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gridOptions = gd.build()


    table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=True)

    selected = table['selected_rows']

    col1, col2 = st.columns(2)

    elimina_selezionati = col1.button('Elimina selezionati')
    if elimina_selezionati:
      if selected == []:
        st.warning('⚠️ Seleziona almeno un ordine')
      else:
        for dictionary in selected:
          db.collection(u'ordini').document(dictionary.id).delete()
        st.success(f'Eliminazione avvenuta')
        time.sleep(1)


    # for dictionary in selected:
    #   q_reso = col2.number_input('Quantotà da rendere del vino selezionato', min_value=0, step=1)
    # effettua_reso = col2.button('Effettua reso vini selezionati')
    # if effettua_reso:
    #   db.collection(u'vini').document(vino_id).update({'quant': q_iniziale - q_evento})

    #   db.collection(u'resi').document()