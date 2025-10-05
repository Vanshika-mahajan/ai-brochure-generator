# 1. ALL IMPORTS GO HERE
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from urllib.parse import urljoin
from io import BytesIO

# 2. MODEL INITIALIZATION
# Initialize models once to be efficient
print("Loading AI models... This might take a moment.")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-distilroberta-base")
print("✅ AI models loaded.")

# 3. ALL FUNCTION DEFINITIONS GO HERE
def crawl_and_classify_website(base_url):
    """
    Crawls the first few pages of a website, classifies their content using an AI model,
    and returns a dictionary of categorized text, the main page's parsed HTML (soup),
    and the total text scraped.
    """
    print(f"🧠 Starting intelligent crawl at: {base_url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Defines the categories for the AI classifier
    brochure_categories = ["Company Overview", "Products and Services", "Contact Information"]
    
    # This dictionary will hold the text for each category
    categorized_text = {cat: "" for cat in brochure_categories}
    total_scraped_text = ""

    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Create a set of URLs to visit, starting with the base URL
        links_to_visit = {base_url}
        for link in soup.find_all('a', href=True):
            if len(links_to_visit) >= 10:
                break
            
            absolute_url = urljoin(base_url, link['href'])
            
            if base_url in absolute_url:
                links_to_visit.add(absolute_url)

        # Visit each found page and classify its content
        for url in links_to_visit:
            print(f"  -> Analyzing page: {url}")
            page_response = requests.get(url, headers=headers, timeout=10)
            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.content, 'html.parser')
                page_text = ' '.join([p.get_text() for p in page_soup.find_all('p')])
                
                total_scraped_text += page_text + " "

                if len(page_text.split()) > 50:
                    result = classifier(page_text[:1024], candidate_labels=brochure_categories)
                    best_category = result['labels'][0]
                    score = result['scores'][0]

                    print(f"    - Classified as '{best_category}' with score: {score:.2f}")
                    
                    if score > 0.60:
                        categorized_text[best_category] += page_text + " "

        return soup, categorized_text, total_scraped_text

    except requests.exceptions.RequestException as e:
        print(f"Error during intelligent crawl: {e}")
        return None, None, None

def extract_images(base_url, soup):
    """Finds the logo and a few other relevant images from the page."""
    images = {'logo': None, 'general': []}
    img_tags = soup.find_all('img')
    
    for img in img_tags:
        src = img.get('src')
        if not src:
            continue
            
        absolute_src = urljoin(base_url, src)
        
        alt_text = img.get('alt', '').lower()
        if not images['logo'] and ('logo' in absolute_src or 'logo' in alt_text):
            images['logo'] = absolute_src
            print(f"  -> Found logo: {absolute_src}")
            continue
            
        if len(images['general']) < 2 and not absolute_src.endswith(('.svg', '.gif')):
            images['general'].append(absolute_src)
            print(f"  -> Found general image: {absolute_src}")
            
    return images

def get_summary(text):
    """Generates a concise summary of the text."""
    if not text or len(text.split()) < 50:
        print("⚠️ Text too short for a meaningful summary.")
        return "No summary could be generated as the website content was too short."
    summary = summarizer(text[:1024], max_length=150, min_length=40, do_sample=False)
    print("✅ Summary generated!")
    return summary[0]['summary_text']

def get_key_details(text):
    """Extracts key details using question-answering."""
    if not text or len(text.strip()) == 0:
        print("⚠️ Context for key details is empty. Skipping question-answering.")
        return "No specific product or service details could be extracted."
    
    question = "What are the main services, products, or solutions offered?"
    result = qa_pipeline(question=question, context=text)
    print("✅ Key details extracted!")
    return result['answer']

def create_brochure_pdf(filename, company_url, summary, details, image_urls):
    """Creates a PDF with text and images, handling image downloads robustly."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    story.append(Paragraph(f"AI-Generated Brochure for: {company_url}", styles['h1']))
    story.append(Spacer(1, 12))

    if image_urls.get('logo'):
        try:
            response = requests.get(image_urls['logo'], headers=headers)
            response.raise_for_status()
            
            logo_data = BytesIO(response.content)
            logo = Image(logo_data, width=120, height=60, kind='proportional')
            
            story.append(logo)
            story.append(Spacer(1, 24))
        except Exception as e:
            print(f"⚠️ Warning: Could not add logo. Error: {e}")

    story.append(Paragraph("Company Overview", styles['h2']))
    story.append(Paragraph(summary, styles['BodyText']))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Key Offerings", styles['h2']))
    story.append(Paragraph(details, styles['BodyText']))
    story.append(Spacer(1, 12))

    if image_urls.get('general'):
        try:
            general_image_url = image_urls['general'][0]
            response = requests.get(general_image_url, headers=headers)
            response.raise_for_status()
            
            img_data = BytesIO(response.content)
            img = Image(img_data, width=450, height=225, kind='proportional')

            story.append(img)
        except Exception as e:
            print(f"⚠️ Warning: Could not add general image. Error: {e}")
            
    doc.build(story)
    print(f"🎉 Brochure with images saved as {filename}!")


# 4. MAIN EXECUTION BLOCK GOES AT THE END
if __name__ == "__main__":
    target_url = input("Enter a valid company URL (e.g., https://www.google.com): ")
    
    main_soup, categorized_content, total_text = crawl_and_classify_website(target_url)
    
    if main_soup:
        print("\n✅ Content scraped. Now generating brochure sections...")
        
        overview_text = categorized_content.get("Company Overview")
        services_text = categorized_content.get("Products and Services")

        if not overview_text and not services_text:
            print("⚠️ Intelligent classification found no specific sections. Switching to fallback mode.")
            overview_text = total_text
            services_text = total_text
        else:
            print("✅ Intelligent classification successful!")

        company_summary = get_summary(overview_text)
        company_details = get_key_details(services_text)
        
        image_data = extract_images(target_url, main_soup)
        
        output_filename = "final_brochure.pdf"
        create_brochure_pdf(
            output_filename,
            target_url,
            company_summary,
            company_details,
            image_data
        )
    else:
        print("\n❌ Failed to retrieve or categorize website data. Brochure not created.")