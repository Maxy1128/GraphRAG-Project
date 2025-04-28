import os
import re
import sys
import json
import pandas as pd

def load_definitions():
    # read methodology_typology_def_table.csv
    methodology_typology_df = pd.read_csv(r"KYC_Shell_Company_Indicator_Methodology_Typology_Def_table\methodology_typology_def_table.csv")
    methodology_dict = {}
    typology_dict = {}
    for _, row in methodology_typology_df.iterrows():
        methodology_id = int(row['methodology_id'])
        typology_id = int(row['typology_id'])
        methodology_desc = row['methodology_description']
        typology_desc = row['typology_description']
        # add methodology description
        if methodology_id not in methodology_dict:
            methodology_dict[methodology_id] = methodology_desc

        typology_dict[(methodology_id, typology_id)] = typology_desc

    typology_subtype_df = pd.read_csv(r"KYC_Shell_Company_Indicator_Typology_subtype_def_table\typology_subtype_def_table.csv")
    subtype_desc_dict = {}
    for _, row in typology_subtype_df.iterrows():
        typology_id_type = int(row['typology_id_type'])
        typology_id_subtype = int(row['typology_id_subtype'])
        desc = row['description']
        subtype_desc_dict[(typology_id_type, typology_id_subtype)] = desc

    return methodology_dict, typology_dict, subtype_desc_dict

methodology_dict, typology_dict, subtype_desc_dict = load_definitions()

def extract_ids_from_object(obj, id_pattern):
    result = set()
    if isinstance(obj, list):
        for item in obj:
            result.update(extract_ids_from_object(item, id_pattern))
    elif isinstance(obj, dict):
        for value in obj.values():
            result.update(extract_ids_from_object(value, id_pattern))
    elif isinstance(obj, str):
        s = obj.strip()
        # if the string is a JSON object or array, parse it first
        if (s.startswith('[') and s.endswith(']')) or (s.startswith('{') and s.endswith('}')):
            try:
                parsed = json.loads(s)
                result.update(extract_ids_from_object(parsed, id_pattern))
            except Exception:
                # if JSON parsing fails, treat it as a normal string
                matches = re.findall(id_pattern, s)
                result.update(matches)
        else:
            matches = re.findall(id_pattern, s)
            result.update(matches)
    else:
        # for other types (e.g., int, float), convert to string
        s = str(obj)
        matches = re.findall(id_pattern, s)
        result.update(matches)
    return result


def process_parquet(file_path, start_row, end_row, desc_counter, desc_value):
    """
    Process a Parquet file and generate two columns: Source and Text.

    - read the Parquet file and slice it according to user-defined row range (row numbers start from 1).
    - Source column: file name (without extension).
    - Text column: concatenate all original columns' data into a text segment. The format is:
        For normal columns: #column_name: [data].
        For typology_counter_value_list and typology_value_list, add explanation information:
          #typology_counter_value_list (desc_counter): [data].
          #typology_value_list (desc_value): [data].
    - At the same time, extract IDs from Typology_ID_list and number_of_typology_value columns (format: two uppercase letters followed by 10 digits),
    return the concatenated DataFrame and a set containing all found IDs.
    
    """
    df = pd.read_parquet(file_path)
    
    df = df.iloc[start_row - 1 : end_row]
    
    file_name = os.path.basename(file_path)
    source = "fact_table_m_1_t_1_2_3"
    
    id_set = set()
    id_pattern = r'\b[A-Z]{1,4}\d{6,10}(?:-?[A-Z0-9]+)?\b'
    
    def build_text(row):
        parts = []
        processed_cols = set()

        for col in df.columns:
            if col in processed_cols:
                continue
            
            value = row[col]
            # if current col needs to extract ID, do the matching
            if col in ["bvd_id_number", "typology_id_list", "typology_value_list"]:
                # print("value:", value)
                extracted = extract_ids_from_object(value, id_pattern)
                # print("extracted:", extracted)
                if extracted:
                    new_ids = extracted - id_set
                    id_set.update(new_ids)
            
            if col == 'methodology_id':
                methodology_id_val = int(float(value))
                methodology_desc = methodology_dict.get(methodology_id_val, '')
                col_text = f"{methodology_id_val} ({methodology_desc})" if methodology_desc else str(value)
                parts.append(f"#{col}: {col_text}.")
                processed_cols.add(col)
                
            elif col == 'typology_id':
                methodology_id_val = int(float(row['methodology_id']))
                typology_id_val = int(float(value))
                typology_desc = typology_dict.get((methodology_id_val, typology_id_val), '')
                col_text = f"{typology_id_val} ({typology_desc})" if typology_desc else str(value)
                parts.append(f"#{col}: {col_text}.")
                processed_cols.add(col)
                
            elif col == 'typology_id_type':
                type_val = int(float(value))
                type_desc = "person" if type_val == 1 else "company" 
                parts.append(f"#{col}: {type_val} ({type_desc}).")
                processed_cols.add(col)
                
            elif col == 'typology_id_subtype':
                type_val = int(float(row['typology_id_type']))
                subtype_val = int(float(value))
                subtype_desc = subtype_desc_dict.get((type_val, subtype_val), '')
                col_text = f"{subtype_val} ({subtype_desc})" if subtype_desc else str(value)
                parts.append(f"#{col}: {col_text}.")
                processed_cols.add(col)
                
            else:
                # for cols that need special explanation
                if col == "typology_counter_value_list":
                    if re.search(r"[A-Za-z0-9]", str(value)):
                        parts.append(f"#{col} ({desc_counter}): {value}.")
                elif col == "typology_value_list":
                    parts.append(f"#{col} ({desc_value}): {value}.")
                else:
                    parts.append(f"#{col}: {value}.")
                processed_cols.add(col)

        return " ".join(parts)
    

    df["Text"] = df.apply(build_text, axis=1)
    df["Source"] = source
    
    new_df = df[["Source", "Text"]]
    
    return new_df, id_set

def main():
    # the input file path that needs to be processed
    input_file = r"fact_table_m_1_t_1_2_3\part-00026-313215ac-e747-4f1b-9e71-056cbe3b8a76-c000.snappy.parquet"


    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist, please check the path and try again.")
        sys.exit(1)
    
    try:
        start_row = 1
        end_row = 10
        if start_row < 1 or end_row < start_row:
            print("The row number input is invalid.")
            sys.exit(1)
    except ValueError:
        print("Please enter a valid integer row number.")
        sys.exit(1)
    
    # Add description for typology_counter_value_list and typology_value_list
    # desc_counter = input("请输入 typology_counter_value_list 的说明：").strip()
    # desc_value = input("请输入 typology_value_list 的说明：").strip()
    desc_counter = input("Please enter the description for typology_counter_value_list: ").strip()
    desc_value = input("Please enter the description for typology_value_list: ").strip()

    output_csv = "SCI_data.csv"
    
    # text file to save the extracted IDs
    output_txt = "entity_ids_1_1_1.txt"
    
    try:
        new_df, id_set = process_parquet(input_file, start_row, end_row, desc_counter, desc_value)
        
        # if the output CSV file does not exist, create it and write the header
        write_header = not os.path.exists(output_csv)
        new_df.to_csv(output_csv, mode='a', header=write_header, index=False, encoding="utf-8-sig")
        print(f"Processed data has been saved to {output_csv}")
        
        # read existing IDs from the text file
        existing_ids = set()
        if os.path.exists(output_txt):
            with open(output_txt, "r", encoding="utf-8") as f:
                for line in f:
                    existing_ids.add(line.strip())
        
        # find new IDs that are not in the existing IDs
        new_ids = id_set - existing_ids
        if new_ids:
            with open(output_txt, "a", encoding="utf-8") as f:
                for id_ in new_ids:
                    f.write(id_ + "\n")
            print(f"New IDs extracted and saved to {output_txt}")
        else:
            print("No new IDs found.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
