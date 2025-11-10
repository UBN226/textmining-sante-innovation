import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

def scraper_forbes_afrique(nb_articles=30):
    """
    Scrape les articles du site Forbes Afrique en utilisant Selenium.
    
    Paramètres:
    - nb_articles: Nombre d'articles à récupérer (par défaut 30)
    
    Retour:
    - DataFrame contenant les colonnes: source, titre, date, lien, texte
    """
    
    articles_data = []
    driver = None
    
    try:
        # Initialiser le navigateur Chrome avec les options appropriées
        print("Initialisation du navigateur Chrome...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-resources')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Accéder au site
        print("Accès au site Forbes Afrique...")
        driver.get("https://forbesafrique.com/")
        
        # Attendre le chargement de la page
        time.sleep(3)
        
        # Accepter les cookies si présent
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter')]"))
            )
            accept_button.click()
            print("Cookies acceptés")
            time.sleep(1)
        except:
            print("Pas de popup de cookies trouvée")
        
        # Faire défiler la page pour charger les articles
        print("Chargement des articles...")
        scroll_count = 0
        max_scrolls = 10
        
        while scroll_count < max_scrolls:
            # Faire défiler vers le bas
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            scroll_count += 1
            print(f"Scroll {scroll_count}/{max_scrolls}")
        
        # Chercher les articles avec différentes stratégies
        print("\nRecherche des articles...")
        
        # Stratégie 1: Chercher les liens dans les articles
        article_links = []
        
        # Chercher tous les liens
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total de liens trouvés: {len(all_links)}")
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                # Vérifier si c'est un lien d'article valide
                if href and text and len(text) > 10 and not href.startswith('javascript'):
                    if '/article' in href or '/news' in href or '/blog' in href or 'forbesafrique.com' in href:
                        article_links.append({
                            'url': href,
                            'titre': text,
                            'element': link
                        })
            except:
                pass
        
        print(f"Articles trouvés: {len(article_links)}")
        
        # Extraire les informations des articles
        seen_urls = set()
        
        for i, article in enumerate(article_links):
            if len(articles_data) >= nb_articles:
                break
            
            try:
                url = article['url']
                titre = article['titre']
                
                # Éviter les doublons
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                # Chercher la date
                try:
                    parent = article['element'].find_element(By.XPATH, "./ancestor::div[1]")
                    parent_text = parent.text
                    date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', parent_text)
                    date_str = date_match.group(1) if date_match else "N/A"
                except:
                    date_str = "N/A"
                
                source = "Forbes Afrique"
                
                print(f"Scraping article {len(articles_data)+1}: {titre[:60]}...")
                
                # Accéder à l'article
                try:
                    driver.execute_script("window.open(arguments[0]);", url)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)
                    
                    # Chercher le contenu
                    try:
                        contenu = driver.find_element(By.CSS_SELECTOR, "main, article, .content, .post-content, [class*='content'], [class*='article']")
                        texte = contenu.text
                    except:
                        texte = "Texte non disponible"
                    
                    texte = texte[:1000] if len(texte) > 1000 else texte
                    
                    # Fermer l'onglet
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    print(f"  Erreur: {e}")
                    if len(driver.window_handles) > 1:
                        try:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except:
                            pass
                    texte = "Erreur lors de la récupération du texte"
                
                # Ajouter les données
                articles_data.append({
                    'source': source,
                    'titre': titre,
                    'date': date_str,
                    'lien': url,
                    'texte': texte
                })
                
                print(f"  ✓ Article ajouté ({len(articles_data)}/{nb_articles})")
                
            except Exception as e:
                print(f"  ✗ Erreur: {e}")
                continue
        
        # Créer le DataFrame
        df = pd.DataFrame(articles_data)
        return df
    
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    
    finally:
        # Fermer le navigateur
        if driver:
            try:
                driver.quit()
                print("Navigateur fermé")
            except:
                pass


def main():
    """Fonction principale"""
    
    print("=" * 80)
    print("SCRAPER DES ARTICLES FORBES AFRIQUE - AVEC SELENIUM")
    print("=" * 80)
    
    # Scraper 30 articles
    df = scraper_forbes_afrique(nb_articles=30)
    
    if not df.empty:
        print("\n" + "=" * 80)
        print(f"RÉSULTAT: {len(df)} articles récupérés")
        print("=" * 80)
        
        # Afficher les premières lignes
        print("\nAperçu des données:")
        print(df.head())
        
        # Afficher les informations du DataFrame
        print("\nInformations du DataFrame:")
        print(df.info())
        
        # Afficher les colonnes
        print("\nColonnes:")
        print(df.columns.tolist())
        
        # Sauvegarder en CSV
        df.to_csv('articles_forbes.csv', index=False, encoding='utf-8')
        print("\n✓ Données sauvegardées dans 'articles_forbes.csv'")
        
        # Sauvegarder en Excel
        df.to_excel('articles_forbes.xlsx', index=False, engine='openpyxl')
        print("✓ Données sauvegardées dans 'articles_forbes.xlsx'")
        
        return df
    else:
        print("Aucun article n'a pu être récupéré.")
        return None


if __name__ == "__main__":
    df_articles = main()
