import streamlit as st
import preprocessor
import matplotlib.pyplot as plt


st.sidebar.title('Whatsapp Chat Analyzer')
st.sidebar.write('Upload your whatsapp chat file to analyze the chat')
st.sidebar.write('The chat file should be a .txt file exported from whatsapp')
uploaded_file = st.sidebar.file_uploader('Choose a file')

if uploaded_file is not None:
    chat_data = uploaded_file.getvalue().decode('utf-8')
    df = preprocessor.preprocess_data(chat_data)
    # st.write(df)

    #unique users dropdown menu to select user
    unique_users = df['user'].unique()
    unique_users = list(unique_users)
    unique_users.sort()
    unique_users.insert(0, 'All')
    selected_user = st.sidebar.selectbox('Select a user', unique_users)
    st.sidebar.write(selected_user)

    #fetch stats
    user_df, total_messages, media_messages, links, emojis, total_words = preprocessor.fetch_stats(selected_user, df)
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
            busiest_users, plot = preprocessor.busiest_users(df)
            st.write('Busiest users:')
            st.write(busiest_users)
            st.pyplot(plot)

    with st.expander('View word cloud and most common words'):
        st.pyplot(preprocessor.word_cloud(df, selected_user))
        st.write('Most common words')
        temp_df, plot = preprocessor.most_common_words(selected_user, df)
        st.write(temp_df)
        st.pyplot(plot)
        st.write("Most common emojis")
        temp_df = preprocessor.most_common_emojis(selected_user, df)
        st.write(temp_df)

    with st.expander("Activity over time"):
        col1, col2 = st.columns(2)
        with col1: #left
            _, plot = preprocessor.daily_timeline(selected_user, df)
            st.pyplot(plot)
            _, plot = preprocessor.weekday_activity_map(selected_user, df)
            st.pyplot(plot)
        with col2: #right
            _, plot = preprocessor.monthly_timeline(selected_user, df)
            st.pyplot(plot)
            _, plot = preprocessor.month_activity_map(selected_user, df)
            st.pyplot(plot)
        
        st.write("Messages sent by hour")
        _, plot = preprocessor.hour_activity_map(selected_user, df)
        st.pyplot(plot)

        st.write("weekly heatmap")
        plot = preprocessor.activity_heatmap(selected_user, df)
        st.pyplot(plot)


    




