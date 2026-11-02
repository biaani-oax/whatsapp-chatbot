from app.llm import MODEL, generate_response # type: ignore


def main():

    conversation = []

    print(f"Biaani Chatbot. Usando el modelo {MODEL}.\n")
    print("Escribe 'salir' para terminar.\n")

    while True:

        user_message = input("Tú: ")

        if user_message.lower() == "salir":
            break

        conversation.append({ # type: ignore
            "role": "user",
            "content": user_message
        })

        answer = generate_response(conversation)

        conversation.append({ # type: ignore
            "role": "assistant",
            "content": answer
        })

        print(f"\nBiaani: {answer}\n")


if __name__ == "__main__":
    main()
