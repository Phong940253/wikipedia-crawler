#!/bin/bash
myArray=("https://vi.wikipedia.org/wiki/Ng%C6%B0%E1%BB%9Di")

for str in ${myArray[@]}; do
    python wikipedia-crawler.py $str --articles=1 --output=people.txt
done