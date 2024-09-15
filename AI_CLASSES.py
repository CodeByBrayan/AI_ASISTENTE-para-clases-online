import os
import pyaudio
import wave
import speech_recognition as sr
from groq import Groq
import keyboard
import threading
import time
from colorama import Fore, Style, init
init(autoreset=True)
# Configura el cliente de Groq con tu API Key, debes crear una cuenta y crear una API, groq es barato e incluye llama 3
client = Groq(
    api_key="AQUI_VA_TU_API_GROQ"
)
is_recording = False
messages = []
WAVE_OUTPUT_FILENAME = "record.wav"

def record_audio():
    global is_recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("\n¡Grabación iniciada! Habla ahora...")
    print("Presiona Shift derecho nuevamente para detener la grabación.")
    frames = []
    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)
    print("\nGrabación finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    if frames:  # Solo guarda el archivo si se grabó algo
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return True
    return False
def transcribe_audio():
    if not os.path.exists(WAVE_OUTPUT_FILENAME):
        print(f"El archivo {WAVE_OUTPUT_FILENAME} no existe.")
        return ""
    r = sr.Recognizer()
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="es-ES")
        print(f"\n{Fore.YELLOW}Mensaje transcrito:{Style.RESET_ALL} {text}")
        return text
    except sr.UnknownValueError:
        print(f"\n{Fore.RED}No se pudo transcribir el audio. Por favor, intenta de nuevo.{Style.RESET_ALL}")
        return ""
    except Exception as e:
        print(f"\n{Fore.RED}Error durante la transcripción: {e}{Style.RESET_ALL}")
        return ""
def format_bot_response(response):
    lines = response.split('\n')
    formatted = []
    formatted.append(f"{Fore.GREEN}Negro11:{Style.RESET_ALL}")
    # Añade cada línea del mensaje a la lista formateada
    for line in lines:
        formatted.append(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
    return '\n'.join(formatted)
def process_input(user_input):
    global messages
    messages.append({"role": "user", "content": user_input})
    # Imprime la pregunta del usuario antes de la respuesta del bot
    print(f"\n{Fore.YELLOW}Tú:{Style.RESET_ALL} {user_input}")
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192" #aqui ponen algun modelo que quieran usar, este es el mas barato
        )
        response = chat_completion.choices[0].message.content
        formatted_response = format_bot_response(response)
        # Imprime el mensaje formateado
        print(formatted_response)
        messages.append({"role": "assistant", "content": response})
    except Exception as e:
        print(f"\n{Fore.RED}Ocurrió un error:{Style.RESET_ALL} {e}")
def toggle_recording():
    global is_recording
    is_recording = not is_recording
    if is_recording:
        threading.Thread(target=record_audio).start()
    else:
        time.sleep(0.5)  # Espera un poco para asegurar que la grabación ha terminado
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            user_input = transcribe_audio()
            if user_input:
                process_input(user_input)
        else:
            print(f"\n{Fore.RED}No se pudo crear el archivo de audio. Por favor, intenta de nuevo.{Style.RESET_ALL}")
    # Muestra el prompt "Tú:" después de procesar el audio, sino les gusta pueden eliminarlo
    if not is_recording:
        print(f"\n{Fore.YELLOW}Tú:{Style.RESET_ALL}", end=" ")
def iniciar_chat():
    global is_recording
    print(f"{Fore.MAGENTA}Bienvenido al Chat AI. Escribe 'salir' para terminar.{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Presiona Shift derecho para comenzar/detener la grabación de voz.{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Puedes escribir en cualquier momento para enviar un mensaje de texto.{Style.RESET_ALL}")

    keyboard.on_press_key("right shift", lambda _: toggle_recording(), suppress=True)
    while True:
        if not is_recording:  # Solo muestra el prompt cuando no está grabando
            user_input = input(f"\n{Fore.YELLOW}Tú:{Style.RESET_ALL} ")
            if user_input.lower() == 'salir':
                print(f"{Fore.GREEN}Chat terminado.{Style.RESET_ALL}")
                break
            if user_input:
                process_input(user_input)
        else:
            # Durante la grabación, no hace nada aquí, XDDD
            pass
if __name__ == "__main__":
    iniciar_chat()
