

import streamlit as st
import requests
import json


url = 'http://54.161.220.191:5000/predict'
url = 'http://364f-54-196-208-236.ngrok.io/predict'
url = 'http://3.89.112.56:8000/predict'
url = 'http://3.82.121.52:8000/predict'
url = 'http://titan-alb-1881147824.us-east-1.elb.amazonaws.com:8000/predict'

# st.write('hello, fastapis and streamlit deployment')
# st.write('work please')
st.title('Predicting Passenger Survival') # Customer Loan Charged off or Fully paid')
st.header('''
           `Titanic model for playing with aws`

           ''')

Sex = st.radio('Sex',['male', 'female'])

Pclass = st.radio('Pclass', [1, 2, 3])

Age = st.number_input('Age', 0,100)


input_data_for_model = {    
    'Pclass': Pclass,
    'Sex': Sex,
    'Age': Age,
    }


if st.button("Predict"):
    if Pclass and Sex and Age is not None:
        input_json = json.dumps(input_data_for_model)
        response = requests.post(url, data=input_json)
        st.success(response.text)
    else:
        st.warning('Please enter all values')
