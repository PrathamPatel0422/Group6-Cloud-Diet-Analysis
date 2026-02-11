from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os

os.makedirs("simulated_nosql", exist_ok=True)

def process_nutritional_data_from_azurite():
    # Correct way to connect to Azurite
    connect_str = "UseDevelopmentStorage=true"

    blob_service_client = BlobServiceClient.from_connection_string(
        connect_str,
        api_version="2021-08-06"
    )

    container_name = "datasets"
    blob_name = "All_Diets.csv"

    # Create container if it does not exist
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        print("Container created")
    except Exception:
        print("Container already exists")

    blob_client = container_client.get_blob_client(blob_name)

    # Download CSV
    stream = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(stream))

    # Compute averages
    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()

    # Save results (simulated NoSQL)
    result = avg_macros.reset_index().to_dict(orient="records")
    with open("simulated_nosql/results.json", "w") as f:
        json.dump(result, f, indent=4)

    return "Data processed and stored successfully."

if __name__ == "__main__":
    print(process_nutritional_data_from_azurite())
