# Repository Guidelines

## Project Structure & Module Organization

This repository is currently an initial scaffold: no application code, tests, assets, or build configuration have been committed. Keep this guide current as the project develops.

When introducing the application, group source code by responsibility. Prefer clear top-level directories such as `src/` for implementation, `tests/` for automated tests, `assets/` for static resources, and `docs/` for supporting documentation. Adopt framework-specific layouts when appropriate and document the chosen structure.

## Build, Test, and Development Commands

No build system, dependency manager, or development commands are configured yet. The first implementation should include a `README.md` with exact setup, build, run, and test commands, including required tool versions. Provide repeatable commands that work from the repository root; update this guide when they become available.

## Coding Style & Naming Conventions

Follow the conventions of the selected language and framework. Use consistent indentation within each file, descriptive identifiers, and filenames that reflect their purpose. Keep modules focused and avoid unrelated changes.

When tooling is introduced, commit formatter and linter configuration and document how to run both.

## Testing Guidelines

No test framework or coverage threshold is configured. Add automated tests alongside new behavior and regression tests for bug fixes. Use descriptive test names that identify the behavior and expected outcome. Keep tests deterministic and document their execution command.

## Commit & Pull Request Guidelines

There is no commit history establishing a message convention. Use concise, imperative subjects, such as `Add game initialization`, and keep each commit focused.

Pull requests should explain the change, link relevant issues, and describe validation performed. Include screenshots for visual changes and identify any setup or configuration changes. Explicitly state when tests could not be run.
