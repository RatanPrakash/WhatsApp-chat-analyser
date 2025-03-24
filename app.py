from importlib.metadata import files
from idna import decode
import streamlit as st
import helper
import matplotlib.pyplot as plt
import os


st.sidebar.title('Whatsapp Chat Analyzer')
st.sidebar.write('Upload your whatsapp chat file to analyze the chat')
st.sidebar.write('The chat file should be a .txt file exported from whatsapp')

# uploaded_file = st.sidebar.file_uploader('Choose a file')
files = os.listdir('chats_dir')
file = st.sidebar.selectbox('Choose a file', files)
uploaded_file = open(f'chats_dir/{file}', 'r', encoding='utf-8')
chat_data = uploaded_file.read()

if chat_data is not None:
    # chat_data = uploaded_file.getvalue().decode('utf-8')
    df = helper.preprocess_data(chat_data)
    # st.write(df)

    #unique users dropdown menu to select user
    unique_users = df['user'].unique()
    unique_users = list(unique_users)
    unique_users.sort()
    unique_users.insert(0, 'All')
    selected_user = st.sidebar.selectbox('Select a user', unique_users)
    st.sidebar.write(selected_user)

    #fetch stats
    user_df, total_messages, media_messages, links, emojis, total_words = helper.fetch_stats(selected_user, df)
    st.title(f'User: {selected_user}')
    # st.write(user_df)
    #display below data side by side 
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write('Total messages:', total_messages)
        st.write('Media messages:', media_messages)
    with col2:
        st.write('Links shared:', links)
        st.write('Emojis shared:', emojis)
    with col3:
        st.write('Total words:', total_words)

    #busiest users (users with most messages)
    with st.expander('Busiest users'):
        if selected_user == 'All':
            busiest_users, plot = helper.busiest_users(df)
            st.write('Busiest users:')
            st.write(busiest_users)
            st.pyplot(plot)

    with st.expander('View word cloud and most common words'):
        st.pyplot(helper.word_cloud(df, selected_user))
        st.write('Most common words')
        temp_df, plot = helper.most_common_words(selected_user, df)
        st.write(temp_df)
        st.pyplot(plot)
        st.write("Most common emojis")
        temp_df = helper.most_common_emojis(selected_user, df)
        st.write(temp_df)

    with st.expander("Activity over time"):
        col1, col2 = st.columns(2)
        with col1: #left
            _, plot = helper.daily_timeline(selected_user, df)
            st.pyplot(plot)
            _, plot = helper.weekday_activity_map(selected_user, df)
            st.pyplot(plot)
        with col2: #right
            _, plot = helper.monthly_timeline(selected_user, df)
            st.pyplot(plot)
            _, plot = helper.month_activity_map(selected_user, df)
            st.pyplot(plot)
        
        st.write("Messages sent by hour")
        _, plot = helper.hour_activity_map(selected_user, df)
        st.pyplot(plot)

        st.write("weekly heatmap")
        plot = helper.activity_heatmap(selected_user, df)
        st.pyplot(plot)

    with st.expander("Links shared"):
        temp_df = helper.extract_links(df)
        st.write(temp_df)

        common_domains, plot = helper.plot_common_domains(df)
        st.pyplot(plot)
        st.write("Most common domains")
        st.write(common_domains)
    




