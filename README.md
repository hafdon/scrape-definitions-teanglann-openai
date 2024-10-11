# Irish Language Learning Assistant

This project is an Irish language learning assistant that helps users improve their understanding, vocabulary, pronunciation, and grammar in the Irish language. It uses OpenAI's GPT-4 model to generate simplified definitions of words and BeautifulSoup to scrape definitions from a specified website.

## Setup

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

    Alteratively, export it to the pip environment

    ```bash
    export OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. **Run the main application:**
    ```sh
    python app.py
    ```

2. **Add words to `words.txt`:**
    Add the words you want to get definitions for in the `words.txt` file, one word per line.

3. **Check the output:**
    The simplified definitions will be saved in `output.csv`.

## Logging

Logs are saved in `program.log`. The logging configuration is set up in [`config/logging.py`](config/logging.py).

## Functions

### `get_overview_definition`

Defined in [`utils/openai/get_overview_definition.py`](utils/openai/get_overview_definition.py), this function sends a request to OpenAI's GPT-4 model to get a simplified definition of a word.

### `scrape_definitions`

Defined in [`utils/teanglann/scrape_definitions.py`](utils/teanglann/scrape_definitions.py), this function scrapes definitions from a specified URL using BeautifulSoup.

## Contributing

1. **Fork the repository.**
2. **Create a new branch:**
    ```sh
    git checkout -b feature-branch
    ```
3. **Make your changes and commit them:**
    ```sh
    git commit -m 'Add some feature'
    ```
4. **Push to the branch:**
    ```sh
    git push origin feature-branch
    ```
5. **Create a pull request.**

## License

This project is licensed under the MIT License.