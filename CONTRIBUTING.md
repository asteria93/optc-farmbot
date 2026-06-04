# OPTC Farming Bot - Contributing Guidelines

## Code of Conduct

Please be respectful, inclusive, and follow these guidelines when contributing.

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Write or update tests
5. Commit your changes (`git commit -am 'Add your feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/optc-farmbot.git
cd optc-farmbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python app.py
```

## Code Style

- Use PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Add comments for complex logic
- Keep functions small and focused

## Testing

- Write unit tests for new features
- Run existing tests before submitting PR
- Aim for >80% code coverage
- Use descriptive test names

```bash
python -m pytest tests/ -v --cov=bot --cov-report=html
```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new farming strategy`
- `fix: Correct account creation bug`
- `docs: Update README with new features`
- `refactor: Simplify farming logic`
- `test: Add tests for API routes`

## Pull Request Process

1. Update README.md with any new features
2. Update requirements.txt if adding dependencies
3. Ensure all tests pass
4. Update API.md if changing API endpoints
5. Provide clear description of changes
6. Link related issues

## Reporting Issues

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error logs/stack traces

## Feature Requests

When suggesting features:
- Explain the use case
- Describe how it would work
- Provide examples if possible
- Consider potential impact

## Questions?

Open an issue or discussion for questions and ideas.

Thank you for contributing! 🚀
