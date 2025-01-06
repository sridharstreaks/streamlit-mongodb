import streamlit as st
from pymongo import MongoClient

# Streamlit App
st.title("MongoDB Atlas Explorer")

# Input MongoDB Connection URI
connection_uri = st.text_input("Enter MongoDB Connection URI", placeholder="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority")

if connection_uri:
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(connection_uri)

        # Access the 'streamlit' database
        db_name = "streamlit"
        if db_name in client.list_database_names():
            db = client[db_name]

            st.success(f"Connected to database: {db_name}")

            # List collections in the database
            collections = db.list_collection_names()
            st.subheader("Collections")
            if collections:
                st.write(collections)

                # Select a collection to view its documents
                selected_collection = st.selectbox("Select a collection to view its documents", collections)
                if selected_collection:
                    collection = db[selected_collection]

                    # Fetch documents
                    documents = list(collection.find())
                    st.subheader(f"Documents in '{selected_collection}' collection")

                    if documents:
                        for doc in documents:
                            st.json(doc)
                    else:
                        st.write("No documents found in this collection.")
            else:
                st.write("No collections found in the database.")
        else:
            st.error(f"Database '{db_name}' not found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
