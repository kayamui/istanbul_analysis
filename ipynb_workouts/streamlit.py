import streamlit as st
st.header('st.button')

if st.button('Say hello'):
    st.write('Why Hello There')
else:
    if st.button('Say Goodbye'):
        st.write('Goodbye')