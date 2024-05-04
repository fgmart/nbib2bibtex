# fred.martin@utsa.edu and OpenAI
#
# result of a collaboration with ChatGPT
#
# see entire process at:
# https://chat.openai.com/share/c45a2450-1b7a-4e66-9fc1-8c52e8932d43
#
# run with python3

import re

def parse_nbib_file(nbib_filename):
    # Read the nbib file
    with open(nbib_filename, 'r', encoding='utf-8') as nbib_file:
        nbib_data = nbib_file.read()

    # Split data into records based on PubMed record separator
    records = re.split(r'\n{2,}', nbib_data.strip())
    parsed_entries = []
    skipped_count = 0

    # Parse each record
    for record in records:
        entry = {}

        # Extract OID (citation key)
        match_oid = re.search(r'OID\s+-\s+(\S+)', record)
        if match_oid:
            entry['key'] = match_oid.group(1)
        else:
            skipped_count += 1
            print(f"Skipping entry (missing OID): {record[:100]}...")
            continue

        # Extract authors (if present)
        match_authors = re.findall(r'AU  - (.+)', record)
        if match_authors:
            entry['authors'] = ' and '.join(match_authors)
        else:
            entry['authors'] = "author missing"  # Default author if none found

        # Extract other fields
        fields_to_extract = ['TI', 'JT', 'DP', 'AB', 'VI', 'IP', 'PG', 'OT']
        for field in fields_to_extract:
            match_field = re.findall(fr'{field}\s+-\s+(.+)', record)
            if match_field:
                if field.lower() == 'ot':
                    # Concatenate multiple lines of OT into a single string with commas
                    entry['keywords'] = ', '.join(match_field)
                else:
                    entry[field.lower()] = match_field[0]

        # Check if all essential fields (key, ti, ab) are present
        if all(key in entry for key in ['key', 'ti', 'ab']):
            parsed_entries.append(entry)
        else:
            skipped_count += 1
            print(f"Skipping entry (missing essential fields): {entry}")

    print(f"Total entries skipped: {skipped_count}")
    return parsed_entries

def write_bibtex_file(entries, output_filename):
    # Write BibTeX entries to output file
    with open(output_filename, 'w', encoding='utf-8') as bibtex_file:
        for entry in entries:
            # Check if all required fields (key, ti, ab) are present
            required_fields = ['key', 'ti', 'ab']
            if all(key in entry for key in required_fields):
                bibtex_entry = f"@article{{{entry['key']},\n"
                
                # Include authors (default "author missing" if not specified)
                bibtex_entry += f"  author = {{{entry['authors']}}},\n"
                
                bibtex_entry += f"  title = {{{entry['ti']}}},\n"
                
                # Include journal if present
                if 'jt' in entry:
                    bibtex_entry += f"  journal = {{{entry['jt']}}},\n"
                
                bibtex_entry += f"  year = {{{entry['dp']}}},\n"
                bibtex_entry += f"  abstract = {{{entry['ab']}}},\n"
                
                # Include optional fields
                if 'vi' in entry:
                    bibtex_entry += f"  volume = {{{entry['vi']}}},\n"
                if 'ip' in entry:
                    bibtex_entry += f"  number = {{{entry['ip']}}},\n"
                if 'pg' in entry:
                    bibtex_entry += f"  pages = {{{entry['pg']}}},\n"
                if 'keywords' in entry:
                    bibtex_entry += f"  keywords = {{{entry['keywords']}}}\n"

                bibtex_entry += "}"  # Close BibTeX entry
                bibtex_file.write(bibtex_entry + '\n\n')
            else:
                print(f"Skipping entry (missing essential fields): {entry}")

    print(f"BibTeX file '{output_filename}' has been created.")

# Example usage
if __name__ == "__main__":
    nbib_filename = input("Enter the filename of the nbib file: ")
    output_filename = input("Enter the output BibTeX filename: ")

    # Parse nbib file
    parsed_entries = parse_nbib_file(nbib_filename)

    # Write BibTeX file
    write_bibtex_file(parsed_entries, output_filename)
