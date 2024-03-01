from bs4 import BeautifulSoup
import json
import httpx


URL = 'https://www.securityandpolicing.co.uk/exhibitors/exhibitors-list-2024/'

html_content = httpx.get(URL)

# Assuming html_content contains the HTML source you provided
soup = BeautifulSoup(html_content, 'html.parser')

exhibitors = []

for exhibitor in soup.find_all("div", class_="exhibitor"):
    data = {}
    data['organisation'] = exhibitor['data-organisation']
    data['sectors'] = json.loads(exhibitor['data-sectors'])
    title_element = exhibitor.find("h6")
    if title_element and title_element.a:
        data['title'] = title_element.get_text(strip=True)
        data['link'] = title_element.a['href']
    stand_element = exhibitor.find("div", class_="col-md-3")
    if stand_element:
        data['stand'] = stand_element.get_text(strip=True)
    company_element = exhibitor.find("div", class_="col-md-9")
    if company_element:
        data['company'] = company_element.get_text(strip=True)
    exhibitors.append(data)
    description_element = exhibitor.find("p")
    if description_element:
        data['description'] = description_element.get_text(strip=True)

if __name__ == '__main__':
    print(json.dumps(exhibitors, indent=2))
