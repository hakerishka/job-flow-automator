# 🤝 Contributing to Job-Flow Automator

Thank you for your interest in contributing to **Job-Flow Automator**! We welcome contributions from the community.

---

## 🛠️ Development Workflow

1. **Fork and Clone the Repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/job-flow-automator.git
   cd job-flow-automator
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies (including Dev Tools):**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Run the Test Suite:**
   ```bash
   pytest
   ```

---

## 🧪 Testing Guidelines

* Write unit tests in `tests/` for any new features or bug fixes.
* Ensure all tests pass before submitting a pull request:
  ```bash
  pytest tests/ -v
  ```

---

## 📐 Code Style & Formatting

* We follow PEP 8 standards with a 120-character line limit.
* Format code with `black`:
  ```bash
  black .
  ```

---

## 📄 Submitting a Pull Request (PR)

1. Create a feature branch: `git checkout -b feature/your-feature-name`.
2. Commit your changes with clear, descriptive commit messages.
3. Push to your branch and open a Pull Request against `main`.
