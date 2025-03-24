from turtle import back
import pandas as pd
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import emoji
import numpy as np
import seaborn as sns

def preprocess_data(chat_data):
    date_time_pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][mM]\s-\s'
    messages = re.split(date_time_pattern, chat_data)[1:]
    date_times = re.findall(date_time_pattern, chat_data)
    df = pd.DataFrame({'date_time': date_times, 'message': messages})
    df['date_time'] = df['date_time'].str.replace('\u202f', ' ')
    df['date_time'] = pd.to_datetime(df['date_time'], format='%m/%d/%y, %I:%M %p - ')
    #separate users and their corresponding messages
    users = []
    messages = []
    for message in df['message']:
        entry = re.split('([\w\W]+?):\s', message)
        if len(entry) > 1:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    # extract date month year hour and minute from date_time
    df['date'] = df['date_time'].dt.date
    df['time'] = df['date_time'].dt.time
    df['hour'] = df['date_time'].dt.hour
    df['minute'] = df['date_time'].dt.minute
    df['day'] = df['date_time'].dt.day
    df['month'] = df['date_time'].dt.month
    df['year'] = df['date_time'].dt.year
    df['weekday'] = df['date_time'].dt.weekday
    df['weekday_en'] = df['weekday'].map({0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'})
    df['month_en'] = df['month'].map({1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'})
    # df['only_date'] = df['date_time'].dt.date
    df.sample(20)
    return df

def fetch_stats(selected_user, df):
    if selected_user == 'All':
        user_df = df
    else:
        user_df = df[df['user'] == selected_user]
    total_messages = user_df.shape[0]
    media_messages = user_df[user_df['message'] == '<Media omitted>\n']
    media_messages = media_messages.shape[0]
    links = user_df[user_df['message'].str.contains('http')]
    print(links)
    links = links.shape[0]
    emojis = user_df[user_df['message'].str.contains('[\U0001F600-\U0001F650]')].shape[0]
    words = user_df['message'].apply(lambda x: len(x.split()))
    total_words = words.sum()
    return user_df, total_messages, media_messages, links, emojis, total_words

def busiest_users(df):
    user_message_counts = df['user'].value_counts().reset_index()
    user_message_counts.columns = ['user', 'message_count']
    user_message_counts['percentage'] = (user_message_counts['message_count'] / user_message_counts['message_count'].sum()) * 100
    user_message_counts['percentage'] = user_message_counts['percentage'].round(2)
    user_message_counts = user_message_counts.sort_values(by='message_count', ascending=False)
    busiest_users = user_message_counts
    plt.bar(busiest_users.user, busiest_users.message_count)
    plt.xticks(rotation=45)
    plt.title('Busiest users')
    plt.xlabel('Users')
    plt.ylabel('Total messages')
    return busiest_users, plt

def word_cloud(df, selected_user):
    if selected_user == 'All':
        user_df = df
    else:
        user_df = df[df['user'] == selected_user]

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    temp = user_df[user_df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']
    temp = temp[temp['message'] != 'You deleted this message\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    words = ' '.join(words)

    wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color='white')
    wordcloud = wordcloud.generate(words)
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    return plt

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']
    temp = temp[temp['message'] != 'You deleted this message\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(50))
    most_common_df.columns = ['word', 'word_count']
    fig, ax = plt.subplots(figsize=(10, 15))
    ax.barh(most_common_df.word, most_common_df.word_count, height=0.8)
    ax.set_xlabel('Word count')
    ax.set_ylabel('Words')
    ax.set_title('Most common words')
    return most_common_df, fig

def most_common_emojis(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ['emoji', 'emoji_count']
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    monthly_timeline = df.groupby(['year', 'month_en']).count()['message'].reset_index()
    monthly_timeline['month_year'] = monthly_timeline['month_en'] + ' ' + monthly_timeline['year'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_timeline['month_year'], monthly_timeline['message'])
    plt.xticks(rotation=45)
    ax.set_title('Messages sent over Months')
    ax.set_xlabel('Month-Year')
    ax.set_ylabel('Total messages')
    return monthly_timeline, fig

def daily_timeline(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('date').count()['message'].reset_index()
    daily_timeline.columns = ['date', 'message_count']

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_timeline['date'], daily_timeline['message_count'])
    ax.set_title('Messages sent over time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total messages')
    return daily_timeline, fig

def weekday_activity_map(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    week_df = df['weekday_en'].value_counts().reset_index()
    week_df.columns = ['weekday', 'message_count']
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(week_df['weekday'], week_df['message_count'])
    ax.set_title('Messages sent per weekday')
    ax.set_xlabel('Weekday')
    ax.set_ylabel('Total messages')
    return None, fig

def month_activity_map(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    month_df = df['month_en'].value_counts().reset_index()
    month_df.columns = ['month', 'message_count']
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(month_df['month'], month_df['message_count'])
    ax.set_title('Messages sent per month')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total messages')

    return month_df, fig

def hour_activity_map(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]

    # Count the number of messages per hour
    hour_counts = df['hour'].value_counts().sort_index()
    # Convert hours to radians
    hours = np.arange(24)
    radians = 2 * np.pi * (hours / 24)

    # Create a polar plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.bar(radians, hour_counts, width=0.3, bottom=0.2)
    ax.set_theta_direction(-1)  # Clockwise
    ax.set_theta_offset(np.pi / 2.0)  # Start from top
    ax.set_xticks(radians)
    ax.set_xticklabels(hours)
    ax.set_yticklabels([])
    ax.set_title('Busiest Hours of the Day', va='bottom')

    return hour_counts, fig

def activity_heatmap(selected_user, df):
    if selected_user != 'All':
        df = df[df['user'] == selected_user]
    
    heatmap_data = df.pivot_table(index='weekday_en', columns='hour', values='message', aggfunc='count', fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, cmap='gray_r', linewidths=.5, fmt='d')
    plt.title('Activity Heatmap')
    plt.xlabel('Hour of Day')
    plt.ylabel('Day of Week')
    return plt

def extract_links(df):
    links = df[df['message'].str.contains('http', na=False)]
    links = links['message'].str.extractall(r'(https?://\S+)')[0]
    return links.reset_index(drop=True)

def plot_common_domains(df):
    links = extract_links(df)
    domains = links.str.extract(r'https?://(?:www\.)?([^/]+)')[0]
    domain_counts = domains.value_counts().reset_index()
    domain_counts.columns = ['domain', 'count']
    
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.bar(domain_counts['domain'], domain_counts['count'], width=0.5)
    plt.xticks(rotation='vertical')
    ax.set_title('Most Common Domains')
    ax.set_xlabel('Domain')
    ax.set_ylabel('Count')
    return domain_counts, fig