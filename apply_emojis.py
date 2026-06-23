import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "docs = [row['Supernumerary'] for _, row in date_shifts.iterrows()]" in line:
        lines[i] = """                docs = []
                for _, row in date_shifts.iterrows():
                    name = row['Supernumerary']
                    clasif = row.get('Classification', 'Secuencia Normal')
                    obs = str(row.get('Observation', '')) if pd.notna(row.get('Observation')) else ''
                    
                    personal_obs = ""
                    if not df_super.empty:
                        doc_match = df_super[df_super['NOMBRES Y APELLIDOS'] == name]
                        if not doc_match.empty:
                            personal_obs = str(doc_match.iloc[0].get('OBSERVACIONES', '')).strip()
                            
                    display_name = name
                    if "Compensación" in str(clasif):
                        display_name += " 🟡(COMP)"
                    elif obs or personal_obs:
                        display_name += " 💬"
                        
                    docs.append(display_name)
"""
        break

for i, line in enumerate(lines):
    if "old_row = df_shifts[(df_shifts['Date'] == old_date) & (df_shifts['Supernumerary'] == moved_doc)].iloc[0]" in line:
        lines[i] = """                        # Remove emojis to get raw name
                        raw_name = moved_doc.split(" 🟡")[0].split(" 💬")[0]
                        old_row = df_shifts[(df_shifts['Date'] == old_date) & (df_shifts['Supernumerary'] == raw_name)].iloc[0]
"""
        break

for i, line in enumerate(lines):
    if "if not new_date_shifts.empty and moved_doc in new_date_shifts['Supernumerary'].values:" in line:
        lines[i] = """                        if not new_date_shifts.empty and raw_name in new_date_shifts['Supernumerary'].values:
"""
        break

for i, line in enumerate(lines):
    if "original_name=moved_doc," in line:
        lines[i] = "                            original_name=raw_name,\n"

for i, line in enumerate(lines):
    if "supernumerary_name=moved_doc," in line:
        lines[i] = "                            supernumerary_name=raw_name,\n"

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Emojis applied successfully!")
