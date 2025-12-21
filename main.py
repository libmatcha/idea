"""
Demo: Extract emails and URLs from a large text using Matcha.
"""

from matcha import find_all

# Large sample text with emails and URLs embedded
TEXT = """
Dear Team,

I hope this message finds you well. Please find below the contact information 
for our upcoming project collaboration:

Project Lead: Sarah Johnson - sarah.johnson@techcorp.com
Technical Architect: Mike Chen - mike_chen123@devstudio.io  
QA Manager: Anna Williams - anna.w@qualitytest.org

For billing inquiries, please contact our finance department at 
billing@company.co or accounts_payable@company.co.uk

Our external consultants can be reached at:
- Dr. James Smith: j.smith@university.edu
- Prof. Maria Garcia: maria.garcia2024@research.ac.uk
- Consultant Team: team+support@consulting.firm.com

Please note that all communications should be CC'd to:
project_updates@techcorp.com and notifications@devstudio.io

For urgent matters, you can reach our 24/7 support at:
emergency_support@techcorp.com or call the hotline.

Legacy contacts (please update your records):
- old.contact@legacy.net
- archive2019@backup.org

Social media inquiries: social.media@marketing.co
Press releases: press@techcorp.com
Job applications: careers@techcorp.com, hr.recruitment@techcorp.com

International offices:
- Tokyo: tokyo.office@techcorp.co.jp
- Berlin: berlin@techcorp.de
- Sydney: info@techcorp.com.au

---
USEFUL LINKS:

Company Website: https://www.techcorp.com
Documentation: https://docs.techcorp.com/api/v2/guide
Support Portal: https://support.techcorp.com/tickets
Developer Hub: https://developers.techcorp.io/getting-started

External Resources:
- Python Docs: https://docs.python.org/3/library/re.html
- GitHub Repo: https://github.com/techcorp/matcha-lib
- Stack Overflow: https://stackoverflow.com/questions/tagged/pattern-matching
- Blog Post: https://blog.techcorp.com/2024/01/introducing-matcha

Partner Sites:
- https://partner1.example.com/integration
- https://api.partner2.io/v1/docs
- http://legacy.oldpartner.net/deprecated

Social Media:
- Twitter: https://twitter.com/techcorp
- LinkedIn: https://linkedin.com/company/techcorp
- YouTube: https://youtube.com/c/TechCorpOfficial

---
This email was sent from noreply@automated.techcorp.com
To unsubscribe, contact unsubscribe@mailinglist.techcorp.com
Visit https://techcorp.com/unsubscribe for more options.
"""


def main():
    print("=" * 70)
    print("MATCHA EXTRACTOR DEMO - Emails & URLs")
    print("=" * 70)
    print()
    print(f"Text length: {len(TEXT)} characters")
    print()
    
    # =========== EMAIL EXTRACTION ===========
    print("EMAILS")
    print("-" * 70)
    
    # Pattern: alphanumeric + dots/underscores/plus @ domain with dots
    email_pattern = "[anum:a-zA-Z0-9._+:]@[anum:a-zA-Z0-9.:]"
    print(f"Pattern: {email_pattern}")
    
    emails = find_all(email_pattern, TEXT)
    print(f"Found {len(emails)} emails:")
    for i, email in enumerate(emails, 1):
        print(f"  {i:2}. {email}")
    
    print()
    
    # =========== URL EXTRACTION ===========
    print("URLS")
    print("-" * 70)
    
    # Pattern: http + optional s + :// + domain + / + path
    # http               - literal "http"
    # [str:s:>=0<=1]     - optional "s" (0 or 1 occurrence)
    # ://                - literal
    # [anum:a-zA-Z0-9.-:]- domain (letters, numbers, dots, hyphens)
    # /                  - literal slash
    # [anum:a-zA-Z0-9./-:]- path (includes slashes)
    
    url_pattern = "http[str:s:>=0<=1]://[anum:a-zA-Z0-9.-:]/[anum:a-zA-Z0-9./-:]"
    print(f"Pattern: {url_pattern}")
    
    urls = find_all(url_pattern, TEXT)
    print(f"Found {len(urls)} URLs with paths:")
    for i, url in enumerate(urls, 1):
        print(f"  {i:2}. {url}")
    
    print()
    
    # Also find URLs without paths (just domain)
    simple_url_pattern = "http[str:s:>=0<=1]://[anum:a-zA-Z0-9.-:]"
    all_urls = find_all(simple_url_pattern, TEXT)
    
    # Filter to show only root domains (no path already captured)
    root_only = [u for u in all_urls if u not in [url.split('/')[0] + '//' + url.split('/')[2] for url in urls]]
    if root_only:
        print(f"Root domains only: {root_only}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
