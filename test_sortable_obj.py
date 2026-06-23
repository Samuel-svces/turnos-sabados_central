import streamlit as st
from streamlit_sortables import sort_items

items = [
    {'header': 'Sat', 'items': [{'id':'1', 'label':'Dr. Juan'}, {'id':'2', 'label':'Dr. Pedro'}]}
]
res = sort_items(items)
print(res)
