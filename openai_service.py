from openai import OpenAI
import json
from config.logging import setup_logging


class OpenAIService:
    def __init__(self, model="gpt-4o-mini", temperature=0.3, max_tokens=500):
        """
        Sets up logging.
        Initializes the OpenAI client.
        Stores configuration.
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

            structured_data = self._parse_content(content)

            return self._extract_definitions(structured_data)

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

    def _parse_content(self, content: str):
        try:
            structured_data = json.loads(content)
            self.logger.debug(f"Structured Data: {structured_data}")
            return structured_data
        except json.JSONDecodeError as jde:
            self.logger.error(f"JSON decoding failed: {jde}")
            self.logger.debug("Attempting to reprocess content.")
            self.logger.debug(f"Received content: {content}")

            # Attempt to reprocess content by stripping code blocks
            content = self._strip_code_blocks(content)

            try:
                structured_data = json.loads(content)
                self.logger.debug(
                    f"Structured Data after reprocessing: {structured_data}"
                )
                return structured_data
            except json.JSONDecodeError as jde2:
                self.logger.error(f"Reprocessing failed: {jde2}")
                self.logger.debug(f"Final received content: {content}")
                raise  # Re-raise exception to be caught in higher level

    def _strip_code_blocks(self, content: str):
        # Remove code block markers if present
        if content.startswith("```json") and content.endswith("```"):
            content = content[6:-3].strip()
        return content

    def _extract_definitions(self, structured_data):
        adjectives = structured_data.get("adjective_definitions", "")
        verbs = structured_data.get("verb_definitions", "")
        nouns = structured_data.get("noun_definitions", "")
        other = structured_data.get("other_definitions", "")
        error = structured_data.get("error")

        if error:
            self.logger.info(f"OpenAI Self-Reported Error: {error}")

        return adjectives, verbs, nouns, other
