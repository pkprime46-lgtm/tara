import requests
from bs4 import BeautifulSoup

# Function to scrape product data from a website
def scrape_products(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Example: Adjust the following selection to match the HTML structure of the target site
        for item in soup.select('.product-item'):
            name = item.select_one('.product-name').text.strip()
            price = item.select_one('.product-price').text.strip()
            products.append({'name': name, 'price': price})
        
        return products
    else:
        print("Failed to retrieve products from API, falling back to hardcoded products.")
        return []

# Fallback hardcoded products
def get_hardcoded_products():
    return [
        {'name': 'Fallback Product 1', 'price': '$10.00'},
        {'name': 'Fallback Product 2', 'price': '$20.00'},
    ]

# Main function to get products
def get_products():
    url = 'https://example.com/api/products'  # Replace with actual API URL
    products = scrape_products(url)
    if not products:
        products = get_hardcoded_products()
    return products

if __name__ == '__main__':
    products = get_products()
    for product in products:
        print(f"Name: {product['name']}, Price: {product['price']}")