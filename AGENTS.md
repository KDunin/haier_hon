# Agent Guidelines for haier_hon

This repository contains the Home Assistant integration for Haier hOn appliances.
Follow these guidelines to ensure code consistency, quality, and maintainability.

## 1. Development Environment & Commands

### Setup
Install development dependencies:
```bash
pip install -r requirements_dev.txt
```

### Build & Linting
Run these commands to verify your changes. All checks must pass.

*   **Formatting (Black):**
    ```bash
    black .
    ```
*   **Linting (Flake8):**
    ```bash
    flake8 .
    ```
*   **Type Checking (MyPy):**
    ```bash
    mypy .
    ```
    *Note: MyPy is configured with strict settings in `mypy.ini`.*
*   **Linting (Pylint):**
    ```bash
    pylint custom_components/hon
    ```

### Testing
*   **Translation Keys:**
    ```bash
    python3 scripts/check.py
    ```
*   **Logging:**
    ```bash
    python3 scripts/test_logging.py
    ```

## 2. Code Style & Conventions

### Formatting
*   **Style:** We use [Black](https://github.com/psf/black) code formatter.
*   **Line Length:** Default (88 chars).
*   **Indentation:** 4 spaces.

### Imports
Organize imports in the following order:
1.  **Standard Library** (e.g., `import logging`, `from dataclasses import dataclass`)
2.  **Third-Party / Home Assistant** (e.g., `from homeassistant.core import HomeAssistant`, `import voluptuous as vol`)
3.  **Local Application** (e.g., `from .const import DOMAIN`, `from .entity import HonEntity`)

*   Use absolute imports for external packages and relative imports (`from . import ...`) for internal module references.

### Typing
*   **Strict Typing:** All new code must be fully typed.
*   **Generics:** Use standard collection generics (e.g., `dict[str, Any]`, `list[int]`) available in Python 3.9+.
*   **Return Types:** Explicitly type return values, even for `None` (e.g., `-> None`).

### Naming
*   **Variables/Functions:** `snake_case`
*   **Classes:** `PascalCase`
*   **Constants:** `UPPER_CASE`
*   **Private Members:** Prefix with `_` (e.g., `_attr_unique_id`).

### Error Handling
*   **Logging:** Use `_LOGGER = logging.getLogger(__name__)`.
*   **Exceptions:** Catch specific exceptions rather than bare `except:`.
*   **Async:** Ensure all I/O bound operations are `await`ed and run in the event loop.

## 3. Architecture & Patterns

*   **Platform:** This is a Home Assistant custom component. Adhere to [Home Assistant developer docs](https://developers.home-assistant.io/).
*   **Library:** The integration relies on the `pyhon` library for API communication.
*   **Entities:** Most entities inherit from `HonEntity`.
*   **Data Updates:** Uses `DataUpdateCoordinator` (`HonDataUpdateCoordinator`) for efficient polling.
*   **Configuration:** Uses `config_flow` for setup.

## 4. Specific Rules

*   **Translations:** Ensure all user-facing strings use translation keys defined in `translations/en.json`.
*   **Manifest:** Update `manifest.json` if dependencies or version changes.
*   **Const:** Define constants in `const.py` to avoid magic strings.
