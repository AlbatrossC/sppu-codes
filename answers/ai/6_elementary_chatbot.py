print("Welcome to Customer Service!")
print("You can ask me about store hours, location, or product availability.")
print("Type 'exit' or 'bye' to end the chat.")

while True:
    user_input = input("\nYou: ").lower()

    if "hours" in user_input or "open" in user_input:
        print("Chatbot: Our store is open from 9 AM to 9 PM, Monday to Saturday.")

    elif "location" in user_input or "where" in user_input:
        print("Chatbot: We are located at 123 Main Street, Downtown.")

    elif "product" in user_input or "available" in user_input:
        print("Chatbot: Can you please specify the product you are looking for?")

    elif "hello" in user_input or "hi" in user_input:
        print("Chatbot: Hello! How can I assist you today?")

    elif "thanks" in user_input or "thank you" in user_input:
        print("Chatbot: You're welcome! Is there anything else I can help you with?")

    elif "exit" in user_input or "bye" in user_input:
        print("Chatbot: Thank you for visiting EasyShop! Have a great day!")
        break
    
    else:
        print("Chatbot: I'm sorry, I didn't understand that. Can you please rephrase?")
