import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import urljoin
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

class ITProgerParser:
    def __init__(self):
        self.base_url = "https://itproger.com"
        self.news_url = os.getenv('ITPROGER_URL', 'https://itproger.com/news')

    def get_news_list(self) -> List[Dict]:
        """Получить список последних новостей"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.news_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Ищем все статьи в основном контенте
            articles = soup.select('.allArticles .article')
            
            for article in articles:
                try:
                    # Заголовок и ссылка
                    title_link = article.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text().strip()
                    link = urljoin(self.base_url, title_link['href'])
                    
                    # Изображение
                    img_elem = title_link.find('img')
                    image_url = ""
                    if img_elem and img_elem.get('src'):
                        image_url = urljoin(self.base_url, img_elem['src'])
                    
                    # Описание
                    desc_elem = article.find('span')
                    description = ""
                    if desc_elem:
                        # Берем следующий span после ссылки с заголовком
                        spans = article.find_all('span')
                        if len(spans) > 1:
                            description = spans[1].get_text().strip()
                    
                    # Дата и просмотры
                    meta_div = article.find('div')
                    date = ""
                    views = ""
                    if meta_div:
                        # Извлекаем дату
                        time_elem = meta_div.find('span', class_='time')
                        if time_elem:
                            date = time_elem.get_text().strip()
                        
                        # Извлекаем просмотры
                        eye_elem = meta_div.find('i', class_='fa-eye')
                        if eye_elem and eye_elem.parent:
                            views_text = eye_elem.parent.get_text().strip()
                            views = re.search(r'(\d+)', views_text)
                            views = views.group(1) if views else "0"
                    
                    if title and link:
                        news_items.append({
                            'title': title,
                            'url': link,
                            'image_url': image_url,
                            'description': description,
                            'date': date,
                            'views': views
                        })
                        
                except Exception as e:
                    print(f"Ошибка при парсинге статьи: {e}")
                    continue
                    
            return news_items
            
        except Exception as e:
            print(f"Ошибка при получении списка новостей: {e}")
            return []

    def get_article_content(self, article_url: str) -> Dict:
        """Получить полное содержимое статьи"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(article_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Заголовок
            title_elem = soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Основное содержимое - ищем в основном контенте страницы
            main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|article'))
            
            content = ""
            if main_content:
                # Убираем ненужные элементы (реклама, боковые панели и т.д.)
                for unwanted in main_content.find_all(['script', 'style', 'aside', 'nav']):
                    unwanted.decompose()
                
                # Извлекаем текстовые блоки
                text_blocks = main_content.find_all(['p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol'])
                
                for block in text_blocks:
                    if block.name in ['h2', 'h3', 'h4']:
                        text = block.get_text().strip()
                        if text:
                            content += f"**{text}**\n\n"
                    elif block.name == 'pre':
                        code_text = block.get_text().strip()
                        content += f"```\n{code_text}\n```\n\n"
                    elif block.name == 'code':
                        code_text = block.get_text().strip()
                        content += f"`{code_text}` "
                    elif block.name in ['ul', 'ol']:
                        items = block.find_all('li')
                        for item in items:
                            text = item.get_text().strip()
                            if text:
                                content += f"• {text}\n"
                        content += "\n"
                    else:  # p и другие
                        text = block.get_text().strip()
                        if text and len(text) > 10:  # Фильтруем очень короткие тексты
                            content += f"{text}\n\n"
            
            # Если контент не найден, используем fallback
            if not content.strip():
                content = "📝 Полное содержимое статьи доступно на сайте itProger.\n\n" \
                         f"[Читать полностью]({article_url})"
            
            return {
                'title': title,
                'full_content': content.strip(),
                'url': article_url
            }
            
        except Exception as e:
            print(f"Ошибка при получении содержимого статьи: {e}")
            return {
                'title': "", 
                'full_content': f"❌ Не удалось загрузить содержимое статьи\n\n[Читать на сайте]({article_url})", 
                'url': article_url
            }

    def search_articles(self, query: str) -> List[Dict]:
        """Поиск статей по запросу"""
        all_articles = self.get_news_list()
        if not all_articles:
            return []
        
        query_lower = query.lower()
        filtered = [
            article for article in all_articles
            if query_lower in article['title'].lower() or 
               query_lower in article.get('description', '').lower()
        ]
        
        return filtered

    def _extract_code_blocks(self, text: str) -> str:
        """Извлечь и форматировать блоки кода для markdown"""
        return text