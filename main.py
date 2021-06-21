import streamlit as st
from bs4 import BeautifulSoup
import base64
from gtts import gTTS
import os
import pandas as pd
import csv
import requests

#-------------------------------------------------------------
def word_mp3(word_data):
    
    text_en = word_data
    ta_tts = gTTS(text_en)
    ta_tts.save('trans.mp3')
    audio_file = open('trans.mp3','rb')
    audio_bytes = audio_file.read()

    with st.beta_expander(word_data):
        
        st.audio(audio_bytes,format = 'audio/ogg',start_time = 0)
        b64 = base64.b64encode(audio_bytes).decode()
        href = f'<a href="data:file/mp3;base64,{b64}" download="{word_data}.mp3">Download mp3</a>'
        st.markdown(href, unsafe_allow_html=True)

#main-------------------------------------------------------------

st.title('英単語　翻訳アプリケーション')

st.header('解説')
st.write('アップロードした英単語を日本語に翻訳します')
st.write('翻訳した英単語のファイルと音声はダウンロード可能です')
st.header('アップロードファイル例')
st.write('アップロードするcsvファイルは以下のように作成してください')
st.write('列名を英単語にし、その下から翻訳したい英単語を書いてください')
example_df = pd.DataFrame({
    '英単語':['apple','black','soccer','penrose','metric'],
    '     ':['','','','',''],
    '     ':['','','','',''],
    '     ':['','','','',''],
    '     ':['','','','',''],
    '     ':['','','','',''],
    '     ':['','','','',''],
})

st.dataframe(example_df,width = 1000, height = 500)

example_csv = example_df.to_csv(index = False).encode()

b64 = base64.b64encode(example_csv).decode()

href = f'<a href="data:file/csv;base64,{b64}" download="example.csv">Download csv</a>'

st.header('exampleファイルのダウンロード')
    
st.markdown(href, unsafe_allow_html=True)


uploaded_file = st.sidebar.file_uploader("ファイルアップロード", type='csv') 
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df,width = 1000, height = 500)

    word_list = df['英単語']
    
    url_list = []

    for add_url in word_list:
        url = 'https://ejje.weblio.jp/content/' + str(add_url)
        url_list.append(url)
    
    word_explanations = []
    word_pronunciations = []
    
    latest_iteration = st.empty()
    bar = st.progress(0)
    i = 0
    
    
    for url in url_list: #意味取得
        try:
            
            res  = requests.get(url)
            soup = BeautifulSoup(res.text,'html.parser')
            
            word_explanation = soup.find('td',attrs = {'class','content-explanation'})
            word_explanations.append(word_explanation.text)

            word_pronunciation = soup.find('div',attrs = {'class','phoneticEjjeWrp'})
            word_pronunciation_replace = word_pronunciation.text.replace('/',' ')
            word_pronunciations.append(word_pronunciation_replace)
            
            latest_iteration.text(f'取得単語数{i+1}語')
            bar.progress((i+1)/len(word_list))
            
            
            i = i + 1

        except Exception:
            word_explanations.append('意味を取得できませんでした')
            word_pronunciations.append(' ')
            pass


    new_df = pd.DataFrame({

        '英単語':word_list,
        '意味':word_explanations,
        '発音記号':word_pronunciations

    })

    st.header('変換後データの表示')
    st.write(new_df)

    csv = new_df.to_csv(index = False).encode()

    b64 = base64.b64encode(csv).decode()

    href = f'<a href="data:file/csv;base64,{b64}" download="new_file.csv">Download csv</a>'

    st.header('変換後csvのダウンロード')
    
    st.markdown(href, unsafe_allow_html=True)

    st.header('発音')
    for word in word_list:
        word_mp3(word)
