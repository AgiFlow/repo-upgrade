from functools import lru_cache
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from langchain.llms import Ollama
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class Models:
    @lru_cache
    @staticmethod
    def get():
        if os.environ.get('AZURE_OPENAI_API_KEY'):
            return Models.azure()
        if os.environ.get('OLLAMA_MODEL'):
            return Models.ollama()
        if os.environ.get('OPENAI_MODEL'):
            return Models.openai()

    @lru_cache
    @staticmethod
    def azure():
        os.environ['OPENAI_API_VERSION'] = os.environ.get('AZURE_OPENAI_API_VERSION')
        return AzureChatOpenAI(
            openai_api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            openai_api_version=os.environ.get('AZURE_OPENAI_API_VERSION'),
            azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT'),
            azure_deployment=os.environ.get('AZURE_DEPLOYMENT'),
        )

    @lru_cache
    @staticmethod
    def ollama():
        return Ollama(
            model=os.environ.get('OLLAMA_MODEL')
        )

    @lru_cache
    @staticmethod
    def openai():
        return ChatOpenAI(
            model=os.environ.get('OPENAI_MODEL', ''),
            api_key=os.environ.get('OPENAI_API_KEY')
        )
