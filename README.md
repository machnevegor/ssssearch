# Static Site Semantic Search

Static Site Semantic Search (ssssearch) is a universal tool for implementing
semantic search on static websites. It combines web scraping, AI-powered natural
language processing, and efficient indexing to provide advanced search
capabilities for any structured website.

The tool is designed for flexibility**: simply configure the root URL and the
system will crawl, index, and analyze the target site. It uses FAISS for
indexing and Google Generative AI for intelligent query handling, making it
ideal for educational, research, or documentation repositories.

For demonstration purposes, the project indexes and searches the
[Eduwiki knowledge base](https://eduwiki.innopolis.university/index.php/Main_Page)
at Innopolis University, demonstrating its potential to process and retrieve
meaningful answers from domain-specific knowledge bases.

## Features

### Universal Web Scraper

- **Configurable Root URL**: Adapt the bot for any website by updating the root
  URL in the configuration.
- **Recursive Crawling**: Automatically traverses all pages linked within the
  domain, ensuring thorough coverage.
- **Full Indexing**: Collects and structures all text-based content from the
  target website for optimal searchability.
- **Progress Monitoring**: Displays a real-time progress bar during the scraping
  process.

### AI-Powered Semantic Search

- **Natural Language Understanding**: Supports semantic query resolution for
  user-friendly and accurate responses.
- **AI Model**: Utilizes Google’s Gemini model to analyze user queries and
  deliver concise answers.
- **Source References**: Cites original content sources to enhance reliability
  and transparency.

### Telegram Bot Integration

- **Seamless Interaction**: Users can query the bot using natural language and
  receive immediate, AI-generated responses.
- **Admin Notifications**: Alerts the admin once the scraping and indexing
  process is complete, indicating the bot is ready for queries.

## Usage

### Prerequisites

- Python 3.12
- Telegram Bot Token (from BotFather)
- Google API Key with access to the Gemini model
- Poetry (install via pip install poetry)

### Steps

1. Install the dependencies using Poetry:

   ```bash
   poetry install
   ```

2. Create a `.env` file and set the required environment variables:

   ```bash
   TELEGRAM_TOKEN=<your-telegram-bot-token>
   TELEGRAM_ADMIN=<your-telegram-id>
   GOOGLE_API_KEY=<your-google-api-key>
   ```

3. Run the Application

   ```bash
   poetry run python main.py
   ```

## Planned Enhancements

- **Multi-Domain Support**: Enable indexing of multiple domains simultaneously.
- **Advanced Query Features**: Support filtering, sorting, and complex queries.
- **UI Improvements**: Develop a web-based interface alongside the Telegram bot.
- **Analytics**: Integrate query logging and analytics for user behavior
  insights.
