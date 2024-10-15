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
            self.logger.debug(f"Raw OpenAI Response: {content}")

            # Parse the JSON response
            structured_data = json.loads(content)
            self.logger.debug(f"Structured Data: {structured_data}")

            adjectives = structured_data.get("adjective_definitions", "")
            verbs = structured_data.get("verb_definitions", "")
            nouns = structured_data.get("noun_definitions", "")
            other = structured_data.get("other", "")

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
                        **General Instructions:**

                        You are an Irish language learning assistant, helping users improve their understanding, vocabulary, pronunciation, and grammar in the Irish language.

                        When provided with a detailed word entry containing definitions in a structured list (e.g., numbered or bullet points), extract and list the key definitions in a simplified, single-line, paragraph-style format. Each definition should include the part of speech followed by a concise definition, separated by a semicolon.

                        Please return the output as structured data in JSON format.

                        **Definition-Specific Instructions:**

                        - Interpret "vt." as "transitive verb" and "vi." as "intransitive verb" based on the context in the definition.
                        - **Do not** include information about other noun forms such as "gs" (genitive singular) or "pl" (plural).
                        - **Do not** include information about the gender of the noun such as "m" (masculine) or "f" (feminine).
                        - The content of the "other" field should include:
                        - Phrases that use common support verbs such as "déan" (do/make), "cuir" (put), "tóg" (take/build), "faigh" (get), "bain" (extract), "téigh" (go), and "tabhair" (give); or "bí" (be) plus a prepositional phrase.
                            - Include the support verb in square brackets at the front of the item.
                            - For example: "(1) [tabhair] thug sé an tomhas go maith dom (he gave me full measure)"
                        - Idiomatic expressions or phrases.
                            - For example: "(In phrase) Ar an toirt, on the spot, immediately."

                        **Special Instructions for Multiple Entries:**

                        If a word has two or more distinct entries (e.g., homonyms), like "teist" below, append Roman numerals (I, II, III, ...) before the definitions and phrases that pertain to each entry.

                        ---

                        **Example 1:**

                        **Input:**

                        ```
                        príosúnach, m. (gs. & npl. -aigh, gpl. príosúnach). Prisoner. príosúnach a dhéanamh de dhuine, to take s.o. prisoner. Fig: príosúnach a dhéanamh den phingin, to keep a tight hold of every penny.
                        ```

                        **Expected Output:**

                        ```json
                        {
                        "word": "príosúnach",
                        "adjective_definitions": "",
                        "verb_definitions": "",
                        "noun_definitions": "(1) prisoner",
                        "other": "(1) príosúnach a dhéanamh de dhuine (to take someone prisoner)"
                        }
                        ```

                        ---

                        **Example 2:**

                        **Input:**

                        ```
                        díomá, f. (gs. díomá). Disappointment, sorrow. díomá a bheith ort, a chur ar dhuine, to be disappointed, to disappoint s.o. Is mór an díomá dó é, it is a great disappointment to him. Is fearr deimhin ná díomá, better be sure than sorry. (Var: diomá)
                        ```

                        **Expected Output:**

                        ```json
                        {
                        "word": "díomá",
                        "adjective_definitions": "",
                        "verb_definitions": "",
                        "noun_definitions": "(1) disappointment; (2) sorrow",
                        "other": "(1) díomá a bheith ort (to be disappointed); (2) is mór an díomá dó é (it is a great disappointment to him)"
                        }
                        ```

                        ---

                        **Example 3 (Multiple Entries):**

                        **Input:**

                        ```
                        teist 1, f. (gs. ~e, pl. ~eanna). 1. Witness, testimony. ~ a thabhairt i rud, to testify to sth. 2. Report, record; recommendation. ~ seirbhíse, service record. ~ agus moladh, recommendation and praise. 3. Reputation, fame. Tá an ~ sin air, he has that reputation. ~ an léinn, reputation for learning. Ba mhór a d~, great was their fame.

                        teist 2, f. (gs. ~e, pl. ~eanna). Test.
                        ```

                        **Expected Output:**

                        ```json
                        {
                        "word": "teist",
                        "adjective_definitions": "",
                        "verb_definitions": "",
                        "noun_definitions": "(I) (1) witness, testimony; (2) report, record, recommendation; (3) reputation, fame. (II) (1) test",
                        "other": "(I) (1) [tabhair] teist a thabhairt i rud (to testify to something); (2) [bí + ar] tá an teist sin air (he has that reputation)"
                        }
                        ```
            
                        """
        user_message = {
            "role": "user",
            "content": definition,
        }

        return [{"role": "system", "content": system_message}, user_message]
