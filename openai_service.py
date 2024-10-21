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

    def get_overview_definition(self, definition: str, instructions: str):
        """
        Handles the API call and processes the response.
        Logs relevant information.
        """
        try:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_message(definition, instructions),
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
            other = structured_data.get("other_definitions", "")
            error = structured_data.get("error")

            if error:
                self.logger.info(f"OpenAI Self-Reported Error: {error}")

            return (adjectives, verbs, nouns, other)
        except json.JSONDecodeError as jde:
            self.logger.error(f"JSON decoding failed {jde}")
            self.logger.debug(f"Received content {content}")

            # Step 1: Split the response into lines
            lines = structured_data.strip().split("\n")

            # Step 2: Remove the first and last lines (the backticks)
            json_lines = lines[1:-1]

            # Step 3: Join the remaining lines back into a single string
            json_str = "\n".join(json_lines)

            # Step 4: Parse the JSON string into a Python dictionary
            data = json.loads(json_str)

            # Now, `data` is a Python dictionary
            print(data)

            adjectives = data.get("adjective_definitions", "")
            verbs = data.get("verb_definitions", "")
            nouns = data.get("noun_definitions", "")
            other = data.get("other_definitions", "")
            error = data.get("error")

            if error:
                self.logger.info(f"OpenAI Self-Reported Error: {error}")

            return (adjectives, verbs, nouns, other)

        except Exception as e:
            self.logger.error(f"Error with OpenAI API: {e}")
            return None

    def _build_message(self, definition, instructions):
        user_message = {
            "role": "user",
            "content": definition,
        }

        return [
            {"role": "system", "content": instructions},
            user_message,
        ]
