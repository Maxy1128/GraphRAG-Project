import os
import glob
import pandas as pd

def main():
    subtype_descriptions = {
        '4': 'global ultimate owner (UBO/GUO)',
        '2': 'previous board of director',
        '1': 'current board of director',
        '3': 'beneficial owner (BO)',
        '0': 'company',
        '5': 'shareholder'
    }

    id_file = "txt file path that stores extracted entity IDs"
    if not os.path.exists(id_file):
        print(f"File {id_file} does not exist, please check the file path.")
        return

    with open(id_file, "r", encoding="utf-8") as f:
        target_ids = set(line.strip() for line in f if line.strip())
    
    if not target_ids:
        print("No IDs were read from the file.")
        return

    print(f"Total of {len(target_ids)} target IDs read.")

    # 2. Traverse all parquet files in the entity_table folder
    folder = "entity_table"
    if not os.path.isdir(folder):
        print(f"Folder {folder} does not exist, please check the path!")
        return

    parquet_files = glob.glob(os.path.join(folder, "*.parquet"))
    if not parquet_files:
        print(f"No parquet files found in folder {folder}.")
        return

    output_rows = []  # For storing output results

    # Traverse all parquet files
    for file in parquet_files:
        try:
            df = pd.read_parquet(file)
        except Exception as e:
            print(f"Error occurred while reading file {file}: {e}")
            continue

        # Check if "entities_id" column exists in the file
        if "entities_id" not in df.columns:
            print(f"File {file} does not contain 'entities_id' column, skipping.")
            continue

        # Filter rows where entities_id is in the target ID set
        matched_df = df[df["entities_id"].isin(target_ids)]
        if matched_df.empty:
            continue

        # Concatenate all column data for each row
        for _, row in matched_df.iterrows():
            # Modified text generation logic: add description for typology_id_subtype
            parts = []
            for col in df.columns:
                if col == "typology_id_subtype":
                    subtype = str(row[col])  # Force convert to string
                    desc = subtype_descriptions.get(subtype, "unknown")
                    parts.append(f"#{col}: {subtype} ({desc}).")
                else:
                    parts.append(f"#{col}: {row[col]}.")
            text = " ".join(parts)
            
            output_rows.append({"Source": "entity_table", "Text": text})
            # Remove found IDs (if the same ID appears in multiple files, only record once)
            id_val = row["entities_id"]
            if id_val in target_ids:
                target_ids.remove(id_val)

    # 4. If there are unmatched IDs, print them
    if target_ids:
        print("The following IDs were not found in any files:")
        for missing_id in target_ids:
            print(missing_id)
    else:
        print("All target IDs have been found in the files.")

    # 5. Write matched results to a new CSV file (two columns: Source and Text)
    output_csv = "usecase.csv"
    if not output_csv:
        output_csv = "usecase.csv"
    
    output_df = pd.DataFrame(output_rows, columns=["Source", "Text"])
    
    # Append if file exists, otherwise create new
    if os.path.exists(output_csv):
        output_df.to_csv(output_csv, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        output_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    
    print(f"Processing completed, results saved to {output_csv}")

if __name__ == "__main__":
    main()