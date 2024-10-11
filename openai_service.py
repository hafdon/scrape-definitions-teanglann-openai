from openai import OpenAI
import json
from config.logging import setup_logging


class OpenAIService:
    def __init__(self, model="gpt-4o-mini", temperature=0.3, max_tokens=500):
        """
        Sets up logging.
        Initializes the OpenAI client.
        Stores configuration
        """
        self.logger = setup_logging()
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_overview_definition(self, definition):
        """
        Handles the API call and processes the response.
        Logs relevant information.
        """
        try:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_message(definition),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            content = completion.choices[0].message.content.strip()
            self.logger.debug(f"Raw OpenAI Respons: {content}")

            # Parse the JSON response
            structured_data = json.loads(content)
            self.logger.debug(f"Structured Data: {structured_data}")

            adjectives = structured_data.get("adjective_definitions", "")
            verbs = structured_data.get("verb_definitions", "")
            nouns = structured_data.get("noun_definitions", "")
            other = structured_data.get("other_definitions", "")

            return (adjectives, verbs, nouns, other)
            pass
        except json.JSONDecodeError as jde:
            self.logger.error(f"JSON decoding failed {jde}")
            self.logger.debug(f"Received content {content}")
            return None
        except Exception as e:
            self.logger.error(f"Error with OpenAI API: {e}")
            return None

    def _build_message(self, definition):
        """
        Separates the message construction logic,
        """
        system_message = """
            You are an Irish language learning assistant, helping users improve their understanding, vocabulary, pronunciation, and grammar in the Irish language.

            When provided with a detailed word entry containing definitions in a structured list (e.g., numbered or bullet points), extract and list the key definitions in a simplified single-line, paragraph-style format. Each definition should include the part of speech followed by a concise definition, separated by a semicolon.
            
            Please return this as structured data. (Note: "vt." and "vi." stand for "transitive verb" and "intransitive verb" respectively. This information can typically be found in the definition.)
            
            example:                    
            {"word":"doicheallach","adjective_definitions":"(1) churlish, inhospitable","verb_definitions":" vt. vi. (1) to be unwilling to receive someone; (2) to be churlish with someone; (3) to be grudging with something, unwilling to do something","noun_definitions":"(1) churlish, cold welcome; (2) grudging word, smile","other":"(phrase) he gave it grudgingly; (phrase) he is stand-offish in company."}
            """
        user_message = {
            "role": "user",
            "content": definition,
        }

        return [{"role": "system", "content": system_message}, user_message]
