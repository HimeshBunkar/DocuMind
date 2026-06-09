from google import genai

client = genai.Client(
    api_key="AQ.Ab8RN6L460NHmK-F3DPMQPfBgwxI2j9N54-X5ikZUgjbc_icYQ"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello"
)

print(response.text)