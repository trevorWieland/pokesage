# Welcome to the Pokesage Docs!

This site contains the project documentation for the `pokesage` project, whose goal is to make developing and training pokemon playing AI *fast*, *easy*, and *powerful*.

The project is built on top of its partner project, [`poketypes`](https://trevorwieland.github.io/poketypes/). `poketypes` is what provides consistency for our category labeling when serializing the battle state, which allows us to do cool things:
* Train one model for all generations
* Offload tedious label encoding
* Ensuring model cross-compatibility
* So much more

Just like `poketypes`, `pokesage` is also built with full type-hinting support, which means that whether you are building a bot that follows traditional branching logic, or a fully machine learning based approach, you don't have to worry about the data pipeline at all.

## Basic Architecture
This package contains fully-typehinted, modern classes for the following purposes:

- [`connectors`](reference/connectors.md): Handlers for the game-communication layer
- [`processors`](reference/processors.md): Handlers for turning game-messages into the Battle State
- [`sages`](reference/sages.md): Handlers for turning game-choices into game-actions (The actual AI part)
- [`battle`](reference/battle.md): pydantic Base Models for storing game state and possible game-choices.

Depending on how you want to use the library, you might need to subclass one or more of the classes referenced in the sections above. For more details about how each component works together, check out the [project flow](project-flow.md) page!

You can get started on this process by following the installation instructions [here](getting-started.md), or by jumping into learning-by-doing and following some of the guides in the [guides section](guides/basics.md).
