# Contributing to E-Commerce API

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs
1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Enhancements
1. Check existing issues for similar suggestions
2. Create a new issue describing:
   - The enhancement and its benefits
   - Possible implementation approach
   - Any potential drawbacks

### Pull Requests
1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Write/update tests as needed
5. Update documentation
6. Submit a pull request

## 📝 Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ecommerce-api.git
   cd ecommerce-api
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database**
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Run Tests**
   ```bash
   python manage.py test
   ```

## 💻 Coding Standards

### Python Style Guide
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Django Best Practices
- Use class-based views when appropriate
- Implement proper model validation
- Use Django ORM efficiently (avoid N+1 queries)
- Write comprehensive docstrings
- Use type hints where beneficial

### API Design
- Follow REST principles
- Use appropriate HTTP methods
- Return meaningful status codes
- Provide clear error messages
- Version your APIs when breaking changes

## 🧪 Testing

### Writing Tests
- Write tests for new features
- Update tests for modified features
- Aim for high test coverage
- Test edge cases and error conditions

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test main.tests.ProductAPITestCase

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📄 Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Document complex logic with inline comments
- Update API documentation when endpoints change

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add product review system
fix: resolve stock calculation bug
docs: update API usage guide
refactor: optimize order queries
test: add tests for cart functionality
```

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🔍 Code Review Process

1. All PRs require at least one review
2. Address reviewer comments
3. Ensure CI/CD checks pass
4. Keep PRs focused and reasonably sized
5. Update the PR description with context

## 🚀 Release Process

1. Update version number
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production

## 📋 Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No console warnings or errors
- [ ] Migrations created if models changed
- [ ] Environment variables documented
- [ ] Backwards compatible (or breaking changes documented)

## 💬 Community

- Be respectful and constructive
- Help others when possible
- Follow the Code of Conduct
- Ask questions in discussions

## 📧 Contact

For questions or concerns, please:
- Open an issue
- Start a discussion
- Contact maintainers

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
