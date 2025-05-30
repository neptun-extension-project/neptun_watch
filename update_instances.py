import requests
import json


def create_markdown_table(headers, data):
    # Calculate the maximum width for each column
    col_widths = [max(len(str(row[i])) for row in [headers] + data) for i in range(len(headers))]
    
    # Create the header row
    header = "| " + " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers))) + " |"
    
    # Create the separator row with hyphens
    separator = "|" + "|".join(f":{'-' * (col_widths[i] - 1)}" for i in range(len(headers))) + "|"
    
    # Create the data rows
    rows = [
        "| " + " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row))) + " |"
        for row in data
    ]
    
    # Combine all parts of the table
    return "\n".join([header, separator] + rows)

with open('instances.txt') as file:
    instances = [line.strip() for line in file.readlines()]

table_data = []
neptuns_by_name = {}
headers = ["URL", "Version", "Generation Date", "Organization Name", "Captcha Required"]

for url in instances:
    try:
        response = requests.get(url + 'api/General/GetEnvironmentData', timeout=60)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()['data']
        org_name = data['organizationData']['organizationName']
        table_data.append([
            url,
            data['version'],
            data['generationDate'],
            org_name,
            str(data['captchaRequired'])
        ])
        properties = {"url": url, "server_name": data['serverName']}
        if org_name not in neptuns_by_name:
            neptuns_by_name[org_name] = [properties]
        else:
            neptuns_by_name[org_name].append(properties)
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching data for {url}: {str(e)}")
        table_data.append([url, "N/A", "N/A", "N/A", "N/A"])

markdown_table = create_markdown_table(headers, table_data)
with open("server_data.json", "w") as f:
    json.dump(neptuns_by_name, f, indent=4)

with open('README.md', 'w') as file:
    file.write("# Új Neptun szerverek adatai\n\n")
    file.write("Itt egy naponta frissülő listát találsz, ami az új Neptun szerverek verzióit és pár metaadatát követi.\n\n")
    file.write(markdown_table)

print("Markdown table has been written to README.md")
