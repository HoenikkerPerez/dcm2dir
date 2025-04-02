# Contributing to dcm2dir

Thank you for considering contributing to dcm2dir! We welcome contributions from the community and are grateful for your support.

## How to Contribute

### Reporting Issues

If you encounter any issues or have suggestions for improvements, please open an issue on GitHub. Provide as much detail as possible, including steps to reproduce the issue and any relevant logs or screenshots.

### Submitting Pull Requests

1. **Fork the repository**: Click the "Fork" button at the top right corner of the repository page.

2. **Clone your fork**: 
    ```sh
    git clone https://github.com/your-username/dcm2dir.git
    cd dcm2dir
    ```

3. **Create a new branch**: 
    ```sh
    git checkout -b feature/your-feature-name
    ```

4. **Make your changes**: Implement your feature or fix the issue.

5. **Run tests**: Ensure that all tests pass and your changes do not break existing functionality.
    ```sh
    pytest
    ```

6. **Commit your changes**: 
    ```sh
    git add .
    git commit -m "Add feature/fix: your feature or fix description"
    ```

7. **Push to your fork**: 
    ```sh
    git push origin feature/your-feature-name
    ```

8. **Open a pull request**: Go to the original repository and click the "New pull request" button. Provide a clear and descriptive title and description for your pull request.

### Code Style
Please follow the existing code style and conventions used in the project. We use `pylint` for linting. Ensure your code passes linting checks:
```sh
pylint --fail-under=8.5 $(git ls-files '*.py')
```

### Documentation
If your contribution adds or changes functionality, please update the documentation accordingly. This includes updating the `README.md` file and any relevant docstrings.

### License
By contributing to dcm2dir, you agree that your contributions will be licensed under the MIT License.

## Thank You!
We appreciate your contributions and efforts to improve dcm2dir. Thank you for your support!
