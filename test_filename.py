from urllib.parse import urlparse

def get_filename(target_url):
    try:
        parsed = urlparse(target_url)
        domain = parsed.netloc.replace('.', '-')
        path = parsed.path.strip('/')
        
        if path:
            path_str = path.replace('/', '_')
            output_filename = f"{domain}_{path_str}.md"
        else:
            output_filename = f"{domain}.md"
            
        if not domain:
            output_filename = "merged_docs.md"
    except Exception:
        output_filename = "merged_docs.md"
    return output_filename

test_urls = [
    "https://example.com/",
    "https://example.com/docs",
    "https://example.com/home",
    "https://example.com/docs/api",
    "https://docs.python.org/3/library/",
]

for url in test_urls:
    print(f"{url} -> {get_filename(url)}")
