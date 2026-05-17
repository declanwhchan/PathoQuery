import os
from pymilvus import connections, utility, Collection

# Connection details from environment variables
HOST = os.getenv("MILVUS_HOST", "9ef527dc-23ef-43e3-930c-7d4687c7129f.wxd.cva7rjed0mvr6khqeoc0.lakehouse.ibmappdomain.cloud")
PORT = int(os.getenv("MILVUS_PORT", "443"))
USER = os.getenv("MILVUS_USER", "ibmlhapikey")
PASSWORD = os.getenv("MILVUS_PASSWORD", "ahaha")
CERT_PATH = os.getenv("MILVUS_SERVER_PEM_PATH", None)

# Connect to Milvus
print("Connecting to IBM watsonx.data Milvus...")
print(f"Host: {HOST}")
print(f"Port: {PORT}")

connect_kwargs = {
    "alias": "default",
    "host": HOST,
    "port": PORT,
    "user": USER,
    "password": PASSWORD,
    "secure": True
}
if CERT_PATH:
    connect_kwargs["server_pem_path"] = CERT_PATH

connections.connect(**connect_kwargs)

print("✓ Connected successfully!\n")

# List all collections
print("Collections in Milvus:")
print("-" * 50)

collections = utility.list_collections()

if collections:
    for i, collection_name in enumerate(collections, 1):
        print(f"{i}. {collection_name}")
        
        # Get collection stats
        try:
            col = Collection(collection_name)
            col.load()
            row_count = col.num_entities
            print(f"   Entities: {row_count}")
        except Exception as e:
            print(f"   Entities: Unable to retrieve")
        print()
else:
    print("No collections found.")

print("-" * 50)
print(f"Total collections: {len(collections)}")

# Disconnect
connections.disconnect("default")
print("\n✓ Disconnected")