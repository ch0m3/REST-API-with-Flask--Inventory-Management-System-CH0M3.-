from . import commands


def main_menu():
    while True:
        print("\n=== Inventory Management CLI ===")
        print("1. View all inventory")
        print("2. View item details")
        print("3. Add item from barcode (OpenFoodFacts)")
        print("4. Add item manually")
        print("5. Update item stock level (quantity)")
        print("6. Delete item")
        print("7. Find item on API (OpenFoodFacts, no save)")
        print("8. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            commands.list_inventory()
        elif choice == "2":
            commands.view_item_details()
        elif choice == "3":
            commands.add_item_from_barcode()
        elif choice == "4":
            commands.add_item_manual()
        elif choice == "5":
            commands.update_item_stock()
        elif choice == "6":
            commands.delete_item()
        elif choice == "7":
            commands.find_item_on_api()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")