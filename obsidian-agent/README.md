
# Obsidian Agent

A Python tool that reads your Obsidian vault, summarizes recent observation notes using GPT-4, and generates weekly review files.

## Features

- 📚 **Vault Reading**: Scans your Obsidian vault for observation notes
- 🤖 **AI Analysis**: Uses GPT-4 to summarize notes and generate insights
- 📝 **Weekly Reviews**: Automatically creates structured weekly review files
- ⚙️ **Configurable**: Customizable time periods and vault paths
- 🧪 **Tested**: Includes comprehensive test suite

## Quick Start

### 1. Installation

```bash
# Clone or download the obsidian-agent folder
cd obsidian-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Add your configuration:
```env
OPENAI_API_KEY=your_openai_api_key_here
VAULT_PATH=/path/to/your/obsidian/vault
```

### 3. Vault Structure

Ensure your Obsidian vault has this structure:
```
YourVault/
├── 3-Areas/
│   └── Mind-Body-System/
│       ├── observations/     # Put your observation notes here
│       └── reviews/          # Weekly reviews will be saved here
```

The agent will create missing directories automatically.

### 4. Usage

Generate a weekly review for the last 7 days:
```bash
python run.py summarize
```

Generate a review for the last 30 days:
```bash
python run.py summarize --days 30
```

Generate a review with a specific output date:
```bash
python run.py summarize --output-date 2024-01-15
```

## How It Works

1. **Scan**: The agent scans your `observations/` folder for markdown files modified in the last N days
2. **Read**: Each note is read and parsed (supports frontmatter)
3. **Analyze**: GPT-4 analyzes each note to generate:
   - A concise summary
   - A hypothesis about patterns
   - A follow-up question for deeper investigation
4. **Synthesize**: All analyses are combined into a structured weekly review
5. **Save**: The review is saved as `weekly-review--YYYY-MM-DD.md` in your `reviews/` folder

## Project Structure

```
obsidian-agent/
├── agent/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── vault_reader.py      # Obsidian vault file scanning
│   ├── gpt_client.py        # OpenAI GPT-4 integration
│   ├── summarizer.py        # Note analysis and aggregation
│   └── writer.py            # Review file generation
├── tests/                   # Test suite
├── run.py                   # CLI entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .env.example            # Environment configuration template
```

## Development

### Running Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_vault_reader.py
```

### Code Formatting

```bash
# Format code with black
black agent/ tests/ run.py
```

### Adding New Features

1. **New functionality**: Add modules to the `agent/` package
2. **CLI commands**: Extend `run.py` with new Click commands
3. **Tests**: Add corresponding test files in `tests/`

## Configuration Options

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `VAULT_PATH`: Path to your Obsidian vault (default: `~/Obsidian/Personal-System`)

### Vault Structure Requirements

The agent expects this specific folder structure in your vault:
- `3-Areas/Mind-Body-System/observations/` - where your observation notes are stored
- `3-Areas/Mind-Body-System/reviews/` - where weekly reviews will be saved

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY environment variable is required"**
- Make sure you've created a `.env` file with your API key
- Verify the API key is valid and has sufficient credits

**"Vault path does not exist"**
- Check that the `VAULT_PATH` in your `.env` file points to your actual Obsidian vault
- Use absolute paths for reliability

**"Observations folder not found"**
- Create the required folder structure in your vault
- The agent will create missing directories automatically when writing reviews

**No notes found**
- Check that you have `.md` files in your observations folder
- Verify the files have been modified within your specified time window
- Check file permissions

### Debug Mode

For detailed logging, you can modify the code to add more print statements or use Python's logging module.

## API Usage

The agent uses OpenAI's GPT-4 model. Typical usage:
- ~500 tokens per note for analysis
- Cost depends on the number and length of your notes
- Consider using GPT-4o-mini for lower costs if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is provided as-is for personal use. Modify and extend as needed for your workflow.
