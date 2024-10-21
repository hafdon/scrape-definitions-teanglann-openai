import csv
import os

from config.logging import setup_logging

# from utils.openai.get_overview_definition import get_overview_definition
# from utils.teanglann.scrape_definitions import scrape_definitions
from openai_service import OpenAIService
from web_scraper_service import WebScraperService


logger = setup_logging()


def read_markdown_file(file_path):
    """
    Reads the content of a Markdown file and returns it as a string.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        str: The content of the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
        return markdown_content
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def main():

    openai_service = OpenAIService(model="gpt-4o-mini", max_tokens=1000)
    web_scraper_service = WebScraperService()

    base_url = "https://www.teanglann.ie/en/fgb"
    urls = []
    words = []

    try:
        # Read words and construct URLs
        with open("words.txt", "r", encoding="utf-8") as file:
            for line in file:
                word = line.strip()
                if word:
                    words.append(word)
                    urls.append(f"{base_url}/{word}")
        logger.info(f"Loaded {len(words)} words from words.txt")
    except FileNotFoundError:
        logger.critical("The file 'words.txt' was not found.")
        return
    except Exception as e:
        logger.critical(f"An error occurred while reading 'words.txt': {e}")
        return

    # List to hold final data
    final_data = []

    try:
        # Iterate over each word and its corresponding URL
        for word, url in zip(words, urls):
            try:
                logger.info(f"Processing word: {word}")
                definition = web_scraper_service.scrape_definitions(url, word)
                if not definition:
                    logger.warning(f"Skipping word '{word}' due to extraction failure.")
                    continue

                instructions = read_markdown_file("instructions.md")

                # Ensure get_overview_definition returns a tuple
                overview = openai_service.get_overview_definition(
                    definition, instructions
                )
                if not overview:
                    logger.warning(
                        f"Skipping word '{word}' because get_overview_definition returned None."
                    )
                    continue

                # Attempt to unpack the overview
                try:
                    adjectives, verbs, nouns, other = overview
                except TypeError as te:
                    logger.error(f"Error unpacking overview for word '{word}': {te}")
                    continue

                # Append to final data
                final_data.append(
                    {
                        "word": word,
                        "adjectives": adjectives,
                        "verbs": verbs,
                        "nouns": nouns,
                        "other": other,
                    }
                )
                logger.info(f"Added definitions for word '{word}'")
            except Exception as e:
                logger.error(f"An error occurred while processing word '{word}': {e}")
                continue  # Continue with the next word

    except KeyboardInterrupt:
        logger.info("Process interrupted by user. Saving data collected so far.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during processing: {e}")
    finally:
        if final_data:
            # Export to CSV
            csv_filename = "output.csv"

            try:
                with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
                    fieldnames = [
                        "word",
                        "adjectives",
                        "verbs",
                        "nouns",
                        "other",
                    ]

                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for entry in final_data:
                        writer.writerow(entry)

                logger.info(f"Data successfully exported to {csv_filename}")
            except Exception as e:
                logger.error(
                    f"An error occurred while writing to '{csv_filename}': {e}"
                )
        else:
            logger.warning("No data to export.")


if __name__ == "__main__":
    main()
