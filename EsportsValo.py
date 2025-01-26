import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load and preprocess the dataset
@st.cache_data
def load_data():
    file_path = 'valorant champions istanbul.csv'  # Update with correct path if needed
    data = pd.read_csv(file_path)
    data['KAST'] = data['KAST'].str.replace('%', '').astype(float)
    data['Prize'] = data['Prize'].str.replace('[\$,]', '', regex=True).astype(float)
    return data

data = load_data()

# Visualization functions
def plot_player_stats(player_name):
    player_data = data[data['Player'] == player_name]
    if player_data.empty:
        st.error(f"Player '{player_name}' not found in the dataset.")
        return

    # Rounds distribution with borders
    rounds_won = player_data['Rounds Win'].values[0]
    rounds_lost = player_data['Rounds Lose'].values[0]
    fig1, ax1 = plt.subplots()
    wedges, texts, autotexts = ax1.pie(
        [rounds_won, rounds_lost],
        labels=['Rounds Won', 'Rounds Lost'],
        autopct='%1.1f%%',
        colors=['#7E25E8', '#5103FF'],
        startangle=140,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1}  # Add borders
    )
    ax1.set_title(f"Rounds Distribution for {player_name}")
    plt.tight_layout()  # Adjust layout to add space between the plots
    st.pyplot(fig1)

    # Calculate Rounds Won %
    rounds_played = player_data['Rounds Played'].values[0]
    rounds_won_percentage = (rounds_won / rounds_played) * 100 if rounds_played != 0 else 0

    # Performance stats (Spider Web Chart)
    stats = {
        'Kills': player_data['Kill'].values[0],
        'K/D Ratio': player_data['K/D'].values[0],
        'Headshot %': player_data['HS %'].values[0],
        'Rounds Won %': rounds_won_percentage,
        'KAST (%)': player_data['KAST'].values[0]
    }

    # Normalize values to a scale of 100 (optional: customize based on max value in the dataset)
    max_kills = data['Kill'].max()
    max_kd_ratio = data['K/D'].max()
    max_headshot_percentage = 100  # As it's already a percentage
    max_rounds_won_percentage = 100  # As it's already a percentage
    max_kast = 100  # As it's also a percentage

    stats_normalized = {
        'Kills': (stats['Kills'] / max_kills) * 100,
        'K/D Ratio': (stats['K/D Ratio'] / max_kd_ratio) * 100,
        'Headshot %': stats['Headshot %'],  # Already a percentage
        'Rounds Won %': stats['Rounds Won %'],  # Already a percentage
        'KAST (%)': stats['KAST (%)'],  # Already a percentage
    }

    categories = list(stats_normalized.keys())
    values = list(stats_normalized.values())
    values += values[:1]  # Repeat the first value to close the circle

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax2.fill(angles, values, color='skyblue', alpha=0.4)
    ax2.plot(angles, values, color='blue', linewidth=2)
    ax2.set_yticks([20, 40, 60, 80, 100])  # Scale with ticks from 0 to 100
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories)

    ax2.set_title(f"Performance Stats for {player_name}", fontsize=14)
    plt.tight_layout()  # Add space for the radar chart
    st.pyplot(fig2)

def plot_leaderboard(metric, top_n):
    if metric not in data.columns:
        st.error(f"Metric '{metric}' not found in the dataset.")
        return

    leaderboard = data[['Player', metric]].sort_values(by=metric, ascending=False).head(top_n)
    fig, ax = plt.subplots()
    sns.barplot(y='Player', x=metric, data=leaderboard, palette='viridis', edgecolor='black', ax=ax)
    ax.set_title(f"Top {top_n} Players by {metric}")
    ax.set_xlabel(metric)
    ax.set_ylabel("Player")
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()  # Adjust layout for leaderboard bar chart
    st.pyplot(fig)

# Streamlit app layout
st.title("Valorant Esports Data Visualization")
st.sidebar.title("Player & Leaderboard Analysis")

# Sidebar options
option = st.sidebar.radio("Choose an option:", ['Player Stats', 'Leaderboard'])

if option == 'Player Stats':
    player_name = st.sidebar.text_input("Enter player name:")
    if st.sidebar.button("Show Stats"):
        plot_player_stats(player_name)

elif option == 'Leaderboard':
    # Filter out 'Rank' and 'Role' from leaderboard metrics
    leaderboard_columns = [col for col in data.columns[3:] if col not in ['Rank', 'Role']]
    metric = st.sidebar.selectbox("Select a metric:", leaderboard_columns)
    top_n = st.sidebar.slider("Number of players to display:", min_value=5, max_value=20, value=10)
    if st.sidebar.button("Show Leaderboard"):
        plot_leaderboard(metric, top_n)
