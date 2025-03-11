import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Living Inventory Management System",
    page_icon="🌱",
    layout="wide"
)

# Initialize session state for inventory
if 'inventory' not in st.session_state:
    if os.path.exists('inventory.json'):
        with open('inventory.json', 'r') as f:
            st.session_state.inventory = json.load(f)
    else:
        st.session_state.inventory = []

def save_inventory():
    with open('inventory.json', 'w') as f:
        json.dump(st.session_state.inventory, f)

def main():
    st.title("🌱 Living Inventory Management System")
    
    # Sidebar for adding new items
    with st.sidebar:
        st.header("Add New Item")
        item_name = st.text_input("Item Name")
        category = st.selectbox(
            "Category",
            ["Plants", "Pets", "Aquatic Life", "Other"]
        )
        quantity = st.number_input("Quantity", min_value=1, value=1)
        price = st.number_input("Price ($)", min_value=0.0, value=0.0, step=0.01)
        care_instructions = st.text_area("Care Instructions")
        
        if st.button("Add Item"):
            new_item = {
                "id": len(st.session_state.inventory) + 1,
                "name": item_name,
                "category": category,
                "quantity": quantity,
                "price": price,
                "care_instructions": care_instructions,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.inventory.append(new_item)
            save_inventory()
            st.success("Item added successfully!")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["View Inventory", "Update Prices", "Analytics"])
    
    with tab1:
        if st.session_state.inventory:
            df = pd.DataFrame(st.session_state.inventory)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                category_filter = st.multiselect(
                    "Filter by Category",
                    options=df['category'].unique()
                )
            with col2:
                search_term = st.text_input("Search by Name")
            
            # Apply filters
            filtered_df = df
            if category_filter:
                filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
            if search_term:
                filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False)]
            
            # Display inventory
            st.dataframe(
                filtered_df,
                column_config={
                    "id": "ID",
                    "name": "Name",
                    "category": "Category",
                    "quantity": "Quantity",
                    "price": st.column_config.NumberColumn(
                        "Price ($)",
                        format="$%.2f"
                    ),
                    "care_instructions": "Care Instructions",
                    "date_added": "Date Added"
                },
                hide_index=True
            )
            
            # Delete item functionality
            item_to_delete = st.selectbox(
                "Select item to delete (by ID)",
                options=[item['id'] for item in st.session_state.inventory]
            )
            if st.button("Delete Selected Item"):
                st.session_state.inventory = [
                    item for item in st.session_state.inventory 
                    if item['id'] != item_to_delete
                ]
                save_inventory()
                st.success("Item deleted successfully!")
                st.rerun()
        
        else:
            st.info("No items in inventory. Add items using the sidebar.")
    
    with tab2:
        st.header("Update Item Prices")
        if st.session_state.inventory:
            df = pd.DataFrame(st.session_state.inventory)
            
            # Select item to update
            item_to_update = st.selectbox(
                "Select item to update (by ID)",
                options=[item['id'] for item in st.session_state.inventory],
                format_func=lambda x: f"ID: {x} - {next((item['name'] for item in st.session_state.inventory if item['id'] == x), '')}"
            )
            
            # Get current price
            current_item = next((item for item in st.session_state.inventory if item['id'] == item_to_update), None)
            if current_item:
                current_price = current_item['price']
                new_price = st.number_input(
                    "New Price ($)",
                    min_value=0.0,
                    value=current_price,
                    step=0.01
                )
                
                if st.button("Update Price"):
                    for item in st.session_state.inventory:
                        if item['id'] == item_to_update:
                            item['price'] = new_price
                    save_inventory()
                    st.success(f"Price updated successfully for {current_item['name']}!")
        else:
            st.info("No items in inventory to update.")
    
    with tab3:
        if st.session_state.inventory:
            df = pd.DataFrame(st.session_state.inventory)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Items by Category")
                category_counts = df['category'].value_counts()
                st.bar_chart(category_counts)
            
            with col2:
                st.subheader("Total Value by Category")
                category_value = df.groupby('category')['price'].sum()
                st.bar_chart(category_value)
            
            st.subheader("Inventory Statistics")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Total Items", df['quantity'].sum())
            with col4:
                st.metric("Total Value", f"${df['price'].sum():.2f}")
            with col5:
                st.metric("Unique Products", len(df))
        
        else:
            st.info("No data available for analytics.")

if __name__ == "__main__":
    main() 