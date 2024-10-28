import requests
import sqlite3

# Get the top 5 headlines from the NewsAPI
def get_top5_headlines_from_api(url):
    response = requests.get(url)
    data = response.json()
    if data.get("status") == "ok":
        articles = data.get("articles")
        return articles[:5]
    return []

# Create a database to store the headlines
def create_database():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS headlines (headline TEXT, description TEXT, published_at TEXT)")
    conn.commit()
    conn.close()

# Insert the headlines into the database, but only if they don't already exist
def insert_headlines_into_database(headlines):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    for headline in headlines:
        c.execute("SELECT * FROM headlines WHERE headline = ?", (str(headline["title"]).strip(),))
        if not c.fetchall():
            c.execute('''
                      INSERT INTO headlines (headline, description, published_at) VALUES (?, ?, ?)
                      ''', (str(headline["title"]).strip(), str(headline["description"]).strip(), str(headline["publishedAt"])[:10]))
        else:
            print(f"Headline '{str(headline['title']).strip()}' already exists in the database.")
    print("Data has been saved to the database.")
    conn.commit()
    conn.close()

# Retrieve headlines from the database based on a keyword
def get_headlines_from_database(keyword):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("SELECT * FROM headlines WHERE headline LIKE ?", (f"%{keyword}%",))
    headlines = c.fetchall()
    conn.close()
    return headlines

create_database()

# Read the API key from a file to keep it secure
with open("news_api_key.txt", "r") as f:
    api_key = f.read().strip()

while True:
    # Prompt the user for input
    choice = input("Type 'a' to search the News API. Type 'd' to search the databse. Type 'exit' to close the program:")
    
    if choice.lower() == "exit":
        print("Exiting the program...")
        break
    elif choice.lower() == "a":
        topic = input("Enter a news topic to search for: ")
        
        if not topic or topic.isnumeric():
            # Check if the input is valid
            print("Invalid input. Please enter a valid news topic.")
            continue
        api_url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={api_key}"

        headlines = get_top5_headlines_from_api(api_url)
        if headlines:
            print(f"Top headlines about {topic}:")
            for i, headline in enumerate(headlines, 1):
                print(f"{i}. Title: {str(headline['title']).strip()}")
                print(f"  Date: {str(headline['publishedAt'])[:10]}")
                print(f"  Description: {str(headline['description']).strip()}")
            insert_headlines_into_database(headlines)
        else:
            print(f"The NewsAPI returned no headlines related to '{topic}'.")
    elif choice.lower() == "d":
        # Read the headlines from the database and display them
        keyword = input("Enter a keyword to search for in the database: ")

        if keyword:
            keyword_headlines = get_headlines_from_database(keyword)
            if keyword_headlines:
                print(f"Headlines related to '{keyword}':")
                for i, headline in enumerate(keyword_headlines, 1):
                    print(f"{i}. Title: {headline[0]}")
                    print(f"  Date: {headline[2]}")
                    print(f"  Description: {headline[1]}")
            else:
                print(f"No headlines found related to '{keyword}'.")
    else:
        print("Invalid input. Please enter 'a', 'd', or 'exit'.")
        continue