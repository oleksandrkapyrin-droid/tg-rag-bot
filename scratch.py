# a = '12345'

# for i in len(a):
#     print(a[i])
user_history = {}
system_prompt = {'role': 'system', 'content': 'Ти корисний та розумний асистент. Відповідай українською мовою.'}
chat_id = 1
user_history[chat_id] = []
user_history[chat_id].append({"role": "user",})
message_for_groq = [system_prompt] + user_history[chat_id]

print(user_history)
print(message_for_groq)