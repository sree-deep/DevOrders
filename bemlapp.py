import streamlit as st
import pandas as pd

st.title("Development Orders")
file1=st.file_uploader('Upload PO SUMMARY please 🙂',key='1')

if file1 is not None:
    po_summary = pd.read_excel(file1,header=1)

    
    
file2=st.file_uploader('Upload SCHEDULES please 🙂',key='2')

if file2 is not None:
    schedules = pd.read_excel(file2,header=1)
  

file3=st.file_uploader('Upload GR PENDING please 🙂',key='3')

if file3 is not None:
    gr_pending = pd.read_excel(file3,header=0)


def get_date(start,gr_pending,po_summary):
    schedules.sort_values(by=['Deliv. Date'],inplace=True)
    old_len=gr_pending.shape[0]
    for index,row in gr_pending.iterrows():
        if index<start:
            continue
        if(row['Qty']>=0):
            continue
        
        helper=row['HELPER']
   
        print(index)
        order_quantity=po_summary.loc[po_summary['HELPER (PO + Material)'] == helper,'Order Quantity'].tolist()
        stbi=po_summary.loc[po_summary['HELPER (PO + Material)'] == helper,'Still to be invoiced (qty)'].tolist()
        if len(order_quantity)>=1 and len(stbi)>=1:
            paid=order_quantity[0]-stbi[0]

            schedules_new=schedules.loc[schedules['HELPER (PO + Material)'] == helper]
            for index1,row1 in schedules_new.iterrows():
                if paid<row1['Scheduled Qty']: 
                    gr_pending.loc[index,'Result_date']=row1['Deliv. Date']
                    
                    difference = row1['Scheduled Qty']-paid
                    #addition=stbi[0]-(-1*row['Qty'])
                    addition=stbi[0]-difference
                    po_summary.loc[po_summary['HELPER (PO + Material)'] == helper,'Still to be invoiced (qty)']=addition

                    if (-1*row['Qty'])>difference:
                        print('yes')
                        new_qty=row['Qty']+difference

                        gr_pending.at[index, 'Qty'] = -1*difference
                        gr_pending = gr_pending.append(gr_pending.iloc[index], ignore_index=True)
                        gr_pending.iloc[-1, gr_pending.columns.get_loc('Qty')] = new_qty
                    break
                else:
                    paid=paid-row1['Scheduled Qty']
    
                    
    if (old_len)!=len(gr_pending.index):
        return old_len,gr_pending,po_summary
    else:
        return -1,gr_pending,po_summary

    
x=0

import base64
def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

if file1 is not None and file2 is not None and file3 is not None:

    st.write("Your file is being generated 😁")
    
    old=gr_pending.shape[0]
    while True:
        x,gr_pending,po_summary=get_date(x,gr_pending,po_summary)
        
        if (gr_pending.shape[0])==old:
            break
        else:
            old=gr_pending.shape[0]

    gr_pending['Result_date'] = gr_pending['Result_date'].dt.date

    st.write(gr_pending)
    if st.button('Download GR PENDING as CSV File'):
        tmp_download_link = download_link(gr_pending, 'gr_pending.csv', 'Click here to download your data!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
    




