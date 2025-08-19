# Merged data

Merged data contains processed log files from two separate data source directories. It is a combination merge for each of the nodes within the two source directories (one legitimate and one malicious).


## format

Each experiment contains several nodes, and each node contains different logs. The merger do every possible node combinations between the two experiments to generate the merged data.

```
merged/
└── <legit_activity>_<mal_activity>/
    └── <run_number>/
        ├── <legit_machine_1>_<mal_machine_A>/
        │   ├── cpu-load-data.txt
        │   ├── file-data.txt
        │   ├── network-data.txt
        │   ├── proc-cpu-data.txt
        │   ├── proc-mem-data.txt
        │   ├── proc-new-data.txt
        │   └── malicious_time.txt
        ├── <legit_machine_1>_<mal_machine_B>/
        │   ├── cpu-load-data.txt
        │   ├── file-data.txt
        │   ├── network-data.txt
        │   ├── proc-cpu-data.txt
        │   ├── proc-mem-data.txt
        │   ├── proc-new-data.txt
        │   └── malicious_time.txt
        ├── <legit_machine_2>_<mal_machine_A>/
        │   ├── cpu-load-data.txt
        │   ├── file-data.txt
        │   ├── network-data.txt
        │   ├── proc-cpu-data.txt
        │   ├── proc-mem-data.txt
        │   ├── proc-new-data.txt
        │   └── malicious_time.txt
        └── <legit_machine_2>_<mal_machine_B>/
            ├── cpu-load-data.txt
            ├── file-data.txt
            ├── network-data.txt
            ├── proc-cpu-data.txt
            ├── proc-mem-data.txt
            ├── proc-new-data.txt
            └── malicious_time.txt
```
Where `<legit_activity>` and `<mal_activity>` are legitimate and malicious experiments perfromed.

`malicious_time.txt`: this file specifically denotes the timeframe (start and end time) that the `<mal_activity>` is inserted.

Refer to [STEELISI/discern_collection/merger](https://github.com/STEELISI/discern_collection/tree/main/merger) for ther merger's source code.