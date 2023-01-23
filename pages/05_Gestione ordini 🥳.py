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
      prodotti.append(doc.id)

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
      info = vino.split('-')
      query = db.collection(u'vini').where(u'nome', u'==', info[0]).where('annata', '==', info[1])
      docs = query.stream()
      for doc in docs:
        nome = doc.to_dict()['nome']
        annata = doc.to_dict()['annata']
        prezzo_vg = doc.to_dict()['prezzo_vg']
        prezzo_a = doc.to_dict()['prezzo_a']
        prezzo_vp = doc.to_dict()['prezzo_vp']
        quant = doc.to_dict()['quant']

      q_vino = st.number_input('Quante bottiglie di {}'.format(vino), key=str(vino), step=1, min_value=0)

      dict_vino[vino]=[quant, q_vino]

  ordine = st.button('Registra ordine per ricevimento')

  if ordine and option!=[]:

    for i in dict_vino:
      q_iniziale = dict_vino[i][0]
      q_evento = dict_vino[i][1]

      if q_evento > q_iniziale:
        st.warning('⚠️ La quantità non è disponibile in magazzino. La scorta attuale è pari a:', q_iniziale)

      db.collection(u'vini').document(i).update({'quant': q_iniziale - q_evento})

      dict_vino[i].remove(dict_vino[i][0])

    db.collection(u'ordini').document(ord_id).set({
      'nome ordine': ord_nome,
      'data evento': str(ord_data),
      'ordinato': dict_vino
      })
      
    st.success('Ordine registrato con successo')
    # time.sleep(1)

with tab2:
  docs_ordini = db.collection('ordini').stream()

  ordini = []
  for doc in docs_ordini:
    ordinato = doc.to_dict()['ordinato']
    lista_vini = sorted(ordinato.keys())

    vini_ord = ''   
    for i in lista_vini:
      vini_ord += str(i) + ' = ' + str(ordinato[i][0]) + ';  '


    ordini.append({'Nome ordine': doc.to_dict()['nome ordine'], 'Data evento':doc.to_dict()['data evento'], 'Vini ordinati': vini_ord}) 

  if ordini != []:
    data = pd.DataFrame(ordini)
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
    gd.configure_selection(selection_mode='single', use_checkbox=True)
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
        st.experimental_rerun()

    
    docs_ordini = db.collection('ordini').stream()

    if len(selected) == 1:
      reso_id = selected[0]['Nome ordine'] 

      for doc in docs_ordini:
        if reso_id == doc.id:
          ordine = doc.to_dict()['ordinato']
          prodotti = ordine.keys()


      vini_resi = col2.multiselect('Scegli il prodotto da rendere', prodotti)

      dict_resi = {}
      for vino in vini_resi:
        q_reso = col2.number_input('Quantità di reso', min_value=0, step=1, key=vino)
        dict_resi[vino] = q_reso

      aggiorna_reso = col2.button('Registra reso')

      docs_vini = db.collection(u'vini').stream()

      if aggiorna_reso:
        db.collection(u'resi_ordini').document(reso_id).set({
                                                      'nome': reso_id,
                                                      'data': str(datetime.now()),
                                                      'reso': dict_resi})
        for vino in vini_resi:
          for doc in docs_vini:
            if vino == doc.id:
              q_iniziale = doc.to_dict()['quant']
              db.collection(u'vini').document(vino).update({'quant': q_iniziale + dict_resi[vino]})

        col2.success('Reso registrato con successo')

# --- Resi ---
  doc_ref = db.collection("resi_ordini")
  docs_resi = doc_ref.stream()

  resi = []
  for doc in docs_resi:
    
    for i in dict_resi:
      resi.append({"Data Reso" : doc.to_dict()['data'],"Nome": doc.to_dict()['nome'],  "Vino": i , "Quantità": dict_resi[i]}) 


  if resi != []:
    data2 = pd.DataFrame(resi)
    gd2 = GridOptionsBuilder.from_dataframe(data2)
    gd2.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
    gridOptions2 = gd2.build()


    table2 = AgGrid(data2, gridOptions=gridOptions2, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=False)
  else:
    st.write("Nessun reso registrato")