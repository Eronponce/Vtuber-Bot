import os
import time

import vlc
from google.cloud import texttospeech_v1beta1 as texttospeech
from twitchio.ext import commands

import creds
from chat import openai_chat_completion


CONVERSATION_LIMIT = 20


def atualizar_status_arquivo(status_da_ia):
    with open("status_da_ia.txt", "w", encoding="utf-8") as status_file:
        status_file.write(status_da_ia)


def synthesize_and_play_audio(ssml_text):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        name="pt-BR-Neural2-C",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    audio_file = os.path.dirname(__file__) + '/output.mp3'
    media = vlc.MediaPlayer(audio_file)
    media.play()

    return response


def generate_ssml_with_marks(text, counter_start=0):
    ssml_text = '<speak>'
    mark_array = []
    response_counter = counter_start

    for i, word in enumerate(text.split(' ')):
        ssml_text += f'<mark name="{response_counter}"/>{word} '
        mark_array.append(word)
        response_counter += 1

    ssml_text = f'{ssml_text.strip()}</speak>'
    return ssml_text, mark_array


class Bot(commands.Bot):
    conversation = list()
    atualizar_status_arquivo("Ia está online")

    def __init__(self):
        Bot.conversation.append({'role': 'system', 'content':
            """Sempre responda em portugues,
            não faça respostas longas,
            seu nome é Iryn,
            não utilize emojis,
            Você é uma mulher,
            você é uma chatbot que esta sendo streamada na twitch plataforma de streaming de jogos,
            não utilize palavras de baixo calão,
              """})
        super().__init__(token=creds.TWITCH_TOKEN, prefix='!', initial_channels=[creds.TWITCH_CHANNEL])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        if len(message.content) > 120 or len(message.content) < 3:
            return
        if not message.content.lower().startswith('iryn'):
            return
        
        atualizar_status_arquivo("Lendo mensagem")
        content = message.content.encode(encoding='ASCII', errors='ignore').decode()
        ssml_text, mark_array = generate_ssml_with_marks(content)
        atualizar_status_arquivo("Enviando mensagem para o google cloud")
        response = synthesize_and_play_audio(ssml_text)
        atualizar_status_arquivo("Processando resposta.")

        with open("output.txt", "a", encoding="utf-8") as out:
            out.write(message.content)

        open('output.txt', 'w').close()
        Bot.conversation.append({'role': 'user', 'content': content})
        atualizar_status_arquivo("enviando mensagem para o openai ")
        response = openai_chat_completion(Bot.conversation)

        if Bot.conversation.count({'role': 'assistant', 'content': response}) == 0:
            Bot.conversation.append({'role': 'assistant', 'content': response})
        if len(Bot.conversation) > CONVERSATION_LIMIT:
            Bot.conversation = Bot.conversation[1:]
            
        ssml_text, mark_array = generate_ssml_with_marks(response)
        atualizar_status_arquivo("Enviando resposta para o google cloud")
        response = synthesize_and_play_audio(ssml_text)

        count = 0
        current = 0
        for i in range(len(response.timepoints)):
            count += 1
            current += 1
            with open("output.txt", "a", encoding="utf-8") as out:
                out.write(mark_array[int(response.timepoints[i].mark_name)] + " ")
            if i != len(response.timepoints) - 1:
                total_time = response.timepoints[i + 1].time_seconds
                time.sleep(total_time - response.timepoints[i].time_seconds)
            if current == 25:
                    open('output.txt', 'w', encoding="utf-8").close()
                    current = 0
                    count = 0
            elif count % 7 == 0:
                with open("output.txt", "a", encoding="utf-8") as out:
                    out.write("\n")
        time.sleep(2)
        open('output.txt', 'w').close()
        Bot.conversation = [{'role': 'system', 'content': Bot.conversation[0]['content']},
                            {'role': 'user', 'content': content}]
        await self.handle_commands(message)


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds.GOOGLE_JSON_PATH
bot = Bot()
bot.run()
