
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import operator

if not firebase_admin._apps:
	cred = credentials.Certificate('firestore-key.json')
	firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title='Armando 2.0', layout = 'wide', page_icon = '📦', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown('📦 Armando 2.0')

st.markdown('# <span style="color: #983C8E;">Grafici</span>', unsafe_allow_html=True)



option = st.selectbox(
    'Seleziona la categoria',
    (' ', 'Vendite', 'Ricevimenti'))


if option == "Pagina principale":
	pass

if option == "Vendite":
	st.header("Grafici vendite a grossisti e privati 📈")
	current_month = datetime.now().strftime("%m")
	current_year =  datetime.now().strftime("%Y")
	mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
	mese_drop = st.selectbox('Seleziona mese di riferimento', mesi)
	sel_mese = mesi.index(mese_drop) + 1
	sel_anno = st.number_input('Seleziona anno di riferimento', step=1, min_value=2000, max_value=int(current_year), value=int(current_year))
	
	col1, col2 = st.columns(2)

	#---------------------------VENDITE e GUADAGNI------------------------------------
	with col1:
		doc_ref = db.collection("vendite")
		docs = doc_ref.stream()
		st.markdown('# <span style="color: #983C8E;">Grafico delle vendite</span>', unsafe_allow_html=True)
		new_data = {'prodotti': [], 'quantità': []}
		for doc in docs:
			nome = doc.to_dict()['nome']
			quant = doc.to_dict()['quant']
			data = doc.to_dict()['data']
			mese = data.split('/')[1]
			anno = data.split('/')[2][0:4]
			
			if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
				if not nome in new_data['prodotti']:
					new_data['prodotti'].append(nome)
					new_data['quantità'].append(quant)
				
				else:
					pos = 0
					for i in range(len(new_data['prodotti'])):
						if nome == new_data['prodotti'][i]:
							pos = i
					temp = new_data['quantità'][pos]
					new_quant = temp + quant
					new_data['quantità'][pos] = new_quant
		
		plt.rcdefaults()
		fig, ax = plt.subplots()
		ax.barh(new_data['prodotti'], new_data['quantità'], color = "#983C8E")
		ax.set_xlabel('quantità')
		ax.invert_yaxis()
		plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
		st.pyplot(fig)


		#--------------vino più venduto----------------
		doc_refg = db.collection("vendite")
		docsg = doc_ref.stream()
		new_datagg = {'prodotti': [], 'quantità': []}
		new_datagp = {'prodotti': [], 'quantità': []}
		vino_grossista = ''
		vino_privato = ''
		for doc in docsg:
			nome = doc.to_dict()['nome']
			quant = doc.to_dict()['quant']
			data = doc.to_dict()['data']
			mese = data.split('/')[1]
			anno = data.split('/')[2][0:4]
			acq = doc.to_dict()['acquirente']

			if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Grossista' == str(acq):
				if not nome in new_datagg['prodotti']:
					new_datagg['prodotti'].append(nome)
					new_datagg['quantità'].append(quant)
				
				else:
					pos = 0
					for i in range(len(new_datagg['prodotti'])):
						if nome == new_datagg['prodotti'][i]:
							pos = i
					temp = new_datagg['quantità'][pos]
					new_quant = temp + quant
					new_datagg['quantità'][pos] = new_quant

			if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Privato' == str(acq):
				if not nome in new_datagp['prodotti']:
					new_datagp['prodotti'].append(nome)
					new_datagp['quantità'].append(quant)
				
				else:
					pos = 0
					for i in range(len(new_datagp['prodotti'])):
						if nome == new_datagp['prodotti'][i]:
							pos = i
					temp = new_datagp['quantità'][pos]
					new_quant = temp + quant
					new_datagp['quantità'][pos] = new_quant
		
		max_quant = max(new_datagg['quantità'])
		for t in range(len(new_datagg['quantità'])):
			gg = new_datagg['quantità'][t]
			if gg == max_quant:
				vino_grossista = vino_grossista + ", " + (new_datagg['prodotti'][t])

		max_quant = max(new_datagp['quantità'])
		for t in range(len(new_datagp['quantità'])):
			gg = new_datagp['quantità'][t]
			if gg == max_quant:
				vino_privato = vino_privato + ", " + (new_datagp['prodotti'][t])


		len1 = int(len(vino_privato))
		vp = vino_privato[2:]
		if ',' in vp:
			st.markdown(f'> I vini più venduti a privati sono: {vp}')
		else:
			st.caption(f'> Il vino più venduto a privati è: {vp}')
		
		len2 = int(len(vino_grossista))
		vg = vino_grossista[2:]
		if ',' in vg:
			st.markdown(f'> I vini più venduti a grossisti sono: {vg}')
		else:
			st.markdown(f'> Il vino più venduto a grossisti è: {vg}')



		st.markdown('# <span style="color: #983C8E;">Grafico dei guadagni</span>', unsafe_allow_html=True)
		doc_ref2 = db.collection("vendite")
		docs2 = doc_ref.stream()
		new_data2 = {'prodotti': [], 'guadagni': []}
		
		for doc in docs2:
			nome = doc.to_dict()['nome']
			guadagno = doc.to_dict()['guadagno']
			data = doc.to_dict()['data']
			mese = data.split('/')[1]
			anno = data.split('/')[2][0:4]
			
			if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
				if not nome in new_data2['prodotti']:
					new_data2['prodotti'].append(nome)
					new_data2['guadagni'].append(guadagno)
					
				else:
					pos = 0
					for i in range(len(new_data2['prodotti'])):
						if nome == new_data2['prodotti'][i]:
							pos = i
					temp = new_data2['guadagni'][pos]
					new_guadagno = temp + guadagno
					new_data2['guadagni'][pos] = new_guadagno

		plt.rcdefaults()		
		fig3, ax3 = plt.subplots()
		ax3.barh(new_data2['prodotti'], new_data2['guadagni'],  color = "#983C8E")
		ax3.set_xlabel('guadagno in euro')
		ax3.invert_yaxis()
		plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
		st.pyplot(fig3)



	#---------------------------RESI e RICAVI------------------------------------
	with col2:
		
		st.markdown('# <span style="color: #983C8E;">Grafico dei ricavi</span>', unsafe_allow_html=True)
		doc_ref2 = db.collection("vendite")
		docs2 = doc_ref.stream()
		new_data2 = {'prodotti': [], 'ricavi': []}
		
		for doc in docs2:
			nome = doc.to_dict()['nome']
			ricavo = doc.to_dict()['ricavo']
			data = doc.to_dict()['data']
			mese = data.split('/')[1]
			anno = data.split('/')[2][0:4]
			
			if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
				if not nome in new_data2['prodotti']:
					new_data2['prodotti'].append(nome)
					new_data2['ricavi'].append(ricavo)
				
				else:
					pos = 0
					for i in range(len(new_data2['prodotti'])):
						if nome == new_data2['prodotti'][i]:
							pos = i
					temp = new_data2['ricavi'][pos]
					new_ricavo = temp + ricavo
					new_data2['ricavi'][pos] = new_ricavo
		
		plt.rcdefaults()
		fig2, ax2 = plt.subplots()
		ax2.barh(new_data2['prodotti'], new_data2['ricavi'], color = "#983C8E")
		ax2.set_xlabel('ricavo in euro')
		ax2.invert_yaxis()
		plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
		st.pyplot(fig2)
		
		
#--------------------PROVA-----------------------
	#st.markdown('# <span style="color: #983C8E;">Grafico dei guadagni</span>', unsafe_allow_html=True)
	doc_ref2 = db.collection("vendite")
	docs2 = doc_ref.stream()
	new_data2 = {'prodotti': [], 'guadagni': []}
	for doc in docs2:
		nome = doc.to_dict()['nome']
		guadagno = doc.to_dict()['guadagno']
		data = doc.to_dict()['data']
		mese = data.split('/')[1]
		anno = data.split('/')[2][0:4]
		
		if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
			if not nome in new_data2['prodotti']:
				new_data2['prodotti'].append(nome)
				new_data2['guadagni'].append(guadagno)
			
			else:
				pos = 0
				for i in range(len(new_data2['prodotti'])):
					if nome == new_data2['prodotti'][i]:
						pos = i
				temp = new_data2['guadagni'][pos]
				new_guadagno = temp + guadagno
				new_data2['guadagni'][pos] = new_guadagno

	plt.rcdefaults()
	fig3, ax3 = plt.subplots()
	ax3.barh(new_data2['prodotti'], new_data2['guadagni'], color = "#983C8E")
	ax3.invert_yaxis()
	ax3.set_xlabel('guadagno in euro')
	plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
	

	major_ticks_top=np.linspace(0,1000,5)
	minor_ticks_top=np.linspace(0,1000,10)
	ax3.set_xticks(major_ticks_top)
	ax3.set_xticks(minor_ticks_top,minor=True)
	ax3.set_title("Subplot 1")
	ax3.grid(which="major",alpha=0.6)
	ax3.grid(which="minor",alpha=0.3)
	#st.pyplot(fig3)
#-------------------FINE PROVA----------------------------





if option == "Ricevimenti":
	st.header("Grafici ricevimenti 📉")
	current_month = datetime.now().strftime("%m")
	current_year =  datetime.now().strftime("%Y")
	mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
	mese_drop = st.selectbox('Seleziona mese di riferimento', mesi)
	sel_mese = mesi.index(mese_drop) + 1
	sel_anno = st.number_input('Seleziona anno di riferimento', step=1, min_value=2000, max_value=int(current_year), value=int(current_year))
	doc_ref = db.collection("vendite")
	docs = doc_ref.stream()


