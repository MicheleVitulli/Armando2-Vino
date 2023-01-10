import pandas as pd
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from codicefiscale import codicefiscale
import numpy as np


# --- Prendo i dati dal csv ---
df = pd.read_csv('comuni1.csv')

# prendo le regioni e le ordino
regioni = list(df['Regione'].drop_duplicates())
regioni = sorted(regioni)

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

# --- Gestione delle risorse in due tab

st.markdown('# <span style="color: #983C8E;">Gestione delle risorse</span>', unsafe_allow_html=True)


tab1, tab2 = st.tabs(["Form nuove risorse", "Visualizza risorse"])


current_date = datetime.now()
  
max_birth = current_date - relativedelta(years=15)

# --- Prima tab --- 
with tab1:
    st.subheader('Aggiungi risorse')

    r_name = st.text_input('Nome*')
    r_surname = st.text_input('Cognome*')
    r_sex =  st.selectbox('Sesso*', ('M', 'F'))
    r_phone = st.text_input('Telefono\Cellulare')
    r_birth = st.date_input('Data di nascita*', value=max_birth,min_value=datetime(1920,1,1), max_value=max_birth)

    r_reg = st.selectbox('Regione di nascita', regioni)

    province = list(df['Provincia'][np.where(df['Regione'] == r_reg)[0]].drop_duplicates())
    r_prov = st.selectbox('Provincia di nascita', province)

    city = list(df['Comune'][np.where(df['Provincia'] == r_prov)[0]].drop_duplicates())
    r_place = st.selectbox('Città di nascita*', city)

    st.caption('\* I campi contrassegnati sono obbligatori')

    try: # provo a generare il codice fiscale automaticamente 
        r_cf = codicefiscale.encode(surname=r_surname, name=r_name, sex=r_sex, birthdate=r_birth.strftime("%Y-%m-%d"), birthplace=r_place)    
    except:
        r_cf = st.text_input('Inserisci il codice fiscale')
    if st.button('**Aggiungi risorsa**'):

        doc_ref = db.collection("volontari").document(r_cf)

        # se non tutti i campi sono compilati rilascio un errore e non aggiungo al database
        if r_cf == '' or r_name=='' or r_surname=='' or r_sex=='' or r_birth=='' or r_place=='':
            st.error('Per favore, compilare tutti i campi', icon="🚨")
        # altrimenti aggiungo
        else:
            r_name = r_name.lower().capitalize()
            r_surname = r_surname.lower().capitalize()
            doc_ref.set({'cf': r_cf, 'name':r_name, 'surname':r_surname, 'sex':r_sex, 'phone':r_phone, 'birth':str(r_birth), 'place':r_place})

            st.success('Risorsa aggiunta con successo')

        
# --- Seconda tab --- 
# in questa tab visualizzo le risorse tramite una tabella aggrid
with tab2:
    st.subheader('Visualizza risorse')

    doc_ref = db.collection("volontari")
    docs = doc_ref.stream()

    volontari = []
    for doc in docs:
        vol_dict = {"Codice fiscale":doc.to_dict()['cf'], "Nome":doc.to_dict()['name'],"Cognome":doc.to_dict()['surname'], 
        "Telefono\Cellulare" : doc.to_dict()['phone'], "Data di nascita":doc.to_dict()['birth'], "Luogo di nascita":doc.to_dict()['place']}
        volontari.append(vol_dict)

    # se è presente almeno un volontario 
    if volontari!=[]:
        data = pd.DataFrame(volontari)
        gd = GridOptionsBuilder.from_dataframe(data)
        gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        gd.configure_grid_options(enableCellTextSelection=True)
        gd.configure_grid_options(ensureDomOrder=True)
        gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)

        gridOptions = gd.build()


        table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, height=270, fit_columns_on_grid_load=True)
        selected = table['selected_rows']

        col1, col2, col3 = st.columns(3)

        # creo un bottone per eliminare le voci selezionate
        elimina_selezionati = col1.button('**Elimina selezionati**')

        # se premuto elimino
        if elimina_selezionati:
            for diz in selected:
                query = db.collection(u'volontari').where(u'cf', u'==', diz['Codice fiscale'])
                docs = query.stream()
                for doc in docs:
                    db.collection('volontari').document(doc.id).delete()
            st.experimental_rerun()

    # se non è presente nessun volontario
    else:
        st.write('Non è registata alcun risorsa')


    
