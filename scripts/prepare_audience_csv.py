"""
Prepara CSV per Meta Custom Audience dalla lista clienti Forever Living.

Legge clienti_esistenti_TEMPLATE.csv (separatore ;) e genera un CSV
con email, first_name, last_name hashati SHA256 per il caricamento
su Meta Ads Manager.

Uso:
    python scripts/prepare_audience_csv.py [input_csv] [output_csv]

Default:
    input:  files/clienti_esistenti_TEMPLATE.csv
    output: data/meta_audience.csv
"""

import csv
import hashlib
import sys
import os


def sha256_hash(value):
    """Hasha un valore con SHA256 dopo trim e lowercase (requisito Meta)."""
    if not value:
        return ""
    return hashlib.sha256(value.strip().lower().encode('utf-8')).hexdigest()


def split_name(full_name):
    """Divide il nome completo in first_name e last_name."""
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "files/clienti_esistenti_TEMPLATE.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "data/meta_audience.csv"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name = row.get('name', '').strip()
            email = row.get('email', '').strip()
            if not name and not email:
                continue
            first_name, last_name = split_name(name)
            rows.append({
                'email': sha256_hash(email),
                'fn': sha256_hash(first_name),
                'ln': sha256_hash(last_name),
            })

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['email', 'fn', 'ln'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV generato: {output_csv}")
    print(f"Righe: {len(rows)}")
    if len(rows) < 100:
        print(f"ATTENZIONE: Meta richiede minimo 100 contatti per Lookalike. Hai {len(rows)}.")
        print("Aggiungi altri contatti alla lista prima di caricare su Ads Manager.")


if __name__ == "__main__":
    main()
