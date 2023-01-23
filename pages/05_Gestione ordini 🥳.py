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

  docs_vini = db.collection(u'vini').stream()
  prodotti = ['']
  for doc in docs_vini:
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

        # st.markdown(f'Sono presenti diversi annata in magazzinno per <span style="color: #983C8E;">{vino}</span>')
        option_double = st.selectbox(f'Seleziona l\'annata', ann_prodotti)

      
        for arr in double_prodotti:
          if option_double in arr:
            target_arr = arr
            break

      else:
        target_arr = double_prodotti[0]

      q_vino = st.number_input('Quante bottiglie di {}'.format(vino), key=str(vino), step=1, min_value=0)

      dict_vino[target_arr[0]]=[target_arr[2], q_vino]

  ordine = st.button('Registra ordine per ricevimento')

  if ordine and option!=[]:
    db.collection(u'ordini').document(ord_id).set({
      'nome ordine': ord_nome,
      'data evento': str(ord_data),
      'ordinato': dict_vino
      })
    
    for i in dict_vino:
      q_iniziale = dict_vino[i][0]
      q_evento = dict_vino[i][1]

      db.collection(u'vini').document(i).update({'quant': q_iniziale - q_evento})

      if q_evento > q_iniziale:
        st.warning('⚠️ La quantità non è disponibile in magazzino. La scorta attuale è pari a:', q_iniziale)

    st.success('Ordine registrato con successo')
    # time.sleep(1)

with tab2:
  docs_ordini = db.collection('ordini').stream()

  ordini = []
  for doc in docs_ordini:
    ordinato = doc.to_dict()['ordinato']
    vini_ord = ''

    for i in ordinato:
      vini_ord += i + ' : ' + str(ordinato[i][1]) + '; \n' #bisognerebbe decidere se mettere anche l'annata ma si fa subito

    ordini.append({'Nome ordine': doc.to_dict()['nome ordine'], 'Data evento':doc.to_dict()['data evento'], 'Vini ordinati': vini_ord}) 
    # ordini.append(ordini_dict)

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
          ord_id = selected[0]['Nome ordine'] + selected[0]['Data evento']
          db.collection(u'ordini').document(ord_id).delete()
        st.success(f'Eliminazione avvenuta')
        time.sleep(1)

    

    if len(selected) == 1:
      reso_id = selected[0]['Nome ordine'] + selected[0]['Data evento']

      for doc in docs_ordini:
        if reso_id == doc.id:
          ordine = doc.to_dict()['ordinato']
          prodotti = ordine.keys()

      vino_reso = col2.selectbox('Scegli il prodotto da rendere', prodotti)

      if vino_reso:
        q_reso = col2.number_input('Quantità di reso', min_value=0, step=1)

      aggiorna_reso = col2.button('Registra reso')
      if aggiorna_reso:

        query = db.collection(u'vini').where(u'nome', u'==', vino_reso)
        docs = query.stream()

        double_prodotti = []
        double = 0

        for doc in docs:
          arr = [doc.id, doc.to_dict()['annata'], doc.to_dict()['quant']]
          double_prodotti.append(arr)
          double += 1 

        ann_prodotti = []
        target_arr = []
    
        if double >= 2:
          for arr in double_prodotti:
            ann_prodotti.append(arr[1])

        # st.markdown(f'Sono presenti diversi annata in magazzinno per <span style="color: #983C8E;">{vino}</span>')
          option_double = st.selectbox(f'Seleziona l\'annata', ann_prodotti)

      
          for arr in double_prodotti:
            if option_double in arr:
              target_arr = arr
              break

        else:
          target_arr = double_prodotti[0]


        vino_id = vino_reso + '-' + str(target_arr[1])
        for doc in docs_vini:
          if vino_reso == doc.id:
            q_iniziale = doc.to_dict['quant']
            db.collection(u'vini').document(doc.id).update({'quant': q_iniziale + q_reso})


    
    # else:
    #   col2.warning('⚠️ Per aggiornare le quantità in magazzino seleziona solo un ordine')

    # q_reso = col2.number_input('Quantità di reso', min_value=0, step=1)
    # aggiorna_reso = col2.button('Registra reso')



    # for dictionary in selected:
    #   q_reso = col2.number_input('Quantotà da rendere del vino selezionato', min_value=0, step=1)
    # effettua_reso = col2.button('Effettua reso vini selezionati')
    # if effettua_reso:
    #   quer
    #   db.collection(u'vini').document(vino_id).update({'quant': q_iniziale - q_evento})

    #   db.collection(u'resi').document()