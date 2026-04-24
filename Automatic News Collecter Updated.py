import requests
from bs4 import BeautifulSoup

def get_bbc_headlines(category_url):
    """Scrapes top 15 headlines based on India or World selection."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(category_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headlines = []
        # Searching for headings that typically wrap BBC links
        for item in soup.find_all(['h2', 'h3'], limit=60):
            title = item.get_text().strip()
            parent_a = item.find_parent('a')
            
            if parent_a and parent_a.get('href'):
                link = parent_a.get('href')
                if not link.startswith('http'):
                    link = "https://www.bbc.com" + link
                
                # Filter for news links and avoid duplicates
                if link not in [h['link'] for h in headlines] and "/news/" in link:
                    # Filter out non-news links like 'Terms of Use' if they creep in
                    if any(x in link for x in ['/india', '/world', '/articles']):
                        headlines.append({'title': title, 'link': link})
            
            if len(headlines) == 15:
                break
                
        return headlines
    except Exception as e:
        print(f"Error fetching headlines: {e}")
        return []

def get_article_details(url, num_paragraphs):
    """Fetches text paragraphs from the selected article."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BBC articles usually store text in 'p' tags within specific sections
        paragraphs = soup.find_all('p')
        clean_paragraphs = [p.get_text() for p in paragraphs if len(p.get_text()) > 45]
        
        return clean_paragraphs[:num_paragraphs]
    except Exception as e:
        print(f"Error fetching article content: {e}")
        return []

def main():
    print("--- BBC News Scraper ---")
    print("1. National News (India)")
    print("2. International News (World)")
    
    choice_type = input("\nEnter choice (1 or 2): ")
    
    if choice_type == '1':
        # Specific URL for India News
        target_url = "https://www.bbc.com/news/world/asia/india"
        print("\n--- Fetching Latest News from India ---")
    elif choice_type == '2':
        target_url = "https://www.bbc.com/news/world"
        print("\n--- Fetching International News ---")
    else:
        print("Invalid choice.")
        return

    news_list = get_bbc_headlines(target_url)
    
    if not news_list:
        print("No headlines found. Check your internet or the URL.")
        return

    print(f"\nFound {len(news_list)} headlines:\n")
    for idx, news in enumerate(news_list, 1):
        print(f"{idx}. {news['title']}")

    try:
        choice = int(input("\nSelect a headline number: ")) - 1
        
        if 0 <= choice < len(news_list):
            selected = news_list[choice]
            para_count = int(input("How many paragraphs  would you like to read?"))
            print(f"\n--- {selected['title']} ---\n")
            content = get_article_details(selected['link'], para_count)
            
            if content:
                for i, p in enumerate(content, 1):
                    print(f"[{i}] {p}\n")
            else:
                print("Could not extract story text. The page layout might be different.")
        else:
            print("Selection out of range.")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
