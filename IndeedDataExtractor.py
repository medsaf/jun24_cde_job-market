from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class JobScraper:
    def __init__(self, base_search_url : str, num_pages=1, filename='data_v2.json'):
        """Initialise le scraper avec les paramètres de recherche."""
        self.base_search_url = base_search_url
        self.num_pages = num_pages
        self.filename = filename
        self.driver = self.init_driver()
        self.existing_data = self.load_existing_data()
        self.existing_job_ids = {job['job_id'] for job in self.existing_data}
        self.new_job_info_list = []

    def init_driver(self):
        """Initialise et renvoie une instance de WebDriver Selenium avec options."""
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                     "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--headless')  # Exécute Chrome en mode headless (sans interface graphique)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        return driver

    def load_existing_data(self):
        """Charge les données existantes depuis un fichier JSON."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return []

    def save_job_info(self):
        """Enregistre les informations des emplois dans un fichier JSON."""
        all_job_info_list = self.existing_data + self.new_job_info_list
        with open(self.filename, 'w', encoding='utf-8') as json_file:
            json.dump(all_job_info_list, json_file, ensure_ascii=False, indent=4)
        print(f"Les informations des emplois ont été enregistrées dans {self.filename}.")

    def get_job_ids(self, search_url):
        """Récupère les identifiants des offres d'emploi à partir de la page de recherche."""
        self.driver.get(search_url)
        time.sleep(3)  # Attendre le chargement de la page.

        job_ids = []  # Intialise la liste des identifiants de chaque offre.
        job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.cardOutline') # Récupère la carte de chaque offre.

        for card in job_cards:
            classes = card.get_attribute('class').split()
            for class_name in classes:
                if class_name.startswith('job_'):
                    job_id = class_name.split('_')[1]
                    job_ids.append(job_id)
                    break  # Job ID trouvé pour cette carte
        return job_ids

    def get_element_text(self, by, value):
        """Récupère le texte d'un élément en utilisant le sélecteur fourni."""
        try:
            element = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((by, value))) # tps en s et pas ms
            return element.text.strip()
        except (NoSuchElementException, TimeoutException):
            return None

    def get_job_info(self, job_id):
        """Récupère les informations détaillées d'une offre d'emploi donnée son identifiant."""
        job_url = f"https://fr.indeed.com/viewjob?jk={job_id}"
        self.driver.get(job_url)

        # Attendre un délai aléatoire entre 2 et 4 secondes pour faire moins automatisé.
        time.sleep(random.uniform(2, 4))

        job_info = {}
        job_info['job_id'] = job_id

        # Liste de dictionnaires contenant les sélecteurs pour chaque information
        # A retravailler afin de rendre plus robuste mais fonctionne pour l'instant
        selectors = [
            {'Titre_du_poste': {'by': By.CSS_SELECTOR, 'value': 'h1.jobsearch-JobInfoHeader-title'}},
            {'Nom_entreprise': {'by': By.CSS_SELECTOR, 'value': 'div.css-hon9z8'}},
            {'Note_entreprise': {'by': By.CSS_SELECTOR, 'value': 'div.css-1unnuiz'}},
            {'Localisation': {'by': By.CSS_SELECTOR, 'value': 'div.css-waniwe'}},
            {'Salaire': {'by': By.CSS_SELECTOR, 'value': 'span.css-19j1a75'}},
            {'Type_de_poste': {'by': By.CSS_SELECTOR, 'value': 'span.css-k5flys'}},
            {'Description_générale': {'by': By.ID, 'value': 'jobDescriptionText'}}
        ]

        # Utilisation de la liste de dictionnaires pour récupérer les informations
        for selector in selectors:
            for key, sel in selector.items():
                if key in job_info and job_info[key] is not None:
                    continue  # Skip if already found
                job_info[key] = self.get_element_text(sel['by'], sel['value'])

        # Bénéfices
        try:
            benefits_section = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="benefits-test"]'))
            )
            benefits_list = benefits_section.find_elements(By.TAG_NAME, 'li')
            benefits = [li.text.strip() for li in benefits_list]
            job_info['Benefices'] = benefits
        except (NoSuchElementException, TimeoutException):
            job_info['Benefices'] = None

        return job_info

    def scrape_jobs(self):
        """Orchestre le processus de scraping."""
        for page_num in range(1, self.num_pages + 1):
            print(f"Scraping page {page_num}")

            # Construire l'URL de la page avec le paramètre de pagination
            if page_num == 1:
                search_url = self.base_search_url
            else:
                start = (page_num - 1) * 10  # Indeed affiche 10 emplois par page
                search_url = f"{self.base_search_url}&start={start}"

            # Récupérer les job IDs de la page de recherche
            job_ids = self.get_job_ids(search_url)
            print(f"Found {len(job_ids)} job IDs on page {page_num}")

            # Pour chaque job_id, extraire les informations de l'emploi
            for job_id in job_ids:
                if job_id in self.existing_job_ids:
                    print(f"Job ID {job_id} already exists. Skipping.")
                    continue

                job_info = self.get_job_info(job_id)

                # Afficher les informations de l'emploi (optionnel)
                print(f"Job ID: {job_id}")
                for key, value in job_info.items():
                    print(f"{key}: {value}")
                    print("-" * 40)

                # Ajouter les informations de l'emploi à la liste
                self.new_job_info_list.append(job_info)
                self.existing_job_ids.add(job_id)  # Ajouter le job_id aux existants

                # Attendre un délai aléatoire entre 1 et 3 secondes entre les requêtes
                time.sleep(random.uniform(1, 3))

        # Enregistrer les informations des emplois dans un fichier JSON
        self.save_job_info()

    def close_driver(self):
        """Ferme le driver Selenium."""
        self.driver.quit()

def main():
    # Paramètres de scraping
    base_search_url = "https://fr.indeed.com/jobs?q=data%20scientist"
    num_pages = 5  # Modifier ce nombre pour scraper plus de pages
    filename = 'data_v2.json'

    # Initialisation du scraper
    scraper = JobScraper(base_search_url, num_pages, filename)

    # Démarrage du scraping
    try:
        scraper.scrape_jobs()
    finally:
        # Fermeture du driver
        scraper.close_driver()

if __name__ == "__main__":
    main()