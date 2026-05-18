import os
import sys
from pathlib import Path

# Setup Django
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

import pandas as pd
from predict.feature_extractor import extract_features

def extract_batch(urls, label, max_urls=200, output_csv=None):
    results = []
    urls = urls[:max_urls]
    total = len(urls)
    
    for idx, url in enumerate(urls):
        try:
            feats = extract_features(url)
            feats['url'] = url
            feats['label'] = label
            results.append(feats)
        except Exception as e:
            print(f"Failed {url[:60]}: {type(e).__name__}")
        
        # Save intermediate results every 50 URLs
        if (idx+1) % 50 == 0 and output_csv and results:
            pd.DataFrame(results).to_csv(output_csv, index=False)
            print(f"  Saved {len(results)} rows so far")
        
        if (idx+1) % 50 == 0 or (idx+1) == total:
            print(f"Progress: {idx+1}/{total}")
    
    return results

if __name__ == "__main__":
    df = pd.read_csv('datasets/raw/phiusiil.csv', usecols=['URL', 'label'])
    phishing = df[df['label'] == 1]['URL'].tolist()
    legit = df[df['label'] == 0]['URL'].tolist()
    
    print(f"Phishing: {len(phishing)}, Legitimate: {len(legit)}")
    
    output_file = 'datasets/features/phiusiil_features.csv'
    all_results = []
    
    print("\nExtracting 200 phishing URLs...")
    phish_results = extract_batch(phishing, 1, max_urls=200, output_csv=output_file)
    all_results.extend(phish_results)
    
    print("\nExtracting 200 legitimate URLs...")
    legit_results = extract_batch(legit, 0, max_urls=200, output_csv=output_file)
    all_results.extend(legit_results)
    
    # Final save
    if all_results:
        pd.DataFrame(all_results).to_csv(output_file, index=False)
        print(f"\n✅ Final: Saved {len(all_results)} rows to {output_file}")
    else:
        print("\n❌ No features extracted. Check network/DNS.")