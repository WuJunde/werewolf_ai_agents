<p align="center">
<img width="180" height="180" style="vertical-align:middle" src="https://github.com/WuJunde/werewolf_ai_agents/blob/main/werewolf_logo.png" />
</p>
<h1 align="center">
<span><i>Werewolf-Agents</i></span>
</h1>

<h3 align="center">
Train Agents to Play Werewolf
</h3>

<p align="center">
    <a href="https://discord.gg/DN4rvk95CC">
        <img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=flat&logoColor=white"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=GPL&color=white&style=flat" alt="License"/>
</p>

Here is a werewolf game played by large-language-model (LLM) based agents. You can use it to analyze LLM behavior in strategic games, train LLM agents to play the game better, or simply enjoy the game with the agents. The project is built upon [MetaGPT](https://github.com/geekan/MetaGPT).


## News
 - [TOP] Join in our [Discord](https://discord.gg/DN4rvk95CC) to ask questions and discuss with others.

## How to play:
## Install

### Pip installation

> Ensure that Python 3.9+ is installed on your system. You can check this by using: `python --version`.  
> You can use conda like this: `conda create -n metagpt python=3.9 && conda activate metagpt`

```bash
pip install metagpt
metagpt --init-config  # it will create ~/.metagpt/config2.yaml, just modify it to your needs
```

### Configuration

You can configure `~/.metagpt/config2.yaml` according to the [example](https://github.com/geekan/MetaGPT/blob/main/config/config2.example.yaml) and [doc](https://docs.deepwisdom.ai/main/en/guide/get_started/configuration.html):

```yaml
llm:
  api_type: "openai"  # or azure / ollama / open_llm etc. Check LLMType for more options
  model: "gpt-4-turbo-preview"  # or gpt-3.5-turbo-1106 / gpt-4-1106-preview
  base_url: "https://api.openai.com/v1"  # or forward url / other llm url
  api_key: "YOUR_API_KEY"
```

### Usage

After installation, you can run the game by:

```bash
python examples/werewolf_game/start_game.py
```

if you meet the error say your API is invalid. Please run ```metagpt --init-config``` again.

