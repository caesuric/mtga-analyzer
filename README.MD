# MTGA Analyzer

Allows you to plug in your MTGA winrate and current rank and find out how many games on average it will take to get to the next rank (bronze, silver, gold, diamond, platinum, mythic).

## Quickstart

1. Acquire Python - https://www.python.org/downloads/
2. Run `git clone https://github.com/caesuric/mtga-analyzer.git`
3. Navigate to the repo directory and run 'python analyze.py --help' to see options!

## Command Line Options

```
usage: analyze.py [-h] [--winrate WINRATE]
                  [--rank {bronze,silver,gold,platinum,diamond}] [--tier TIER]
                  [--subtier SUBTIER] [--runs RUNS]

Analyze games to rank up to the next rank in MTGA based on winrate.

optional arguments:
  -h, --help            show this help message and exit
  --winrate WINRATE     Your winrate at the current rank.
  --rank {bronze,silver,gold,platinum,diamond}
                        Current rank
  --tier TIER           Your tier at the current rank.
  --subtier SUBTIER     Your "blocks" on the meter at the current tier.
  --runs RUNS           Sim runs to execute. Increases execution time and
                        accuracy.
```